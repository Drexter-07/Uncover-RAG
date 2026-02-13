@echo off
start cmd /k "cd backend && call venv\Scripts\activate && title Backend && uvicorn main:app --reload"
timeout /t 5
start cmd /k "cd frontend && title Frontend && npm run dev"
echo Application started.

echo Backend running on http://localhost:8000
echo Frontend running on http://localhost:5173
echo Please ensure your OPENAI_API_KEY is set in backend/.env
pause
