// static/chat.js
const chatbox = document.getElementById('chatbox');
const input = document.getElementById('message');
const sendBtn = document.getElementById('send');

sendBtn.addEventListener('click', sendMessage);
input.addEventListener('keypress', function(e) {
    if(e.key === 'Enter') sendMessage();
});

function appendMessage(sender, msg) {
    const p = document.createElement('p');
    p.className = sender;

    // Render HTML for bot, text for user
    if(sender === 'bot') {
        p.innerHTML = `<strong>${sender.toUpperCase()}:</strong> ${msg}`;
    } else {
        p.textContent = `${sender.toUpperCase()}: ${msg}`;
    }

    chatbox.appendChild(p);
    chatbox.scrollTop = chatbox.scrollHeight;
}

async function sendMessage() {
    const msg = input.value;
    if (!msg) return;
    appendMessage('user', msg);
    input.value = '';

    const res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: msg})
    });
    const data = await res.json();
    appendMessage('bot', data.response);
}