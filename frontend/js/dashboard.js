const API_BASE = "/api/v1";
let currentUser = localStorage.getItem("finova_user");

async function fetchProfile() {
    if (!currentUser) return;
    try {
        let res = await fetch(`${API_BASE}/user/profile/?username=${currentUser}`);
        if(res.ok) {
            let data = await res.json();
            document.getElementById("level-txt").innerText = `Lvl ${data.level}`;
            document.getElementById("xp-txt").innerText = `${data.xp} XP`;
            document.getElementById("balance-txt").innerText = data.balance;
            
            if(document.getElementById("username-display")) {
                document.getElementById("username-display").innerText = data.username;
            }
            if(document.getElementById("balance-big")) {
                document.getElementById("balance-big").innerText = `₹${data.balance}`;
            }
        }
    } catch(e) {
        console.error("Failed to fetch profile", e);
    }
}
