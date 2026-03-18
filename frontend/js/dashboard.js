const API_BASE = "http://127.0.0.1:8000/api/v1";
let currentUser = localStorage.getItem("finova_user");

async function fetchProfile() {
    if (!currentUser) return;
    try {
        let res = await fetch(`${API_BASE}/user/profile/?username=${currentUser}`);
        if (res.ok) {
            let data = await res.json();

            // Update all stat pills across pages safely
            const safe = (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val; };
            safe("level-txt", `Lvl ${data.level}`);
            safe("xp-txt", `${data.xp} XP`);
            safe("balance-txt", parseFloat(data.balance).toFixed(2));
            safe("username-display", data.username);
            safe("balance-big", `₹${parseFloat(data.balance).toFixed(2)}`);
            safe("stat-level", `Lvl ${data.level}`);
            safe("stat-xp", `${data.xp} XP`);
        }
    } catch (e) {
        console.error("Failed to fetch profile", e);
    }
}
