function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

async function callBackend(endpoint, data) {
    try {
        const response = await fetch(`http://localhost:5000/api/${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        return result;
    } catch (error) {
        throw error;
    }
}

async function handleTranslate() {
    const text = document.getElementById('translate-text').value;
    const lang = document.getElementById('translate-lang').value;
    const btn = document.getElementById('translate-btn');
    const loading = document.getElementById('translate-loading');
    const result = document.getElementById('translate-result');
    const error = document.getElementById('translate-error');
    
    if (!text.trim()) {
        alert('Please enter text to translate');
        return;
    }
    
    btn.disabled = true;
    loading.style.display = 'block';
    result.classList.remove('show');
    error.style.display = 'none';
    
    try {
        const response = await callBackend('translate', { text, language: lang });
        
        document.getElementById('translate-output').textContent = response.translation;
        document.getElementById('translate-romaji').textContent = response.romaji;
        
        const breakdownHtml = response.breakdown.length > 0 
            ? response.breakdown.map(item => `
                <div class="breakdown-item">
                    <strong>${item.english}</strong>
                    <span><strong>${item.target}</strong> (${item.romaji})</span>
                    <span>${item.meaning}</span>
                </div>
            `).join('')
            : '<div style="color: #9c5a7f;">See translation above for word-by-word breakdown</div>';
        
        document.getElementById('translate-breakdown').innerHTML = breakdownHtml;
        result.classList.add('show');
    } catch (err) {
        error.textContent = 'Error: ' + err.message;
        error.style.display = 'block';
    } finally {
        btn.disabled = false;
        loading.style.display = 'none';
    }
}

async function handleSummarize() {
    const text = document.getElementById('summarize-text').value;
    const btn = document.getElementById('summarize-btn');
    const loading = document.getElementById('summarize-loading');
    const result = document.getElementById('summarize-result');
    const error = document.getElementById('summarize-error');
    
    if (!text.trim()) {
        alert('Please enter text to summarize');
        return;
    }
    
    btn.disabled = true;
    loading.style.display = 'block';
    result.classList.remove('show');
    error.style.display = 'none';
    
    try {
        const response = await callBackend('summarize', { text });
        document.getElementById('summarize-output').textContent = response.summary;
        result.classList.add('show');
    } catch (err) {
        error.textContent = 'Error: ' + err.message;
        error.style.display = 'block';
    } finally {
        btn.disabled = false;
        loading.style.display = 'none';
    }
}

async function handleSentiment() {
    const text = document.getElementById('sentiment-text').value;
    const btn = document.getElementById('sentiment-btn');
    const loading = document.getElementById('sentiment-loading');
    const result = document.getElementById('sentiment-result');
    const error = document.getElementById('sentiment-error');
    
    if (!text.trim()) {
        alert('Please enter text to analyze');
        return;
    }
    
    btn.disabled = true;
    loading.style.display = 'block';
    result.classList.remove('show');
    error.style.display = 'none';
    
    try {
        const response = await callBackend('sentiment', { text });
        
        const badgeClass = `sentiment-${response.sentiment.toLowerCase()}`;
        const html = `
            ${response.analysis}
            <div class="sentiment-badge ${badgeClass}">${response.sentiment}</div>
        `;
        
        document.getElementById('sentiment-output').innerHTML = html;
        result.classList.add('show');
    } catch (err) {
        error.textContent = 'Error: ' + err.message;
        error.style.display = 'block';
    } finally {
        btn.disabled = false;
        loading.style.display = 'none';
    }
}

const sel = document.getElementById('translate-lang');
sel.classList.add('placeholder');
sel.addEventListener('change', () => sel.classList.remove('placeholder'));
