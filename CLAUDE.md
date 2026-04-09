# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VinSchool One "Smart Hub" — hackathon prototype (AI20K, VinUni-VinSchool, April 2026). Adds an AI conversational layer to the VinSchool One parent app: conversational search, smart daily digest, and actionable notification summaries.

**Student in demo:** Nguyễn Hưng · Mã: VS108245 · Lớp 5B06 · Trường Tiểu học Vinschool Timescity T36

## Running the Project

**Frontend prototype only (no AI):**
```bash
python3 -m http.server 8080
# open http://localhost:8080/prototype.html
```

**Full stack (prototype + AI backend):**
```bash
# Terminal 1 — FastAPI backend (port 5050, NOT 8000)
source .venv/bin/activate
python server.py

# Terminal 2 — static file server for prototype
python3 -m http.server 8080
```

> `prototype.html` hardcodes `fetch('http://localhost:8000/chat')` — if the backend runs on 5050 (default in `server.py`), update the fetch URL in the prototype or change `server.py` port to 8000.

**Rebuild FAISS semantic index** (after editing `rag_data.json`):
```bash
python3 build_rag_index.py
```

**Run tests:**
```bash
python -m pytest test_vinschool_tools.py test_vinschool_agent.py -v
```

**Ingest new notifications into RAG data:**
```bash
python scripts/ingest_notifications.py
```

## Architecture

```
prototype.html  (single-file mobile UI, 19 screens)
    │  fetch POST /chat
    ▼
server.py       (FastAPI, CORS open, port 5050)
    │
    ▼
services/vinschool_agent.py  (VinschoolAgent class, Gemini function-calling)
    │  tool dispatch
    ▼
services/vinschool_tools.py  (VinschoolTools — reads rag_data.json)
    │  general_search only
    ▼
services/rag_service.py      (keyword BM25 fallback; FAISS+SentenceTransformer if faiss_index.bin exists)
    │
    └──► data/rag_data.json  (chunked JSON from xlsx mockdata)
```

### Agent Tool Map

Each tool in `vinschool_tools.py` reads a specific sheet from `rag_data.json`:

| Tool | Sheet key in rag_data.json |
|------|---------------------------|
| `get_student_profile` | `Student Information` |
| `get_attendance` | `Điểm danh` |
| `get_homework` | `Bài tập` |
| `get_menu` | `Thực đơn` |
| `get_tuition_info` | `Học phí` |
| `get_grades` | `Kết quả học tập` |
| `get_latest_comments` | `Nhận xét` |
| `get_notifications` | `Thông báo` |
| `get_contact_info` | `Teacher Information`, `Parent  Guardian Information` (double space!) |
| `general_search` | RAG across all chunks |

### Prototype UI Routing (`prototype.html`)

Navigation is driven by a JS router with three constructs:
- `MAIN[]` — screens that show the top app header
- `TAB_MAP{}` — maps tab names to their page IDs
- `goTo(id)` / `goBack()` / `switchTab(tab)` — navigation functions

AI-specific screens: `page-ai-search`, `page-ai-chat`, `page-ai-brief`.

The chat input calls `sendMsg()` → `fetch('/chat')` → renders markdown via `marked.js` → calls `renderAiChatFollowUp(userText, aiReplyText)` which generates contextual follow-up chips via `pickFollowUpQueries()`.

## Critical Constraints

- **No LLM generation for financial/grade numbers.** For tuition and scores, the agent must only route to the hard-coded UI screen — never summarize or paraphrase numeric values.
- **Student scoping.** All tool calls are implicitly scoped to VS108245 (Nguyễn Hưng). The system prompt must inject student ID + name so the model never calls a tool for the wrong student.
- **The `Parent  Guardian Information` sheet name has a double space** — match exactly when filtering by sheet.
- **Agent is a singleton** (`get_vinschool_agent()`). Chat history accumulates within a server session; restarting the server resets history.

## Environment

`.env` file (not committed):
```
GOOGLE_API_KEY=...
GOOGLE_CLOUD_PROJECT=our-audio-472409-e5
GOOGLE_CLOUD_LOCATION=global
```

The client uses `vertexai=False` (Google AI Studio API key), not Vertex AI service account auth.

Current model: `gemini-3-1-flash-lite` (set in `VinschoolAgent.__init__`).
