const setupScreen = document.getElementById("setup-screen");
const chatScreen = document.getElementById("chat-screen");
const genderGroup = document.getElementById("gender-group");
const partnerNameInput = document.getElementById("partner-name");
const startBtn = document.getElementById("start-btn");
const setupError = document.getElementById("setup-error");
const chatPartnerName = document.getElementById("chat-partner-name");
const chatAvatar = document.getElementById("chat-avatar");
const messagesEl = document.getElementById("messages");
const messageInput = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const resetBtn = document.getElementById("reset-btn");

let selectedGender = null;
let partnerInitial = "?";

genderGroup.addEventListener("click", (e) => {
  const btn = e.target.closest(".toggle-btn");
  if (!btn) return;
  selectedGender = btn.dataset.value;
  [...genderGroup.children].forEach((c) => c.classList.remove("selected"));
  btn.classList.add("selected");
});

function addMessage(text, who) {
  const row = document.createElement("div");
  row.className = `msg-row ${who}`;

  if (who === "partner") {
    const avatar = document.createElement("div");
    avatar.className = "msg-avatar";
    avatar.textContent = partnerInitial;
    row.appendChild(avatar);
  }

  const bubble = document.createElement("div");
  bubble.className = `msg ${who}`;
  bubble.textContent = text;
  row.appendChild(bubble);

  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return row;
}

function addTypingIndicator() {
  const row = document.createElement("div");
  row.className = "msg-row partner typing-row";

  const avatar = document.createElement("div");
  avatar.className = "msg-avatar";
  avatar.textContent = partnerInitial;
  row.appendChild(avatar);

  const bubble = document.createElement("div");
  bubble.className = "msg partner";
  bubble.innerHTML = `<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>`;
  row.appendChild(bubble);

  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return row;
}

async function startChat() {
  setupError.textContent = "";
  const partnerName = partnerNameInput.value.trim();

  if (!selectedGender) {
    setupError.textContent = "Please select whether you're male or female.";
    return;
  }
  if (!partnerName) {
    setupError.textContent = "Please give your partner a name.";
    return;
  }

  startBtn.disabled = true;
  startBtn.textContent = "Starting...";

  try {
    const res = await fetch("/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ gender: selectedGender, partner_name: partnerName }),
    });
    const data = await res.json();

    if (!res.ok) {
      setupError.textContent = data.error || "Something went wrong.";
      startBtn.disabled = false;
      startBtn.textContent = "Start Chatting";
      return;
    }

    partnerInitial = data.partner_name.trim().charAt(0).toUpperCase() || "?";
    chatPartnerName.textContent = data.partner_name;
    chatAvatar.textContent = partnerInitial;

    setupScreen.classList.add("hidden");
    chatScreen.classList.remove("hidden");
    addMessage(data.message, "partner");
    messageInput.focus();
  } catch (err) {
    setupError.textContent = "Could not reach the server. Please try again.";
    startBtn.disabled = false;
    startBtn.textContent = "Start Chatting";
  }
}

async function sendMessage() {
  const text = messageInput.value.trim();
  if (!text) return;

  addMessage(text, "user");
  messageInput.value = "";
  sendBtn.disabled = true;

  const typingRow = addTypingIndicator();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    typingRow.remove();

    if (!res.ok) {
      addMessage(data.error || "Something went wrong.", "partner");
    } else {
      addMessage(data.message, "partner");
    }
  } catch (err) {
    typingRow.remove();
    addMessage("Connection error. Please try again.", "partner");
  } finally {
    sendBtn.disabled = false;
    messageInput.focus();
  }
}

async function resetChat() {
  await fetch("/reset", { method: "POST" });
  messagesEl.innerHTML = "";
  chatScreen.classList.add("hidden");
  setupScreen.classList.remove("hidden");
  startBtn.disabled = false;
  startBtn.textContent = "Start Chatting";
  partnerNameInput.value = "";
  selectedGender = null;
  [...genderGroup.children].forEach((c) => c.classList.remove("selected"));
}

startBtn.addEventListener("click", startChat);
resetBtn.addEventListener("click", resetChat);
sendBtn.addEventListener("click", sendMessage);
messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});
partnerNameInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") startChat();
});