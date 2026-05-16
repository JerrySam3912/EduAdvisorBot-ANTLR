# 🎓 EduAdvisorBot: Course Registration Assistant

A natural language chatbot that helps students answer course-related questions — eligibility, prerequisites, registration deadlines, and more — powered by ANTLR4 grammar-based parsing.

![Python](https://img.shields.io/badge/Made%20With-Python-3670A0?style=flat&logo=python&logoColor=white)
![ANTLR4](https://img.shields.io/badge/Powered%20By-ANTLR4-red)
![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)

---

## 📽 Demo

👉 [Click here to watch the demo video](https://youtu.be/RpvjOIwHuFs?si=AUodA7mQa3roGMER)

The video walks through:
- Asking about course eligibility in Vietnamese
- Querying course prerequisites and requirements
- Checking registration deadlines and platforms
- Session-aware conversation with student ID recognition

---

## 📌 Introduction

**EduAdvisorBot** is a smart assistant for students to:
- Check course eligibility based on completed prerequisites
- Query curriculum structure and course requirements
- Find out registration deadlines and platforms
- Get answers in Vietnamese

Built with **Python**, **FastAPI**, and **ANTLR4**, EduAdvisorBot uses grammar-driven intent parsing for reliable, deterministic understanding of natural language queries — no LLM required.

---

## ✨ Features

- 🗨 **Natural Language Chatbot** for course-related queries
- 🌍 **Vietnamese Support** — Vietnamese input with language validation
- 🧬 **ANTLR4 Grammar Parsing** with visitor-based slot extraction
- 🔁 **Regex Fallback Classifier** for patterns outside the grammar
- 🎓 **Curriculum Data Lookup** via structured curriculum JSON
- 📢 **Edusoft Notice Integration** for registration announcements
- 💬 **Session Memory** — retains student ID and conversation context
- 🚀 **FastAPI REST Backend** — ready for React frontend integration
- 🧪 **Comprehensive Test Suite** — grammar, NLP pipeline, and session memory tests

---

## ⚙ Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-username/EduAdvisorBot-ANTLR.git
cd EduAdvisorBot-ANTLR
```

### 2. Create Python Virtual Environment

```bash
python -m venv apps/backend-api/.venv
# Windows:
apps/backend-api/.venv/Scripts/Activate.ps1
# macOS/Linux:
source apps/backend-api/.venv/bin/activate
```

### 3. Install Dependencies

```bash
cd apps/backend-api
pip install -r requirements.txt
```

### 4. Generate ANTLR Parser Files

```bash
cd apps/backend-api
antlr4 -Dlanguage=Python3 -o app/generated app/grammar/CourseQuery.g4
```

### 5. Run the Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. API docs are at `http://localhost:8000/docs`.

### 6. Run the Frontend

```bash
cd apps/edu-chatbot-fe
pnpm install
pnpm dev
or
npm install
npm dev
```

The frontend will be available at `http://localhost:5173`. It connects to the backend at `http://localhost:8000`.

---

## 🚀 Usage

Send a POST request to the `/api/v1/chat` endpoint:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "ITCSIU22001 có được đăng ký môn CS101 không?", "session_id": "user-123"}'
```

**Example queries:**

- *Vietnamese*: `ITCSIU22001 có được đăng ký IT069IU không?`
- *Prerequisites*: `OOP có những môn tiên quyết gì?`
- *Registration time*: `Khi nào được đăng ký học kỳ tới?`

---

## 🛠 Configuration / Customization

- **Grammar Rules**: Modify `app/grammar/CourseQuery.g4` and regenerate the parser.
- **Curriculum Data**: Update `curriculum.json` via the build script in `scripts/build_curriculum_json.py`.
- **Intents**: Adjust intent definitions in `app/nlp/intents.py`.
- **Session Memory**: Configure TTL and storage in `app/services/session_memory_service.py`.

---

## 🧱 Project Structure

```text
EduAdvisorBot-ANTLR/
├── apps/
│   ├── backend-api/         # FastAPI backend
│   │   ├── api/v1/endpoints/ # FastAPI route handlers
│   │   ├── core/             # App configuration
│   │   ├── grammar/          # ANTLR grammar (.g4)
│   │   ├── generated/        # ANTLR-generated Python files
│   │   ├── nlp/              # Parser, visitor, language detection, intents
│   │   ├── repositories/     # Academic data access
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── services/         # Business logic (chat, curriculum, session)
│   │   └── tests/            # Test suite
│   └── edu-chatbot-fe/       # React + Vite frontend
│       └── src/              # React components
├── scripts/                  # Curriculum data build scripts
└── docs/                    # Documentation

> 🔄 Grammar → Parser → Visitor → Processor → Service → Response

---

## 🧠 Prompt Engineering Principles Applied

This project applies grammar-driven semantic parsing instead of LLM-based prompting:

- **Deterministic Parsing**: ANTLR grammar defines exact syntactic patterns with no ambiguity.
- **Slot Extraction**: `IntentSlotExtractor` visitor pulls intent, course code, and semester from the parse tree.
- **Language**: Vietnamese with detected language flag in the response.
- **Graceful Fallback**: Regex classifier handles inputs that fall outside the grammar.
- **Session Context**: Conversation memory preserves student ID and last topic across turns.

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

---

## 🙌 Credits

* Developed by:
  * Hoàng Xuân Dũng (ITITWE22009) — Team learder, Backend NLP pipeline & system integration
  * Nguyễn Hồng Ngọc Hân (ITCSIU22229) - Frontend developer, integration with the backend and perform system testing
  * Nguyễn Nhật Nam (ITITWE22149) — Data collection & processing
  * Đặng Nguyễn Nhật Vy (ITITDK22102) — Data refinement & chatbot testing

* Advisor: Ph.D. Lê Thị Ngọc Hạnh

* Supported by: International University – Vietnam National University, HCMC

**Tech Stack**:

- 🐍 Python 3.12
- 🧬 ANTLR4
- 🚀 FastAPI
- 📄 Pydantic
- ⚛ React 19 + Vite
- 🧠 NLP Grammar + Parsing

---

> "Your course registration questions — answered instantly, in Vietnamese language❤️."
