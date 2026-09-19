function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function appendMessage(text, sender) {
    const chatBody = document.getElementById('chatBody');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'msg ' + (sender === 'user' ? 'user-msg' : 'ai-msg');
    msgDiv.innerText = text;
    chatBody.appendChild(msgDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
}

async function sendMessageToAI(message) {
    appendMessage(message, 'user');

    try {
        const response = await fetch('/api/agent/', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ "message": message }) 
        });

        const data = await response.json();
        
        if (response.ok) {
            appendMessage(data.response || data.reply || "Done.", 'ai');
        } else {
            appendMessage("Error: " + (data.error || "UnKnown "), 'ai');
        }

    } catch (error) {
        appendMessage('Bad Connecting.', 'ai');
    }
}

function sendQuickMessage(text) {
    sendMessageToAI(text);
}

function sendManualMessage() {
    const inputField = document.getElementById('chatInput');
    const text = inputField.value.trim();
    if (text !== '') {
        sendMessageToAI(text);
        inputField.value = ''; 
    }
}

document.getElementById('chatInput').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendManualMessage();
    }
});