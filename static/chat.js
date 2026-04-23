// static/chat.js
const chatbox = document.getElementById('chatbox');
const input = document.getElementById('message');
const sendBtn = document.getElementById('send');

sendBtn.addEventListener('click', sendMessage);
input.addEventListener('keypress', function(e) {
    if(e.key === 'Enter') sendMessage();
});

function appendMessage(sender, responseData) {
    const p = document.createElement('p');
    p.className = sender;

    if(sender === 'bot') {
        if (typeof responseData === 'object' && responseData.type === 'table') {
            // Build safe table DOM
            const tableContainer = document.createElement('div');
            tableContainer.style.cssText = 'width: 100%; margin: 8px 0; background: #1a1d27; border-radius: 8px; overflow: hidden; font-family: monospace; font-size: 12px;';

            if (responseData.title) {
                const title = document.createElement('div');
                title.textContent = responseData.title;
                title.style.cssText = 'padding: 12px 16px; background: #21253a; color: #e8eaf6; font-weight: bold; border-bottom: 1px solid #333;';
                tableContainer.appendChild(title);
            }

            const table = document.createElement('table');
            table.style.cssText = 'width: 100%; border-collapse: collapse;';

            // Headers
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            headerRow.style.cssText = 'background: #21253a;';
            responseData.columns.forEach(col => {
                const th = document.createElement('th');
                th.textContent = col.label;
                th.style.cssText = 'padding: 10px 12px; text-align: left; color: #a0aec0; font-weight: 500; font-size: 11px; text-transform: uppercase;';
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);

            // Rows
            const tbody = document.createElement('tbody');
            responseData.rows.forEach(rowData => {
                const tr = document.createElement('tr');
                responseData.columns.forEach(col => {
                    const td = document.createElement('td');
                    let value = rowData[col.key] || '—';
                    if (col.key.includes('status')) {
                        const badge = document.createElement('span');
                        badge.textContent = value;
                        badge.style.cssText = 'display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0;';
                        td.appendChild(badge);
                    } else {
                        td.textContent = value;
                    }
                    td.style.cssText = 'padding: 10px 12px; color: #e8eaf6; border-bottom: 1px solid #333;';
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);
            tableContainer.appendChild(table);
            p.appendChild(tableContainer);
        } else {
            // Text fallback - sanitize
            const safeText = DOMPurify ? DOMPurify.sanitize(String(responseData || '')) : String(responseData || '').replace(/</g, '<').replace(/>/g, '>');
            p.innerHTML = `<strong>${sender.toUpperCase()}:</strong> ${safeText}`;
        }
    } else {
        p.textContent = `${sender.toUpperCase()}: ${responseData}`;
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
