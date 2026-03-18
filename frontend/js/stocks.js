// Define base URL if not already from auth.js, using the same global variable context
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
        let pClass = st.current_price >= oldPrice ? "text-success" : "text-danger";
        
        html += `
            <tr>
                <td><strong>${st.symbol}</strong></td>
                <td>${st.name}</td>
                <td class="${pClass}">₹${st.current_price}</td>
                <td>
                    <button class="btn btn-primary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;" onclick="tradeStock(${st.id}, 10, 'buy')">Buy 10</button>
                    <button class="btn btn-outline" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; margin-left: 0.5rem;" onclick="tradeStock(${st.id}, 10, 'sell')">Sell 10</button>
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
        html = '<p class="text-secondary">You don\'t own any stocks yet.</p>';
    } else {
        html = `<ul style="list-style: none; padding: 0;">`;
        portfolio.forEach(p => {
            let profit = (p.current_price - p.average_buy_price) * p.quantity;
            let pClass = profit >= 0 ? "text-success" : "text-danger";
            html += `
                <li style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-color);">
                    <strong>${p.symbol}</strong> - ${p.quantity} shares<br/>
                    <small>Buy Avg: ₹${p.average_buy_price} | Current: ₹${p.current_price}</small><br/>
                    PnL: <span class="${pClass}">${profit >= 0 ? '+' : '-'}₹${Math.abs(profit).toFixed(2)}</span>
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
    msgObj.innerText = ""; errObj.innerText = "";
    
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
            if(data.profit) {
                msgObj.innerText += ` | Profit: ₹${parseFloat(data.profit).toFixed(2)} (+XP)`;
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
