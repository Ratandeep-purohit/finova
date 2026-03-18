let currentScenarioId = null;

async function loadScenario() {
    let type = Math.random() > 0.5 ? "SCAM" : "TAX"; // Mix them up
    try {
        let res = await fetch(`${API_BASE}/scenarios/?type=${type}`);
        if(res.ok) {
            let data = await res.json();
            currentScenarioId = data.id;
            
            document.getElementById("sc-type").innerText = data.type === 'SCAM' ? 'UPI Fraud Alert' : 'Tax Challenge';
            document.getElementById("sc-type").style.color = data.type === 'SCAM' ? 'var(--danger)' : 'var(--primary)';
            document.getElementById("sc-title").innerText = data.title;
            document.getElementById("sc-desc").innerText = data.description;
            
            // Build buttons contextually
            let actionsHTML = "";
            if(data.type === 'SCAM') {
                actionsHTML = `
                    <button class="btn btn-outline" style="width: 50%" onclick="submitAnswer('DECLINE')">Decline/Report</button>
                    <button class="btn btn-primary" style="width: 50%" onclick="submitAnswer('PAY')">Pay Amount</button>
                `;
            } else {
                actionsHTML = `
                    <button class="btn btn-primary" style="width: 50%" onclick="submitAnswer('YES')">Yes</button>
                    <button class="btn btn-primary" style="width: 50%" onclick="submitAnswer('NO')">No</button>
                `;
            }
            
            document.getElementById("sc-actions").innerHTML = actionsHTML;
            document.getElementById("sc-result").innerText = "";
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
        
        if(data.correct) {
            resDiv.innerText = `[SUCCESS] +XP Gained! ${data.message}`;
            resDiv.className = "text-success";
        } else {
            resDiv.innerText = `[FAILED] ${data.message}`;
            resDiv.className = "text-danger";
        }
        
        document.getElementById("sc-actions").style.display = "none";
        document.getElementById("next-btn").style.display = "inline-block";
        
        // Update top bar stats
        fetchProfile();
    } catch(e) {
        console.error("Submit error");
    }
}
