# Textmate

A small Flask app: pick whether you're male or female, name your partner,
and chat with an AI that stays in character as them. Built with LangChain
(`langchain-google-genai` + `RunnableWithMessageHistory`) on top of Gemini.

## Run locally

```bash
cd partner-chatbot
python -m venv venv
source venv/bin/activate     
pip install -r requirements.txt

cp .env.example .env

python app.py
```

Open http://localhost:5000

## Architecture

### Request flow

1. **Setup (`/`)** — User selects a gender and enters a partner name.
2. **Session init (`/start`)** — Server builds a LangChain chain for this user and stores it in memory, keyed to their Flask session cookie.
3. **Chat (`/chat`)** — Each message is sent through that session's chain; history is tracked automatically so context carries across turns.
4. **Reset (`/reset`)** — Clears the session's chain and history to start fresh.

### Routes

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Setup screen — collect gender + partner name |
| `/start` | POST | Initialize a new chat session and its LangChain chain |
| `/chat` | POST | Send a message, get a reply, history auto-updates |
| `/reset` | POST | Clear the current session |

### How the chain is built (`/start`)

- A `ChatPromptTemplate` is assembled from:
  - a **system instruction** (defines the AI's persona based on gender + partner name)
  - a **message history placeholder** (inserts prior turns)
  - the **human input** (the new message)
- This prompt is piped into `ChatGoogleGenerativeAI` (Gemini).
- The result is wrapped in `RunnableWithMessageHistory`, which ties the chain to an `InMemoryChatMessageHistory` instance.
- The chain + history are stored server-side in a dict, keyed by the browser's Flask session id — so each user gets an isolated, persistent conversation.

### How a message is handled (`/chat`)

1. Look up the chain for the current session id.
2. Invoke the chain with the new user message.
3. `RunnableWithMessageHistory` automatically appends both the user message and the AI reply to that session's history.
4. Return the reply — next call automatically has full prior context.

### Session storage

- **In-memory only** (a Python dict) — no database.
- Sessions are lost on server restart.
- Each session is isolated by Flask's session cookie, so concurrent users don't share chains or history.