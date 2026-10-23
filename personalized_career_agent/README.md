# Personalized Career Recommendation Agent

A starter full-stack project: Streamlit frontend, FastAPI backend, SQLAlchemy database layer, MySQL support, scikit-learn TF-IDF/cosine similarity, skill-gap analysis, learning roadmap, and a baseline NLP-style career assistant.

## Setup (Windows)
1. Install Python 3.11+ and VS Code.
2. Extract this ZIP and open the project folder in VS Code.
3. In the terminal:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env`. SQLite is configured by default for easy first run.
5. Start the backend:
   ```powershell
   uvicorn backend.main:app --reload
   ```
6. In a second terminal, activate `.venv` and run:
   ```powershell
   streamlit run frontend/app.py
   ```
7. Visit `http://127.0.0.1:8000/docs` for the API and the Streamlit URL printed in the terminal for the dashboard.

## Use MySQL
Create a database called `career_agent`, then set `.env`:
`DATABASE_URL=mysql+pymysql://career_user:YOUR_PASSWORD@localhost:3306/career_agent`

Create a user and grant privileges in MySQL:
```sql
CREATE DATABASE career_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'career_user'@'localhost' IDENTIFIED BY 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON career_agent.* TO 'career_user'@'localhost';
FLUSH PRIVILEGES;
```

## Concepts for your report
- **RAD (Rapid Application Development):** build the application iteratively, collect feedback, and improve modules in short cycles.
- **Machine Learning:** TF-IDF and cosine similarity rank career descriptions against the student's skills, interests, and goals.
- **NLP:** text normalization and similarity-based matching support the baseline assistant and profile-to-career matching. The current assistant is a rule-based prototype, not a generative LLM.
- **Full stack:** Streamlit UI → FastAPI REST endpoints → SQLAlchemy → SQLite/MySQL.

## Limitations and next steps
- The match score is a text similarity score, not a probability of employment.
- This prototype has no authentication. Do not deploy with real personal data until secure authentication, access controls, validation, privacy notices, and deletion are added.
- Improve the assistant with spaCy, sentence-transformers, or an LLM API after reviewing privacy, costs, and hallucination risks.
- Add tests, deployment configuration, and a custom HTML/CSS/JavaScript frontend if required by your rubric.
