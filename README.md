# Lumina AI Personalized Learning Tutor

A React and FastAPI learning application with NVIDIA models, document RAG, persistent memory, real MCP tools and an interactive Three.js robot.

[Repository](https://github.com/milyaskhan-2127/Lumina-AI----Personalized-Learning-Tutor) · [Word report](docs/report/Lumina_AI_Project_Report.docx)

## Run on Windows

Requires Python 3.12+, Node.js 20.19+ or 22.12+, and NVIDIA API access.

1. Run `setup.cmd` to install dependencies.
2. Copy `.env.example` to `.env` and enter your `NVIDIA_API_KEY`. Alternatively create `API.txt` containing the key.
3. Run `start.cmd` and open http://localhost:5173. The backend runs at http://localhost:8000.

The submission contains application source, required assets, dependency manifests, launchers and the Word report. Installations, credentials, uploaded documents and local learning data are not included. The application creates `backend/data/` when first started.

## Features and architecture

- Personalized streaming tutor with saved conversations, learning preferences and language settings.
- PDF, DOCX, PPTX and TXT ingestion, semantic retrieval and source references.
- MCP-generated quizzes, grading, persistent progress and learning analytics.
- Interactive 3D robot with whole-viewport cursor tracking, task animations and quiz celebrations.
- Floating companion, document lessons, focus timer and optional browser speech controls.

React communicates with FastAPI through the Vite `/api` proxy. LangGraph loads student context and chooses a response, ChromaDB retrieval or a real stdio MCP tool. NVIDIA provides chat and embeddings. SQLite stores preferences, conversations, scores and completed focus sessions. Backend events control the robot's visible state.

This is a local single-student application. Extracted text and relevant learning context are sent to NVIDIA. Browser voice support varies. OCR and public multi-user authentication are not implemented.
