/**
 * Pashu Suraksha - Veterinary Chatbot UI Controller ("Pashu AI Sahayak")
 * Manages floating chat drawer, message thread, voice playback of replies, and quick question pills.
 */

class VeterinaryChatbotManager {
  constructor() {
    this.isOpen = false;
    this.currentLanguage = 'hi';
    this.messages = [];
  }

  init() {
    this.setupEventListeners();
    this.renderInitialGreeting();
  }

  setupEventListeners() {
    const floatBtn = document.getElementById('chatFloatBtn');
    const closeBtn = document.getElementById('chatDrawerCloseBtn');
    const sendBtn = document.getElementById('chatSendBtn');
    const chatInput = document.getElementById('chatTextInput');
    const langSelect = document.getElementById('chatLanguageSelect');

    if (floatBtn) {
      floatBtn.addEventListener('click', () => this.toggleChat());
    }

    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.closeChat());
    }

    if (sendBtn) {
      sendBtn.addEventListener('click', () => this.sendMessage());
    }

    if (chatInput) {
      chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          this.sendMessage();
        }
      });
    }

    if (langSelect) {
      langSelect.addEventListener('change', (e) => {
        this.currentLanguage = e.target.value;
      });
    }
  }

  toggleChat() {
    if (this.isOpen) {
      this.closeChat();
    } else {
      this.openChat();
    }
  }

  openChat() {
    const drawer = document.getElementById('chatDrawer');
    const floatBtn = document.getElementById('chatFloatBtn');
    if (drawer) drawer.classList.add('open');
    if (floatBtn) floatBtn.style.display = 'none';
    this.isOpen = true;

    // Focus input
    setTimeout(() => {
      document.getElementById('chatTextInput')?.focus();
    }, 200);
  }

  closeChat() {
    const drawer = document.getElementById('chatDrawer');
    const floatBtn = document.getElementById('chatFloatBtn');
    if (drawer) drawer.classList.remove('open');
    if (floatBtn) floatBtn.style.display = 'flex';
    this.isOpen = false;
    window.VoiceManager.stop();
  }

  renderInitialGreeting() {
    const thread = document.getElementById('chatMessagesThread');
    if (!thread) return;

    thread.innerHTML = `
      <div class="chat-bubble bot">
        <div class="bubble-sender">🤖 Pashu AI Sahayak (पशु एआई सहायक)</div>
        <div class="bubble-text">
          नमस्ते! मैं पशु स्वास्थ्य एवं रोग निवारण सहायक हूँ। आप मुझसे पशु रोगों के लक्षण, प्राथमिक उपचार, टीकाकरण व दवा निकासी के बारे में कभी भी पूछ सकते हैं।
        </div>
        <div class="bubble-quick-prompts">
          <span class="quick-prompt" onclick="window.ChatbotManager.sendUserQuery('गाय के मुंह में छाले हैं क्या करें?')">🐮 मुंह में छाले</span>
          <span class="quick-prompt" onclick="window.ChatbotManager.sendUserQuery('लम्पी स्किन रोग से बचाव')">⚪ लम्पी रोग रोकथाम</span>
          <span class="quick-prompt" onclick="window.ChatbotManager.sendUserQuery('पशु का पेट फूलने (अफारा) का तुरंत उपचार')">⚠️ अफारा (पेट फूलना)</span>
          <span class="quick-prompt" onclick="window.ChatbotManager.sendUserQuery('टीकाकरण कैलेंडर')">💉 टीकाकरण समय</span>
        </div>
      </div>
    `;
  }

  sendUserQuery(text) {
    const input = document.getElementById('chatTextInput');
    if (input) input.value = text;
    this.sendMessage();
  }

  async sendMessage() {
    const input = document.getElementById('chatTextInput');
    const text = input ? input.value.trim() : '';
    if (!text) return;

    input.value = '';
    this.appendUserMessage(text);

    // Typing indicator
    const typingId = this.showTypingIndicator();

    try {
      const res = await fetch('/api/chatbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          language: this.currentLanguage
        })
      });

      const data = await res.json();
      this.removeTypingIndicator(typingId);

      if (data.success) {
        this.appendBotReply(data);
      }
    } catch (err) {
      console.error('Chatbot request error:', err);
      this.removeTypingIndicator(typingId);
      this.appendBotReply({
        title: "Connection Error",
        reply: "सॉरी, सर्वर से जुड़ने में त्रुटि हुई। कृपया थोड़ी देर बाद पुनः प्रयास करें।",
        suggested_questions: []
      });
    }
  }

  appendUserMessage(text) {
    const thread = document.getElementById('chatMessagesThread');
    if (!thread) return;

    const div = document.createElement('div');
    div.className = 'chat-bubble user';
    div.innerHTML = `<div class="bubble-text">${this.escapeHtml(text)}</div>`;
    thread.appendChild(div);
    this.scrollToBottom();
  }

  appendBotReply(data) {
    const thread = document.getElementById('chatMessagesThread');
    if (!thread) return;

    const div = document.createElement('div');
    div.className = 'chat-bubble bot';

    // Format markdown-like bold text & bullet points
    let formattedReply = this.escapeHtml(data.reply)
      .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
      .replace(/\n/g, '<br>');

    let quickPillsHtml = '';
    if (data.suggested_questions && data.suggested_questions.length > 0) {
      quickPillsHtml = `
        <div class="bubble-quick-prompts" style="margin-top:0.6rem;">
          ${data.suggested_questions.map(q => `
            <span class="quick-prompt" onclick="window.ChatbotManager.sendUserQuery(decodeURIComponent('${encodeURIComponent(q)}'))">${this.escapeHtml(q)}</span>
          `).join('')}
        </div>
      `;
    }

    div.innerHTML = `
      <div class="bubble-header">
        <span class="bubble-sender">🤖 ${this.escapeHtml(data.title || 'Pashu AI')}</span>
        <button class="btn-bubble-tts" onclick="window.ChatbotManager.speakText(this)" data-text="${encodeURIComponent(data.reply || '')}">
          🔊 सुनें (Listen)
        </button>
      </div>
      <div class="bubble-text">${formattedReply}</div>
      ${quickPillsHtml}
    `;

    thread.appendChild(div);
    this.scrollToBottom();
  }

  speakText(btn) {
    const rawText = decodeURIComponent(btn.dataset.text || '');
    if (!rawText) return;
    const bcpCode = this.currentLanguage === 'hi' ? 'hi-IN' : 'en-IN';
    window.VoiceManager.togglePlayback(rawText, bcpCode);
  }

  showTypingIndicator() {
    const thread = document.getElementById('chatMessagesThread');
    if (!thread) return null;

    const id = 'typing_' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'chat-bubble bot typing-indicator';
    div.innerHTML = `<span></span><span></span><span></span>`;
    thread.appendChild(div);
    this.scrollToBottom();
    return id;
  }

  removeTypingIndicator(id) {
    if (!id) return;
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  scrollToBottom() {
    const thread = document.getElementById('chatMessagesThread');
    if (thread) {
      thread.scrollTop = thread.scrollHeight;
    }
  }

  escapeHtml(str) {
    return (str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }
}

window.ChatbotManager = new VeterinaryChatbotManager();
