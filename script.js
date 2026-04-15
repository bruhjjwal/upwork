const chatArea = document.getElementById('chatArea');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const welcomeScreen = document.getElementById('welcomeScreen');

let conversationHistory = [];
let isLoading = false;

// Auto-resize textarea
chatInput.addEventListener('input', () => {
  chatInput.style.height = 'auto';
  chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
  sendBtn.disabled = !chatInput.value.trim();
});

// Send on Enter (Shift+Enter for newline)
chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

sendBtn.addEventListener('click', sendMessage);

// Suggestion chips
document.querySelectorAll('.suggestion-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    chatInput.value = chip.textContent;
    chatInput.dispatchEvent(new Event('input'));
    sendMessage();
  });
});

function sendMessage() {
  const message = chatInput.value.trim();
  if (!message || isLoading) return;

  // Hide welcome screen
  if (welcomeScreen) {
    welcomeScreen.style.display = 'none';
  }

  // Add user message
  appendMessage('you', message);
  conversationHistory.push({ role: 'user', content: message });

  // Clear input
  chatInput.value = '';
  chatInput.style.height = 'auto';
  sendBtn.disabled = true;

  // Show typing indicator
  showTyping();

  // Call API
  isLoading = true;
  fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: message,
      history: conversationHistory.slice(0, -1) // exclude the message we just added
    })
  })
    .then(res => res.json())
    .then(data => {
      hideTyping();
      if (data.error) {
        appendMessage('assistant', `Error: ${data.error}`);
      } else {
        appendMessage('assistant', data.reply);
        conversationHistory.push({ role: 'model', content: data.reply });
      }
    })
    .catch(err => {
      hideTyping();
      appendMessage('assistant', 'Something went wrong. Please try again.');
      console.error(err);
    })
    .finally(() => {
      isLoading = false;
    });
}

function appendMessage(role, content) {
  const wrapper = document.createElement('div');
  wrapper.className = `message ${role === 'you' ? 'user' : 'assistant'}`;

  const label = document.createElement('div');
  label.className = 'message-label';
  label.textContent = role === 'you' ? 'You' : 'Assistant';

  const body = document.createElement('div');
  body.className = 'message-content';
  body.innerHTML = formatMessage(content);

  const divider = document.createElement('div');
  divider.className = 'message-divider';

  wrapper.appendChild(label);
  wrapper.appendChild(body);
  wrapper.appendChild(divider);
  chatArea.appendChild(wrapper);

  // Scroll to bottom
  chatArea.scrollTop = chatArea.scrollHeight;
}

function formatMessage(text) {
  // Basic markdown-ish formatting
  return text
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Inline code
    .replace(/`(.*?)`/g, '<code>$1</code>')
    // Bullet lists
    .replace(/^\s*[-•]\s+(.+)$/gm, '<li>$1</li>')
    // Numbered lists
    .replace(/^\s*\d+\.\s+(.+)$/gm, '<li>$1</li>')
    // Wrap consecutive <li> in <ul>
    .replace(/((<li>.*?<\/li>\s*)+)/g, '<ul>$1</ul>')
    // Line breaks to paragraphs
    .split(/\n\n+/)
    .map(p => p.trim())
    .filter(p => p)
    .map(p => {
      if (p.startsWith('<ul>') || p.startsWith('<ol>')) return p;
      return `<p>${p.replace(/\n/g, '<br>')}</p>`;
    })
    .join('');
}

function showTyping() {
  const indicator = document.createElement('div');
  indicator.className = 'typing-indicator';
  indicator.id = 'typingIndicator';
  indicator.innerHTML = `
    <span class="message-label">Assistant</span>
    <div class="typing-dots">
      <span></span>
      <span></span>
      <span></span>
    </div>
  `;
  chatArea.appendChild(indicator);
  chatArea.scrollTop = chatArea.scrollHeight;
}

function hideTyping() {
  const indicator = document.getElementById('typingIndicator');
  if (indicator) indicator.remove();
}
