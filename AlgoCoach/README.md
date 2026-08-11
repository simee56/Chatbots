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


