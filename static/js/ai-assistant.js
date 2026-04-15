(function() {
    const WIDGET_HTML = `
    <div id="ai-widget" style="position:fixed;bottom:1.5rem;right:1.5rem;z-index:9999;font-family:Helvetica Neue,Arial,sans-serif">
        <div id="ai-chat" style="display:none;width:350px;max-height:500px;background:#161616;border:1px solid #333;border-radius:12px;overflow:hidden;flex-direction:column;margin-bottom:.5rem;box-shadow: 0 10px 25px rgba(0,0,0,0.5)">
            <div style="background:#CF2030;padding:.8rem 1rem;display:flex;justify-content:space-between;align-items:center">
                <span style="color:#fff;font-weight:600;font-size:.9rem">AI Assistant</span>
                <button onclick="toggleAI()" style="background:none;border:none;color:#fff;font-size:1.2rem;cursor:pointer">×</button>
            </div>
            <div id="ai-messages" style="flex:1;overflow-y:auto;padding:1rem;max-height:350px;min-height:200px"></div>
            <div style="padding:.8rem;border-top:1px solid #222;display:flex;gap:.5rem">
                <input id="ai-input" type="text" placeholder="Tanya sesuatu..." style="flex:1;padding:.6rem .8rem;background:#0a0a0a;border:1px solid #333;border-radius:8px;color:#fff;font-size:.9rem;outline:none" onkeydown="if(event.key==='Enter')sendAI()">
                <button onclick="sendAI()" style="background:#CF2030;border:none;color:#fff;padding:.6rem 1rem;border-radius:8px;cursor:pointer;font-size:.9rem">Kirim</button>
            </div>
        </div>
        <button onclick="toggleAI()" id="ai-fab" style="width:56px;height:56px;border-radius:50%;background:#CF2030;border:none;color:#fff;font-size:1.5rem;cursor:pointer;box-shadow:0 4px 12px rgba(207,32,48,.4);transition:transform .2s; display:flex; align-items:center; justify-content:center" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
        </button>
    </div>`;

    document.body.insertAdjacentHTML('beforeend', WIDGET_HTML);

    const pageContext = document.body.getAttribute('data-ai-context') || 'general';
    let chatHistory = [];
    let greeted = false;

    const GREETINGS = {
        form: "Halo! Saya bantu isi form ini. Kalau bingung di pertanyaan mana pun, langsung tanya saja.",
        edu: "Halo! Saya bisa jelaskan konsep yang ada di halaman ini. Tanya apa saja.",
        general: "Halo! Saya asisten Mahardika Hub. Ada yang bisa dibantu?"
    };

    window.toggleAI = function() {
        const chat = document.getElementById('ai-chat');
        const fab = document.getElementById('ai-fab');
        if (chat.style.display === 'none') {
            chat.style.display = 'flex';
            fab.style.display = 'none';
            if (!greeted) {
                addMessage('assistant', GREETINGS[pageContext] || GREETINGS.general);
                greeted = true;
            }
            document.getElementById('ai-input').focus();
        } else {
            chat.style.display = 'none';
            fab.style.display = 'flex';
        }
    };

    window.sendAI = async function() {
        const input = document.getElementById('ai-input');
        const text = input.value.trim();
        if (!text) return;

        addMessage('user', text);
        input.value = '';
        input.disabled = true;

        chatHistory.push({role: 'user', content: text});

        try {
            const res = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({messages: chatHistory, context: pageContext})
            });
            const data = await res.json();
            const reply = data.reply || 'Maaf, tidak bisa memproses. Coba lagi.';
            addMessage('assistant', reply);
            chatHistory.push({role: 'assistant', content: reply});
        } catch(e) {
            addMessage('assistant', 'Koneksi terputus. Coba lagi.');
        }
        input.disabled = false;
        input.focus();
    };

    function addMessage(role, text) {
        const container = document.getElementById('ai-messages');
        const div = document.createElement('div');
        div.style.cssText = `margin-bottom:.8rem;padding:.6rem .8rem;border-radius:8px;font-size:.85rem;line-height:1.5;max-width:85%;${
            role === 'user'
                ? 'background:#CF2030;color:#fff;margin-left:auto;text-align:right'
                : 'background:#222;color:#ddd'
        }`;
        div.textContent = text;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }
})();
