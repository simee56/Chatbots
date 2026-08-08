# AlgoCoach

A fun learning project: a blunt, roast-you-if-you-go-off-topic DSA
instructor bot. Ask it about arrays, trees, graphs, DP, whatever — it'll
teach you properly. Try small talk and it'll roast you back to the topic.
Built with Flask + LangChain (`langchain-google-genai` +
`RunnableWithMessageHistory`) on top of Gemini.

## Run locally

```bash
python -m venv venv
venv\Scripts\Activate.ps1     
pip install -r requirements.txt

cp .env.example .env
# paste your real Gemini API key into .env

python app.py
```

Open http://localhost:5000

## How it works

- `/start` builds a LangChain chain with a strict DSA-only system prompt
- `/chat` sends your message through it and returns the reply
- `/reset` clears the session

Chat history lives in memory on the server, so it resets on restart.
Fine for a solo project.

## Deploying

Push to GitHub, deploy on Render (or Railway/Fly.io) with:
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app --timeout 60`
- Env vars: `GOOGLE_GEMINI_KEY`, `FLASK_SECRET_KEY`