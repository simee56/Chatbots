# Partner Chat

A small Flask app: pick whether you're male or female, name your partner,
and chat with an AI that stays in character as them. Built with LangChain
(`langchain-google-genai` + `RunnableWithMessageHistory`) on top of Gemini.

## Run locally

```bash
cd partner-chatbot
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and paste your real Gemini API key

python app.py
```

Open http://localhost:5000

## How it works

- `/` — setup screen (gender + partner name)
- `/start` — builds a LangChain `RunnableWithMessageHistory` chain server-side:
  a `ChatPromptTemplate` (system instruction + message history placeholder +
  human input) piped into `ChatGoogleGenerativeAI`. The chain + its message
  history are stored in memory keyed by a per-browser session id (Flask
  session cookie).
- `/chat` — invokes that session's chain with your new message; LangChain's
  `InMemoryChatMessageHistory` automatically appends both your message and
  the reply, so conversation context carries forward on the next call.
- `/reset` — clears the session so you can start over.

Only a session id lives in the cookie — the actual chain and its message
history live in Python dicts on the server (`chat_chains`,
`message_histories`), which means:
- It resets if the server restarts.
- It won't work correctly if you deploy with multiple worker
  processes/instances (each worker has its own memory). Fine for
  personal use; swap in Redis or a DB if you want it more robust.

## Deploying

Any host that runs a Python web app works (Render, Railway, Fly.io,
a VPS, etc.). General steps:

1. Push this folder to a GitHub repo (don't commit `.env`).
2. On the host, set these environment variables in its dashboard:
   - `GOOGLE_GEMINI_KEY`
   - `FLASK_SECRET_KEY` (any random string)
3. Set the start command to something like:
   ```
   gunicorn app:app
   ```
4. **Important:** if your host runs more than one worker process,
   the in-memory `chat_sessions` dict won't be shared between them and
   users may randomly lose their chat. For single-worker/personal
   deployments this isn't an issue.
