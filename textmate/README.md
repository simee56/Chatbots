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

