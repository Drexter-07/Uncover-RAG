# Uncover - AI-Powered Skincare & Hair Restoration

Uncover is a full-stack application that provides personalized skincare and hair treatment recommendations. It leverages a specific clinical knowledge base and generic AI capabilities to offer professional advice tailored to user concerns.

## 🚀 Features

-   **AI-Powered Recommendations**: Uses OpenAI's GPT models to analyze user queries.
-   **RAG Architecture**: Retrieval-Augmented Generation ensures answers are grounded in Uncover's specific treatment offerings (`treatments.json`).
-   **Vector Search**: Utilizes ChromaDB for semantic search to find relevant treatments.
-   **Modern UI**: A responsive, aesthetically pleasing interface built with React and Tailwind CSS.
-   **Interactive Experience**: animated UI elements and instant feedback loops.

## 🛠️ Tech Stack

### Frontend
-   **React**: UI Library
-   **Vite**: Build tool
-   **Tailwind CSS**: Styling
-   **Framer Motion**: Animations
-   **Lucide React**: Icons

### Backend
-   **FastAPI**: Web framework
-   **LangChain**: Framework for LLM applications
-   **ChromaDB**: Vector Database
-   **OpenAI API**: Embeddings and Chat Completion

## 📋 Prerequisites

-   **Node.js** (v18 or higher)
-   **Python** (v3.10 or higher)
-   **OpenAI API Key**

## ⚡ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd uncover
```

### 2. Backend Setup
Navigate to the backend directory and set up the Python environment.

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
# source venv/bin/activate

pip install -r requirements.txt
```

**Environment Variables:**
Create a `.env` file in the `backend` folder and add your OpenAI API Key:
```env
OPENAI_API_KEY=sk-your_api_key_here
```

**Prepare Data:**
Ensure `treatments.json` is present in the `backend` directory. If starting fresh, you might need to run the scraper (if available) or ensure the JSON file is populated.

**Run the Backend:**
```bash
python main.py
```
The server will start at `http://localhost:8000`.

### 3. Frontend Setup
Open a new terminal and navigate to the frontend directory.

```bash
cd frontend
npm install
```

**Run the Frontend:**
```bash
npm run dev
```
The application will operate at `http://localhost:5173`.

## 📖 Usage

1.  Ensure both backend and frontend servers are running.
2.  Open your browser to `http://localhost:5173`.
3.  In the search bar, type your skin or hair concern (e.g., "I have acne scars" or "treatment for hair loss").
4.  The AI will analyze your query, search the internal database for matching treatments, and present a recommendation card along with a personalized message.

## 📂 Project Structure

```
uncover/
├── backend/
│   ├── chroma_db/          # Vector database storage
│   ├── main.py             # FastAPI application & RAG logic
│   ├── treatments.json     # Knowledge base
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.jsx         # Main frontend logic
│   │   └── main.jsx        # Entry point
│   ├── tailwind.config.js  # Styling configuration
│   └── vite.config.js      # Build configuration
└── README.md
```
