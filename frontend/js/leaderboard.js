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
                    let rankIcon = index === 0 ? "👑" : index === 1 ? "🥈" : "🥉";
                    let glowColor = index === 0 ? "#fbbf24" : index === 1 ? "#cbd5e1" : "#d97706";
                    
                    podiumHTML += `
                        <div class="podium-item ${podiumClass}">
                            <div class="rank-card rank-${index + 1}">
                                <div class="rank-avatar">${rankIcon}</div>
                                <h3 class="mb-2 text-xl" style="color: ${glowColor};">${p.username}</h3>
                                <p class="text-secondary font-bold">${p.xp} XP</p>
                                <p class="text-success mt-2 text-sm">₹${p.balance}</p>
                            </div>
                        </div>
                    `;
                }

                // Render Table for everyone including top 3
                let rankClass = index === 0 ? "text-accent text-xl" : index === 1 ? "text-xl" : index === 2 ? "text-xl" : "text-secondary";
                tableHTML += `
                    <tr>
                        <td class="${rankClass} font-mono">#${index + 1}</td>
                        <td class="font-bold">${p.username}</td>
                        <td><span class="stat-pill" style="display:inline-block; padding: 0.25rem 0.75rem; font-size: 0.75rem;">Lvl ${p.level}</span></td>
                        <td class="text-secondary font-mono">${p.xp} XP</td>
                        <td class="text-success font-mono">₹${p.balance}</td>
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
