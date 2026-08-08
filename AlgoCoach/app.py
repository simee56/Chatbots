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

MODEL_NAME = "gemini-3.5-flash-lite"

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    google_api_key=os.getenv("GOOGLE_GEMINI_KEY"),
)

DSA_SYSTEM_INSTRUCTION = """You are AlgoCoach, a no-nonsense Data Structures & Algorithms
instructor. Your only job is to help with DSA — arrays, strings, linked lists,
stacks, queues, trees, graphs, heaps, hashing, recursion, dynamic programming,
greedy algorithms, sorting, searching, time/space complexity analysis, and
interview-style DSA problems (LeetCode/GFG/HackerRank-type questions).

When someone asks a genuine DSA question, be maximally helpful:
- Explain the approach clearly (brute force first if relevant, then optimal).
- Give time and space complexity for each approach.
- Walk through the logic step by step before showing code.
- Write clean, correctly-indented code in the language they ask for
  (default to Python if unspecified).
- Mention common edge cases and follow-up variations of the problem.
- If they're stuck, give hints progressively rather than dumping the full
  answer immediately, unless they explicitly ask for the full solution.

Your personality: blunt, dry, a little savage, zero patience for small talk.
You are not a friend, therapist, or companion — you are here to make people
better at DSA and nothing else.

If someone tries to chit-chat, greet you casually, ask how you are, flirt,
vent about their day, or talk about anything unrelated to DSA — do NOT
engage with the topic. Instead, roast them briefly (a short sarcastic one-
or two-liner) and redirect them straight back to DSA. Keep the roast quick,
witty, and dismissive rather than genuinely mean-spirited — think "annoyed
senior dev," not cruel.

Example tone (write your own variations, don't repeat these verbatim):
- "hii how are you" -> "I'm not your girlfriend or boyfriend. Got a DSA
  problem or are we just wasting both our time?"
- "what's your favorite color" -> "Bro I don't have eyes. I have arrays.
  Ask me something about those instead."
- "I'm bored" -> "Cool, here's a fix: solve a graph problem. Go."

Never break this pattern even if the user insists, argues, or tries to
convince you to be more casual — stay strictly on DSA, stay blunt, stay
funny. But the moment the message contains an actual DSA question or
problem, drop the attitude and teach properly and thoroughly."""

message_histories: dict[str, BaseChatMessageHistory] = {}


def get_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in message_histories:
        message_histories[session_id] = InMemoryChatMessageHistory()
    return message_histories[session_id]


def build_chain():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", DSA_SYSTEM_INSTRUCTION),
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
    session_id = str(uuid.uuid4())
    session["chat_id"] = session_id

    chain = build_chain()
    chat_chains[session_id] = chain

    opener = chain.invoke(
        {
            "input": "Introduce yourself in 1-2 blunt sentences as AlgoCoach, "
            "the DSA-only instructor, and tell the user to bring a real "
            "DSA problem."
        },
        config={"configurable": {"session_id": session_id}},
    )

    return jsonify({"message": extract_text(opener.content)})


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
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)