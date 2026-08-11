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

python app.py
```

Open http://localhost:5000

## Architecture

### Request flow

1. **Session init (`/start`)** — Server builds a LangChain chain with a strict DSA-only system prompt and stores it in memory, keyed to the user's Flask session.
2. **Chat (`/chat`)** — Each message is sent through the chain; if it's off-topic, the system prompt steers the model into roasting the user back to DSA. History carries across turns automatically.
3. **Reset (`/reset`)** — Clears the session's chain and history.

### Routes

| Route | Method | Purpose |
|---|---|---|
| `/start` | POST | Initialize a new session and its LangChain chain |
| `/chat` | POST | Send a message, get a reply, history auto-updates |
| `/reset` | POST | Clear the current session |

### How the chain is built (`/start`)

- A `ChatPromptTemplate` combines:
  - a **system instruction** — enforces the DSA-only persona and roast behavior on off-topic input
  - a **message history placeholder** — inserts prior turns for context
  - the **human input** — the new message
- Piped into `ChatGoogleGenerativeAI` (Gemini).
- Wrapped in `RunnableWithMessageHistory`, tied to an `InMemoryChatMessageHistory` instance.
- Chain + history are stored server-side in a dict, keyed by the Flask session id, so each user's conversation stays isolated.

### How a message is handled (`/chat`)

1. Look up the chain for the current session id.
2. Invoke it with the new message.
3. `RunnableWithMessageHistory` auto-appends both the user message and the reply to session history.
4. Return the reply — next call has full prior context, including whether the user's been on-topic or not.

### Session storage

- **In-memory only** (a Python dict) — no database.
- Sessions are lost on server restart.
- Each session isolated via Flask's session cookie.