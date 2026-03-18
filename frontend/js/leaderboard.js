async function loadLeaderboard() {
    try {
        let res = await fetch(`${API_BASE}/leaderboard/`);
        if (res.ok) {
            let p_data = await res.json();
            
            // Render Podium
            let podiumHTML = "";
            let tableHTML = "";
            
            p_data.forEach((p, index) => {
                if (index < 3) {
                    let podiumClass = index === 0 ? "podium-1" : index === 1 ? "podium-2" : "podium-3";
                    let rankIcon = index === 0 ? "1" : index === 1 ? "2" : "3";
                    
                    podiumHTML += `
                        <div class="podium-item ${podiumClass}">
                            <div class="rank-card">
                                <div class="rank-avatar">${rankIcon}</div>
                                <h3 class="font-bold">${p.username}</h3>
                                <p class="text-secondary text-sm">${p.xp} XP</p>
                                <p class="text-success mt-2 text-sm font-medium">₹${p.balance}</p>
                            </div>
                        </div>
                    `;
                }

                // Render Table for everyone including top 3
                let rankClass = index === 0 ? "text-warning font-bold" : (index === 1 || index === 2) ? "font-bold" : "text-secondary";
                tableHTML += `
                    <tr>
                        <td class="${rankClass}">#${index + 1}</td>
                        <td class="font-medium">${p.username}</td>
                        <td><span class="stat-pill" style="font-size: 0.75rem;">Lvl ${p.level}</span></td>
                        <td class="text-secondary">${p.xp} XP</td>
                        <td class="text-success font-medium">₹${p.balance}</td>
                    </tr>
                `;
            });
            
            document.getElementById("podium-display").innerHTML = podiumHTML;
            document.getElementById("leaderboard-body").innerHTML = tableHTML;
        }
    } catch (e) {
        console.error("Leaderboard error", e);
        document.getElementById("leaderboard-body").innerHTML = "<tr><td colspan='5' class='text-danger text-center'>Failed to load leaderboard.</td></tr>";
    }
}
