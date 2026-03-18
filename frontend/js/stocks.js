let oldPrices = {};
let sessionTrades = 0;
let sessionPnL = 0;

// ── Fetch & render stocks ──────────────────────────────────────────────────
async function fetchStocks() {
    try {
        let res = await fetch(`${API_BASE}/stocks/`);
        if (res.ok) renderStocks(await res.json());
    } catch (e) { console.error("Market fetch error", e); }
}

function renderStocks(stocks) {
    let html = "";
    stocks.forEach(st => {
        const price    = parseFloat(st.current_price);
        const old      = oldPrices[st.symbol] ?? price;
        const diff     = price - old;
        const pClass   = diff > 0 ? "badge-up" : diff < 0 ? "badge-dn" : "badge-neu";
        const arrow    = diff > 0 ? "▲" : diff < 0 ? "▼" : "—";
        const pct      = old !== 0 ? ((diff / old) * 100).toFixed(2) : "0.00";
        oldPrices[st.symbol] = price;

        html += `
        <div class="stock-card">
            <div>
                <span style="font-weight:700;">${st.symbol}</span>
                <span class="text-secondary text-sm" style="margin-left:0.5rem;">${st.name}</span><br>
                <span style="font-weight:600; font-size:1rem;">₹${price.toFixed(2)}</span>
                <span class="${pClass}" style="margin-left:0.5rem;">${arrow} ${Math.abs(pct)}%</span>
            </div>
            <div class="stock-actions">
                <input class="qty-input" type="number" id="qty-${st.id}" value="10" min="1" max="500">
                <button class="btn btn-primary" style="padding:0.35rem 0.75rem; font-size:0.8rem;" onclick="trade(${st.id},'buy')">Buy</button>
                <button class="btn btn-outline"  style="padding:0.35rem 0.75rem; font-size:0.8rem;" onclick="trade(${st.id},'sell')">Sell</button>
            </div>
        </div>`;
    });
    document.getElementById("stock-list").innerHTML = html;
}

// ── Fetch & render portfolio ───────────────────────────────────────────────
async function fetchPortfolio() {
    try {
        let res = await fetch(`${API_BASE}/stocks/portfolio/?username=${currentUser}`);
        if (res.ok) renderPortfolio(await res.json());
    } catch (e) { console.error("Portfolio fetch error", e); }
}

function renderPortfolio(portfolio) {
    const el = document.getElementById("portfolio-list");
    if (!portfolio.length) {
        el.innerHTML = '<p class="text-secondary text-center" style="padding:2rem;">You don\'t own any stocks yet.</p>';
        return;
    }
    let html = "";
    portfolio.forEach(p => {
        const cur  = parseFloat(p.current_price);
        const avg  = parseFloat(p.average_buy_price);
        const pnl  = (cur - avg) * p.quantity;
        const cls  = pnl >= 0 ? "text-success" : "text-danger";
        const sign = pnl >= 0 ? "+" : "";
        html += `
        <div class="portfolio-item">
            <div>
                <strong>${p.symbol}</strong>
                <span class="text-secondary text-sm" style="margin-left:0.5rem;">${p.quantity} shares</span><br>
                <span class="text-secondary text-sm">Avg ₹${avg.toFixed(2)} · Now ₹${cur.toFixed(2)}</span>
            </div>
            <span class="${cls} font-bold text-sm">${sign}₹${pnl.toFixed(2)}</span>
        </div>`;
    });
    el.innerHTML = html;
}

// ── Trade ─────────────────────────────────────────────────────────────────
async function trade(stockId, action) {
    const qtyEl = document.getElementById(`qty-${stockId}`);
    const qty   = parseInt(qtyEl ? qtyEl.value : 10);
    if (!qty || qty < 1) { showToast("Enter a valid quantity.", "error"); return; }

    const ep = action === 'buy' ? 'buy/' : 'sell/';
    try {
        let res = await fetch(`${API_BASE}/stocks/${ep}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser, stock_id: stockId, quantity: qty })
        });
        let data = await res.json();
        if (res.ok) {
            sessionTrades++;
            let toastMsg = data.message;
            if (data.profit !== undefined) {
                const pnl = parseFloat(data.profit);
                sessionPnL += pnl;
                const sign = pnl >= 0 ? "+" : "";
                toastMsg += `  ·  P&L: ${sign}₹${pnl.toFixed(2)}`;
                document.getElementById("stat-pnl").innerText = `${sessionPnL >= 0 ? '+' : ''}₹${sessionPnL.toFixed(2)}`;
                document.getElementById("stat-pnl").style.color = sessionPnL >= 0 ? "var(--success)" : "var(--danger)";
            }
            document.getElementById("stat-trades").innerText = sessionTrades;
            showToast(toastMsg, "success");
            fetchProfile();
            fetchPortfolio();
        } else {
            showToast(data.error || "Transaction failed.", "error");
        }
    } catch (e) {
        showToast("Could not reach the server.", "error");
    }
}

// ── Toast notification ─────────────────────────────────────────────────────
function showToast(msg, type = "success") {
    const old = document.getElementById("toast-el");
    if (old) old.remove();
    const t = document.createElement("div");
    t.id = "toast-el";
    t.className = `toast ${type}`;
    t.innerText = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 4000);
}

// ── Init ──────────────────────────────────────────────────────────────────
function initStocks() {
    fetchStocks();
    fetchPortfolio();
    setInterval(() => { fetchStocks(); fetchPortfolio(); }, 5000);
}
