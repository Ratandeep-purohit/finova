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

async function checkAndRewardMission(missionId, xpReward) {
    if(!currentUser) return;
    
    const storageKey = `finova_missions_${currentUser}`;
    let missions = JSON.parse(localStorage.getItem(storageKey) || "{}");
    
    if (missions[missionId]) return; // already done

    missions[missionId] = true;
    localStorage.setItem(storageKey, JSON.stringify(missions));
    
    try {
        await fetch(`${API_BASE}/user/reward/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: currentUser, xp: xpReward})
        });
        
        const f = document.createElement('div');
        f.style = "position:fixed;top:20px;right:20px;padding:12px 24px;background:#16a34a;color:#fff;border-radius:8px;font-weight:bold;z-index:9999;box-shadow:0 10px 15px -3px rgba(0,0,0,0.1);animation:slideIn 0.3s forwards;";
        f.innerText = `🎉 Mission Complete: +${xpReward} XP`;
        document.body.appendChild(f);
        setTimeout(()=>f.remove(), 4000);
        
        fetchProfile();
    } catch(e) {
        console.error("Failed to apply mission reward", e);
    }
}
