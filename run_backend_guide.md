# Chạy Backend (BE)

Backend của dự án là một FastAPI app nằm ở `backend-api`.

---

## 1. Vào thư mục backend

```bash
cd d:\ppl\projectPpl\EduAdvisorBot-ANTLR\apps\backend-api
```

---

## 2. Kích hoạt virtual environment

Nếu bạn dùng virtualenv đã có sẵn:

```powershell
.\.venv\Scripts\Activate.ps1
```

Nếu chưa có, tạo rồi kích hoạt:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

---

## 3. Cài dependency

```bash
pip install -r requirements.txt
```

---

## 4. Chạy server

```bash
uvicorn app.main:app --reload --port 8000
```
