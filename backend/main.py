import json
import os 
import scraper  
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration
TREATMENTS_FILE = "treatments.json"
CHROMA_PATH = "chroma_db"

# Global variables
vectorstore = None
retriever = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    global vectorstore, retriever

    if not os.path.exists(TREATMENTS_FILE):
        print(f"⚠️ {TREATMENTS_FILE} not found. Triggering auto-scraper...")
        try:
            scraper.crawl_and_extract() # This runs your scraper.py
            print("✅ Scraping complete. File created.")
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
    else:
        print(f"📂 Found {TREATMENTS_FILE}. Skipping scrape.")
    
    print("Loading treatments...")
    try:
        with open(TREATMENTS_FILE, "r", encoding="utf-8") as f:
            treatments_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {TREATMENTS_FILE} not found. Ensure you ran the scraper.")
        treatments_data = []

    # Prepare documents for VectorStore
    documents = []
    for item in treatments_data:
        # Robustly get content. If 'page_content' exists (new format), use it.
        # If not, fall back to constructing it from fields (old format).
        content = item.get("page_content")
        if not content:
            # Fallback construction
            t = item.get("treatment", "Unknown")
            c = item.get("concern", "")
            b = item.get("benefit", "")
            content = f"Treatment: {t}\nConcern: {c}\nBenefit: {b}"

        # Clean metadata (remove large text fields to save memory)
        metadata = item.copy()
        if "page_content" in metadata:
            del metadata["page_content"]
        if "description" in metadata: # Optional cleanup
            del metadata["description"]
            
        documents.append(Document(page_content=content, metadata=metadata))

    if not documents:
        print("⚠️ No content to index.")
    else:
        # Initialize VectorStore
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        try:
            # Optional: Clear existing collection if needed
            # vectorstore.delete_collection()
            pass
        except:
            pass

        vectorstore = Chroma.from_documents(
            documents=documents, 
            embedding=embeddings,
            collection_name="treatments_collection",
            persist_directory=CHROMA_PATH
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        print(f"✅ Indexed {len(documents)} documents.")

    yield
    # Shutdown logic
    print("Shutting down...")

app = FastAPI(title="Wellness Recommendation API", lifespan=lifespan)

# CORS Config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class RecommendationRequest(BaseModel):
    query: str

class TreatmentResponse(BaseModel):
    treatment: Optional[str] = None
    concern: Optional[str] = None
    benefit: Optional[str] = None
    technology: Optional[str] = None

class RecommendationResponse(BaseModel):
    recommendation_text: str
    related_treatments: List[TreatmentResponse]

# --- Helper to format docs for the chain ---
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# --- The Recommendation Endpoint ---
@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_treatment(request: RecommendationRequest):
    if not retriever:
        raise HTTPException(status_code=500, detail="System not initialized properly.")

    # 1. Define the Parser (Forces JSON output)
    parser = JsonOutputParser()

    # 2. Define the Prompt
    template = """You are a Senior Dermatologist at Uncover Clinics.
    Your goal is to recommend a treatment based on the context and formatted strictly as JSON.

    ### CONTEXT FROM KNOWLEDGE BASE:
    {context}

    ### USER CONCERN:
    {question}

    ### INSTRUCTIONS:
    1. **Analyze:** Look at the user's concern and find the best treatment in the context.
    2. **Off-Topic Check:** If the user's question is **NOT** related to skincare or haircare or the context provided (e.g., "Capital of India", "Math questions"), you must return a polite refusal JSON.
    3. **Extract Details:** You MUST extract or infer the "Targeting" (what issues it fixes) and "Benefit" (the result) from the text.
    4. **Ignore Home Remedies:** If the context mentions home remedies (Aloe Vera, Lemon, etc.), ignore them. Focus ONLY on professional clinical treatments (Lasers, Facials, GFC).
    5. **Format:** Output ONLY a single valid JSON object. Do not include markdown formatting.
    
    **JSON Keys Required:**
    - "reply": A friendly, professional conversation response (max 3 sentences). If refusing, say you only handle skincare.
    - "treatment": The specific name of the treatment (e.g., "Hydrafacial Elite"). **Return null if off-topic.**
    - "targeting": A short string listing issues it treats (e.g., "Dullness, Dehydration"). **Return null if off-topic.**
    - "benefit": The main advantage (e.g., "Instant Glow, No Downtime"). **Return null if off-topic.**
    - "technology": The machine name if mentioned (e.g., "Alma Soprano"), else null.

    ### EXAMPLE OUTPUT (Success):
    {{
      "reply": "For dry skin, I highly recommend our Hydrafacial Elite. It deeply exfoliates and hydrates your skin, giving you an instant glow.",
      "treatment": "Hydrafacial Elite",
      "targeting": "Dry skin, Clogged Pores, Dullness",
      "benefit": "Deep Hydration & Instant Glow",
      "technology": "Vortex-Fusion"
    }}

    ### EXAMPLE OUTPUT (Refusal):
    {{
      "reply": "I apologize, but I can only answer questions related to Uncover Clinics' skin and hair treatments.",
      "treatment": null,
      "targeting": null,
      "benefit": null,
      "technology": null
    }}

    YOUR JSON RESPONSE:"""

    prompt = ChatPromptTemplate.from_template(template)
    model = ChatOpenAI(model="gpt-4.1-nano", temperature=0.4)

    # 3. Create the Chain
    chain = (
        {
            "context": retriever | format_docs, 
            "question": RunnablePassthrough()
        }
        | prompt
        | model
        | parser 
    )

    try:
        # 4. Run the Chain
        result = chain.invoke(request.query)

        # If treatment is None, it means the AI refused. We return empty list.
        if not result.get("treatment"):
             return RecommendationResponse(
                recommendation_text=result.get("reply", "I can only answer questions about Uncover Skincare."),
                related_treatments=[]
            )

        # Success Case
        # 5. Map JSON to Pydantic Response
        # The frontend needs a list for 'related_treatments', so we wrap the single result
        return RecommendationResponse(
            recommendation_text=result.get("reply", "I recommend booking a consultation."),
            related_treatments=[
                TreatmentResponse(
                    treatment=result.get("treatment", "Consultation"),
                    concern=result.get("targeting", "General Wellness"),
                    benefit=result.get("benefit", "Expert Care"),
                    technology=result.get("technology", None)
                )
            ]
        )

    except Exception as e:
        print(f"❌ Error processing request: {e}")
        # Fallback in case of JSON error or LLM hallucination
        return RecommendationResponse(
            recommendation_text="I'm having a little trouble finding the perfect match right now. I'd recommend booking a consultation with our experts to discuss your specific needs.",
            related_treatments=[]
        )

@app.get("/")
def read_root():
    return {"message": "Wellness API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)