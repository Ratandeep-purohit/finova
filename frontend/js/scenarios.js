let currentScenarioId = null;
let currentScenarioType = 'SCAM';

async function loadScenario(type = 'SCAM') {
    currentScenarioType = type;
    try {
        let res = await fetch(`${API_BASE}/scenarios/?type=${type}`);
        if(res.ok) {
            let data = await res.json();
            currentScenarioId = data.id;
            
            document.getElementById("sc-type").innerText = data.type === 'SCAM' ? '⚠️ FRAUD ALERT DETECTED' : '📄 TAX PREPARATION';
            document.getElementById("sc-type").style.color = data.type === 'SCAM' ? 'var(--danger)' : 'var(--primary)';
            document.getElementById("sc-title").innerText = data.title;
            document.getElementById("sc-desc").innerText = data.description;
            
            let actionsHTML = "";
            if(data.type === 'SCAM') {
                actionsHTML = `
                    <button class="btn btn-outline" style="flex: 1; border-color: var(--success); color: var(--success);" onclick="submitAnswer('DECLINE')">Decline & Report</button>
                    <button class="btn btn-danger" style="flex: 1;" onclick="submitAnswer('PAY')">Pay Amount</button>
                `;
            } else {
                actionsHTML = `
                    <button class="btn btn-primary" style="flex: 1" onclick="submitAnswer('YES')">Yes</button>
                    <button class="btn btn-outline" style="flex: 1; border-color: var(--danger); color: var(--danger)" onclick="submitAnswer('NO')">No</button>
                `;
            }
            
            document.getElementById("sc-actions").innerHTML = actionsHTML;
            document.getElementById("sc-result").style.display = "none";
            document.getElementById("next-btn").style.display = "none";
            document.getElementById("sc-actions").style.display = "flex";
        }
    } catch(e) {
        console.error("Fetch err", e);
    }
}

async function submitAnswer(action) {
    try {
        let res = await fetch(`${API_BASE}/scenarios/answer/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: currentUser, scenario_id: currentScenarioId, action: action})
        });
        
        let data = await res.json();
        let resDiv = document.getElementById("sc-result");
        resDiv.style.display = "block";
        
        if(data.correct) {
            resDiv.innerHTML = `<strong class="text-success text-xl">SUCCESS!</strong><br><p class="mt-2 text-secondary">You made the right call.</p><div class="text-success mt-4 font-mono font-bold">+XP ${data.message}</div>`;
            resDiv.className = "scenario-result-box scenario-success";
        } else {
            resDiv.innerHTML = `<strong class="text-danger text-xl">CRITICAL MISTAKE!</strong><br><p class="mt-2 text-secondary">This error just cost you hard-earned cash.</p><div class="text-danger mt-4 font-mono font-bold">Lost ₹500.00</div>`;
            resDiv.className = "scenario-result-box scenario-danger";
        }
        
        document.getElementById("sc-actions").style.display = "none";
        document.getElementById("next-btn").style.display = "inline-flex";
        
        fetchProfile();
    } catch(e) {
        console.error("Submit error", e);
    }
}
