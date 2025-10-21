# ClauseEase AI - Contract Language Simplifier

Transform complex legal documents into plain English using AI.

An intelligent document processing system that automatically analyzes legal contracts and converts complex legal language into easy-to-understand plain English using advanced AI models.

---

## Features

- 📄 Multi-format support (PDF, DOCX, TXT)
- 🤖 AI-powered analysis using BART and Legal-BERT
- 📊 Visual charts and statistics
- 🔐 Secure JWT authentication
- ⚡ Real-time processing with progress tracking
- 📈 Readability metrics comparison
- 🎯 15 clause types detection
- 📚 Legal terms extraction and glossary

---

## Tech Stack

**Frontend:** HTML, CSS, JavaScript  
**Backend:** Python, Flask, JWT  
**AI Models:** BART, Legal-BERT, spaCy  
**Processing:** 5-stage pipeline for document analysis

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Setup Environment
```bash
# Copy environment template
cp .env.example .env
# Edit .env with your JWT_SECRET_KEY
```

### 3. Run Backend Server
```bash
# Start Flask API on port 5000
python src/main.py
```

### 4. Run Frontend Server
```bash
# In a new terminal, navigate to frontend folder
cd frontend
python -m http.server 8080
```

### 5. Access Application
Open browser and go to: **http://localhost:8080**

---

## Project Structure

```
├── frontend/           # Web interface
│   ├── auth/          # Login/Register pages
│   ├── landing/       # Upload interface
│   └── results/       # Results display
├── src/
│   ├── main.py        # Flask API
│   └── components/    # Processing modules
├── scripts/           # Utility scripts
├── .env.example       # Environment template
└── requirements.txt   # Dependencies
```

---

## API Endpoints

```
POST /api/register     - Create account
POST /api/login        - User login
POST /api/process      - Process document
```

---

## Supported Clause Types (15)

Confidentiality, Termination, Indemnity, Dispute Resolution, Governing Law, Payment Terms, Intellectual Property, Warranties, Liability, Force Majeure, Assignment, Non-Compete, Severability, Amendment, Notice

---

## Requirements

- Python 3.8+
- 4GB RAM (8GB recommended)
- Internet (first run for model download)

---

## License

For educational and research purposes.

---

**Made with ❤️ for simplifying legal documents**

