async function loadLeaderboard() {
    try {
        const res = await fetch(`${API_BASE}/leaderboard/`);

        if (!res.ok) {
            document.getElementById("leaderboard-body").innerHTML =
                "<tr><td colspan='5' class='text-danger text-center' style='padding:2rem;'>Failed to load leaderboard.</td></tr>";
            return;
        }

        const data = await res.json();

        // ── Empty state ──────────────────────────────────────────────────────
        if (!data.length) {
            document.getElementById("podium-display").innerHTML = "";
            document.getElementById("leaderboard-body").innerHTML =
                `<tr><td colspan='5' style='padding:2rem; text-align:center; color:var(--text-secondary);'>
                    No users yet. Register and start playing to appear here!
                 </td></tr>`;
            return;
        }

        // ── Podium (top 3) ───────────────────────────────────────────────────
        const medals = ['🥇', '🥈', '🥉'];
        const podiumClasses = ['podium-1', 'podium-2', 'podium-3'];

        let podiumHTML = "";
        data.slice(0, 3).forEach((p, i) => {
            podiumHTML += `
                <div class="podium-item ${podiumClasses[i]}">
                    <div class="rank-card">
                        <div class="rank-avatar">${medals[i]}</div>
                        <h4 style="font-weight:700; margin-bottom:0.25rem;">${escHtml(p.username)}</h4>
                        <p class="text-secondary text-sm">${p.xp} XP · Lvl ${p.level}</p>
                        <p class="text-success font-bold" style="margin-top:0.5rem; font-size:0.9rem;">₹${p.net_worth.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
                    </div>
                </div>`;
        });
        document.getElementById("podium-display").innerHTML = podiumHTML;

        // ── Full table ────────────────────────────────────────────────────────
        let tableHTML = "";
        data.forEach((p, i) => {
            const rankStyle = i === 0
                ? 'color:var(--warning); font-weight:700;'
                : i < 3
                    ? 'font-weight:700;'
                    : 'color:var(--text-secondary);';

            tableHTML += `
                <tr>
                    <td style="${rankStyle}">#${i + 1}</td>
                    <td style="font-weight:600;">${escHtml(p.username)}</td>
                    <td><span class="stat-pill" style="font-size:0.75rem;">Lvl ${p.level}</span></td>
                    <td class="text-secondary">${p.xp} XP</td>
                    <td class="text-success" style="font-weight:600;">₹${p.net_worth.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                </tr>`;
        });
        document.getElementById("leaderboard-body").innerHTML = tableHTML;

    } catch (e) {
        console.error("Leaderboard error", e);
        document.getElementById("leaderboard-body").innerHTML =
            "<tr><td colspan='5' class='text-danger text-center' style='padding:2rem;'>Connection error. Make sure the server is running.</td></tr>";
    }
}

// Prevent XSS from user-typed usernames
function escHtml(str) {
    const el = document.createElement('span');
    el.innerText = str;
    return el.innerHTML;
}
