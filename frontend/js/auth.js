const API_URL = "/api/v1";

async function login() {
    const user = document.getElementById("username").value;
    const pass = document.getElementById("password").value;
    const errObj = document.getElementById("login-error");

    if(!user || !pass) {
        errObj.innerText = "Please fill both fields.";
        return;
    }

    try {
        let res = await fetch(`${API_URL}/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({username: user, password: pass})
        });
        
        if (res.ok) {
            let data = await res.json();
            // Store simple mock session
            localStorage.setItem("finova_user", data.profile.username);
            window.location.href = "dashboard.html";
        } else {
            // Attempt register
            let resReg = await fetch(`${API_URL}/auth/register/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({username: user, password: pass})
            });

            if (resReg.ok) {
                // Auto login after register
                localStorage.setItem("finova_user", user);
                window.location.href = "dashboard.html";
            } else {
                errObj.innerText = "Invalid credentials or username taken.";
            }
        }
    } catch (e) {
        errObj.innerText = "Server error. Is the backend running?";
    }
}

function logout() {
    localStorage.removeItem("finova_user");
    window.location.href = "index.html";
}

function authCheck() {
    if(!localStorage.getItem("finova_user")) {
        window.location.href = "index.html";
    }
}
