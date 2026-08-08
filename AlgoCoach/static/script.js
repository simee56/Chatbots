const introScreen = document.getElementById("intro-screen");
const chatScreen = document.getElementById("chat-screen");
const startBtn = document.getElementById("start-btn");
const setupError = document.getElementById("setup-error");
const messagesEl = document.getElementById("messages");
const messageInput = document.getElementById("message-input");
const resetBtn = document.getElementById("reset-btn");

function addLine(text, who) {
  const line = document.createElement("div");
  line.className = `line ${who}`;

  const tag = document.createElement("span");
  tag.className = "tag";
  tag.textContent = who === "user" ? "you >" : "algocoach >";
  line.appendChild(tag);

  const textEl = document.createElement("span");
  textEl.className = "text";
  textEl.textContent = text;
  line.appendChild(textEl);

  messagesEl.appendChild(line);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return line;
}

function addTypingLine() {
  const line = document.createElement("div");
  line.className = "line bot typing";

  const tag = document.createElement("span");
  tag.className = "tag";
  tag.textContent = "algocoach >";
  line.appendChild(tag);

  const textEl = document.createElement("span");
  textEl.className = "text";
  textEl.innerHTML = `<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>`;
  line.appendChild(textEl);

  messagesEl.appendChild(line);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return line;
}

async function startChat() {
  setupError.textContent = "";
  startBtn.disabled = true;
  startBtn.textContent = "$ booting...";

  try {
    const res = await fetch("/start", { method: "POST" });
    const data = await res.json();

    if (!res.ok) {
      setupError.textContent = data.error || "session failed to start.";
      startBtn.disabled = false;
      startBtn.textContent = "$ run session.start()";
      return;
    }

    introScreen.classList.add("hidden");
    chatScreen.classList.remove("hidden");
    resetBtn.classList.remove("hidden");
    addLine(data.message, "bot");
    messageInput.focus();
  } catch (err) {
    setupError.textContent = "connection failed. is the server running?";
    startBtn.disabled = false;
    startBtn.textContent = "$ run session.start()";
  }
}

async function sendMessage() {
  const text = messageInput.value.trim();
  if (!text) return;

  addLine(text, "user");
  messageInput.value = "";
  messageInput.disabled = true;

  const typingLine = addTypingLine();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    typingLine.remove();

    if (!res.ok) {
      addLine(data.error || "something broke.", "bot");
    } else {
      addLine(data.message, "bot");
    }
  } catch (err) {
    typingLine.remove();
    addLine("connection error. try again.", "bot");
  } finally {
    messageInput.disabled = false;
    messageInput.focus();
  }
}

async function resetChat() {
  await fetch("/reset", { method: "POST" });
  messagesEl.innerHTML = "";
  chatScreen.classList.add("hidden");
  resetBtn.classList.add("hidden");
  introScreen.classList.remove("hidden");
  startBtn.disabled = false;
  startBtn.textContent = "$ run session.start()";
}

startBtn.addEventListener("click", startChat);
resetBtn.addEventListener("click", resetChat);
messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});