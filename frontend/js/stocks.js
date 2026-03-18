const API_BASE = "/api";
let currentUser = localStorage.getItem("finova_user");
let oldPrices = {};

async function fetchStocks() {
    try {
        let res = await fetch(`${API_BASE}/stocks/`);
        if (res.ok) {
            let data = await res.json();
            renderStocks(data);
        }
    } catch(e) {
        console.error("Error fetching stocks");
    }
}

async function fetchPortfolio() {
    try {
        let res = await fetch(`${API_BASE}/stocks/portfolio/?username=${currentUser}`);
        if(res.ok) {
            let data = await res.json();
            renderPortfolio(data);
        }
    } catch(e) {
        console.error("Portfolio error");
    }
}

function renderStocks(stocks) {
    let html = "";
    stocks.forEach(st => {
        let oldPrice = oldPrices[st.symbol] || st.current_price;
        let diff = st.current_price - oldPrice;
        let pClass = diff >= 0 ? "text-success" : "text-danger";
        let arrow = diff >= 0 ? "▲" : "▼";
        if (diff === 0) { arrow = "—"; pClass = "text-secondary"; }

        html += `
            <tr>
                <td class="font-mono text-primary-color" style="font-weight: 700;">${st.symbol}</td>
                <td class="text-secondary">${st.name}</td>
                <td class="${pClass} font-mono font-bold">₹${st.current_price} <span class="text-xs ml-1">${arrow}</span></td>
                <td>
                    <button class="btn btn-primary" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;" onclick="tradeStock(${st.id}, 10, 'buy')">Buy 10</button>
                    <button class="btn btn-outline" style="padding: 0.4rem 0.8rem; font-size: 0.8rem; margin-left: 0.5rem;" onclick="tradeStock(${st.id}, 10, 'sell')">Sell 10</button>
                </td>
            </tr>
        `;
        oldPrices[st.symbol] = st.current_price;
    });
    document.getElementById("stock-list").innerHTML = html;
}

function renderPortfolio(portfolio) {
    let html = "";
    if(portfolio.length === 0) {
        html = '<p class="text-secondary text-center">You don\'t own any stocks yet.</p>';
    } else {
        html = `<ul style="list-style: none; padding: 0;">`;
        portfolio.forEach(p => {
            let pr_c = parseFloat(p.current_price);
            let pr_avg = parseFloat(p.average_buy_price);
            let profit = (pr_c - pr_avg) * p.quantity;
            let pClass = profit >= 0 ? "text-success" : "text-danger";
            
            html += `
                <li style="margin-bottom: 0.5rem; padding: 1rem; border: 1px solid var(--border-color); border-radius: var(--radius-md); background: rgba(0,0,0,0.2);">
                    <div class="flex justify-between items-center mb-1">
                        <strong class="font-mono text-primary-color">${p.symbol}</strong>
                        <span class="text-secondary text-sm">${p.quantity} shares</span>
                    </div>
                    <div class="flex justify-between items-center text-sm font-mono mt-2">
                        <span class="text-secondary">Avg: ₹${pr_avg.toFixed(2)} | Cur: ₹${pr_c.toFixed(2)}</span>
                        <span class="${pClass} font-bold">${profit >= 0 ? '+' : '-'}₹${Math.abs(profit).toFixed(2)}</span>
                    </div>
                </li>
            `;
        });
        html += `</ul>`;
    }
    document.getElementById("portfolio-list").innerHTML = html;
}

async function tradeStock(id, qty, action) {
    let msgObj = document.getElementById("market-msg");
    let errObj = document.getElementById("market-err");
    msgObj.innerText = ""; msgObj.className = "success-msg font-mono text-center";
    errObj.innerText = ""; errObj.className = "error-msg font-mono text-center";
    
    let ep = action === 'buy' ? 'buy/' : 'sell/';
    try {
        let res = await fetch(`${API_BASE}/stocks/${ep}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: currentUser, stock_id: id, quantity: qty})
        });
        let data = await res.json();
        if(res.ok) {
            msgObj.innerText = data.message;
            if(data.profit !== undefined) {
                msgObj.innerText += ` | PnL: ₹${parseFloat(data.profit).toFixed(2)}`;
                msgObj.className = parseFloat(data.profit) >= 0 ? "success-msg font-mono text-center" : "error-msg font-mono text-center";
            }
            fetchProfile(); // update balance on top
            fetchPortfolio();
        } else {
            errObj.innerText = data.error;
        }
    } catch(e) {
        errObj.innerText = "Transaction failed!";
    }
}

function initStocks() {
    fetchStocks();
    fetchPortfolio();
    setInterval(() => {
        fetchStocks();
        fetchPortfolio();
    }, 5000); // 5 sec update
}
