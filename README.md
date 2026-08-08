# Chatbots

A collection of small chatbot projects built to learn LLM API integration —
Gemini + LangChain + Flask.

## Projects

### [Textmate](./textmate) — [Live](https://chatbots-9v1s.onrender.com/)
Chat with your own AI partner. Pick your gender, name your partner, and
chat — the bot stays in character as a warm, affectionate partner.

### [AlgoCoach](./AlgoCoach) — [Live](https://chatbots-1-8ckg.onrender.com/)
A blunt, no-nonsense DSA instructor with a terminal-style UI. Ask it real
data structures & algorithms questions and it teaches properly. Try small
talk and it roasts you back to the topic.

## Stack

- **Flask** — backend + routing
- **LangChain** (`langchain-google-genai`, `RunnableWithMessageHistory`) —
  conversation memory
- **Gemini API** — the underlying model
- Deployed on **Render**

## Running any project locally

```bash
cd <project-folder>
python -m venv venv
venv\Scripts\Activate.ps1     # Windows PowerShell
pip install -r requirements.txt

cp .env.example .env
# paste your real Gemini API key into .env

python app.py
```

## Note

Both apps run on Render's free tier, so the first request after ~15 min of
inactivity takes 30-60s to wake up. That's normal, not a bug.