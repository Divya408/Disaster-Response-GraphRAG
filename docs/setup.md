# Setup Guide

See the main `README.md` for the fastest path to running the project. This
document covers additional detail on each optional component.

## 1. Python Environment (Windows)

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks the activation script, run PowerShell as Administrator
once and execute:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 2. Python Environment (macOS / Linux)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Node / Frontend Setup

Requires Node.js 18+ and npm.

```bash
cd frontend
npm install
cp .env.example .env   # adjust VITE_API_BASE_URL if your backend isn't on localhost:8000
npm run dev
```

## 4. Environment Variables

```bash
cd backend
cp ../.env.example .env
```

Edit `backend/.env` as needed. In `DEMO_MODE=true` (the default), you do not
need to set anything else — the app seeds its own demo data, uses the
in-memory graph and TF-IDF retrieval fallback, and uses deterministic Demo
Mode LLM answers.

## 5. Neo4j (Optional)

The project runs fine without Neo4j (it falls back to an in-memory graph).
To use real Neo4j:

1. Install [Neo4j Desktop](https://neo4j.com/download/) or run via Docker:
   ```bash
   docker run -p7474:7474 -p7687:7687 -e NEO4J_AUTH=neo4j/your_password neo4j:5
   ```
2. Set in `backend/.env`:
   ```env
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your_password
   ```
3. Restart the backend. The startup log will show `Graph backend: Neo4j`
   instead of `in-memory (networkx fallback)`; also visible via
   `GET /api/health`.

## 6. LLM (Optional)

The project runs fine without a live LLM (Demo Mode answers are used
instead, always clearly labeled). To connect a real, OpenAI-compatible LLM:

```env
DEMO_MODE=false
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1
```

Any OpenAI-compatible provider (Azure OpenAI proxy, local vLLM/Ollama
OpenAI-compatible server, etc.) can be used by changing `LLM_BASE_URL`.

## 7. ChromaDB / sentence-transformers (Optional)

If `chromadb` and a working embedding backend are installed, the vector
store automatically uses them; otherwise it falls back to a scikit-learn
TF-IDF index, which requires no downloads. No configuration is needed
either way beyond `CHROMA_PATH` in `.env` if you want to change where the
Chroma files are stored.

## 8. Running the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

- API root: http://localhost:8000/
- Interactive API docs (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

On startup in Demo Mode, the backend automatically seeds the SQLite
database, builds the knowledge graph from `backend/data/demo/` +
`backend/data/documents/`, and builds the hybrid vector/BM25 index — no
manual steps are required before you can start querying.

## 9. Running the Frontend

```bash
cd frontend
npm run dev
```

Open http://localhost:5173.

## 10. Loading New Documents

Use the **Documents** page in the UI (upload → then click "Rebuild Vector
Index" and "Rebuild Knowledge Graph"), or via API:

```bash
curl -X POST http://localhost:8000/api/documents/upload -F "file=@mydoc.pdf"
curl -X POST http://localhost:8000/api/documents/index
curl -X POST http://localhost:8000/api/graph/build
```

Or via scripts:

```bash
python scripts/build_graph.py
python scripts/build_vector_index.py
```

## 11. Running Tests

```bash
cd backend
pytest -v
```

Note: `tests/test_api.py` requires `fastapi`/`httpx` to be installed (they
are in `requirements.txt`); all other test modules only require the core
scientific-Python stack and run independently of FastAPI.

## 12. Running the Evaluation Script

```bash
cd backend
python ../scripts/evaluate.py
```

## 13. Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'app'` | Run commands from inside `backend/`, or set `PYTHONPATH=backend` |
| Frontend shows "Could not reach the backend API" | Make sure `uvicorn app.main:app --reload` is running and `frontend/.env`'s `VITE_API_BASE_URL` matches its address |
| Neo4j not connecting | The app automatically falls back to the in-memory graph; check `GET /api/health` → `graph_backend` |
| PDF upload fails silently | Check `MAX_UPLOAD_SIZE_MB` in `.env` and confirm the file extension is one of `.pdf .docx .txt .md .csv` |
| CORS errors in the browser console | Add your frontend origin to `CORS_ORIGINS` in `backend/.env` |
