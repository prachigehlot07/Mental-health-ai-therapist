
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatBox = document.getElementById('chat-box');

chatForm.addEventListener('submit', async (e) => {
e.preventDefault();
const input = userInput.value.trim();
if (!input) return;

appendMessage('user', input);
userInput.value = '';

try {
    const res = await fetch('/chatbot/reply', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ msg: input }),
    });

    if (!res.ok) throw new Error('Network response was not ok.');

    const data = await res.json();
    appendMessage('bot', data.reply);
} catch (err) {
    console.error('Error:', err);
    appendMessage('bot', "Oops, I'm offline or broken 😵");
}
});

function appendMessage(sender, text) {
    const msg = document.createElement('div');
    msg.classList.add('message', sender);
    msg.textContent = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

