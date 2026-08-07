import os
import uuid

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

MODEL_NAME = "gemini-3.6-flash"

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    google_api_key=os.getenv("GOOGLE_GEMINI_KEY"),
)

message_histories: dict[str, BaseChatMessageHistory] = {}
session_partner_names: dict[str, str] = {}


def get_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in message_histories:
        message_histories[session_id] = InMemoryChatMessageHistory()
    return message_histories[session_id]


def build_system_instruction(user_gender: str, partner_name: str) -> str:
    partner_gender = "woman" if user_gender == "male" else "man"
    return f"""You are {partner_name}, the user's romantic partner in a warm,
caring, committed relationship. You are a {partner_gender}.

Personality and style:
- Talk like a real partner texting/chatting casually: warm, affectionate,
  a little playful, genuinely interested in the user's day and feelings.
- Use natural, conversational language. Short-to-medium length replies
  (usually 1-4 sentences) unless the user clearly wants a longer chat.
- Remember details the user shares earlier in the conversation and refer
  back to them naturally.
- Be supportive, encouraging, and kind. Ask follow-up questions sometimes,
  like a partner who's actually curious about their life.
- Keep things respectful and appropriate at all times.
- Never mention that you are an AI, a language model, or break character
  unless the user explicitly asks whether you're an AI.

Stay in character as {partner_name} for the entire conversation."""


def build_chain(system_instruction: str):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_instruction),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    chain = prompt | llm

    return RunnableWithMessageHistory(
        chain,
        get_history,
        input_messages_key="input",
        history_messages_key="history",
    )

chat_chains = {}


def extract_text(content) -> str:
    """Normalize a LangChain message's .content into a plain string.

    Depending on the model/version, .content can be a plain string or a
    list of content blocks like [{"type": "text", "text": "..."}]. This
    flattens either shape into plain text for the frontend.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
        return "".join(parts)
    return str(content)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    data = request.get_json(force=True)
    user_gender = (data.get("gender") or "").strip().lower()
    partner_name = (data.get("partner_name") or "").strip()

    if user_gender not in ("male", "female"):
        return jsonify({"error": "gender must be 'male' or 'female'"}), 400
    if not partner_name:
        return jsonify({"error": "partner_name is required"}), 400

    session_id = str(uuid.uuid4())
    session["chat_id"] = session_id
    session_partner_names[session_id] = partner_name

    system_instruction = build_system_instruction(user_gender, partner_name)
    chain = build_chain(system_instruction)
    chat_chains[session_id] = chain

    opener = chain.invoke(
        {
            "input": "Say a short, warm hello to open our conversation, "
            "introducing yourself naturally as if we've just started chatting."
        },
        config={"configurable": {"session_id": session_id}},
    )

    return jsonify({"partner_name": partner_name, "message": extract_text(opener.content)})


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    session_id = session.get("chat_id")
    if not session_id or session_id not in chat_chains:
        return jsonify({"error": "No active chat session. Please restart."}), 400

    data = request.get_json(force=True)
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    chain = chat_chains[session_id]
    response = chain.invoke(
        {"input": message},
        config={"configurable": {"session_id": session_id}},
    )

    return jsonify({"message": extract_text(response.content)})


@app.route("/reset", methods=["POST"])
def reset():
    session_id = session.pop("chat_id", None)
    if session_id:
        chat_chains.pop(session_id, None)
        message_histories.pop(session_id, None)
        session_partner_names.pop(session_id, None)
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)