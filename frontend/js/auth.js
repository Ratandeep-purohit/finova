const API_URL = "http://127.0.0.1:8000/api/v1";

async function login() {
    const user = document.getElementById("username").value;
    const pass = document.getElementById("password").value;
    const errObj = document.getElementById("login-error");

    if(!user || !pass) {
        errObj.innerText = "Please provide both username and password.";
        return;
    }

    try {
        let res = await fetch(`${API_URL}/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({username: user, password: pass})
        });
        
        let data = await res.json();
        
        if (res.ok) {
            localStorage.setItem("finova_user", data.profile.username);
            window.location.href = "dashboard.html";
        } else {
            errObj.innerText = data.error || "Invalid credentials.";
        }
    } catch (e) {
        errObj.innerText = "Server error. Is the backend running?";
    }
}

async function register() {
    const user = document.getElementById("reg-username").value;
    const pass = document.getElementById("reg-password").value;
    const conf = document.getElementById("reg-confirm").value;
    const email = document.getElementById("reg-email").value;
    const phone = document.getElementById("reg-phone").value;
    const errObj = document.getElementById("reg-error");

    if (!user || !pass || !conf) {
        errObj.innerText = "Username and password are required.";
        return;
    }

    if (pass !== conf) {
        errObj.innerText = "Passwords do not match.";
        return;
    }

    if (!email && !phone) {
        errObj.innerText = "At least an Email or a Phone Number is required.";
        return;
    }

    try {
        let res = await fetch(`${API_URL}/auth/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: user, 
                password: pass,
                email: email,
                phone_number: phone
            })
        });

        let data = await res.json();

        if (res.ok) {
            // Auto login after successful register
            localStorage.setItem("finova_user", user);
            window.location.href = "dashboard.html";
        } else {
            errObj.innerText = data.error || "Error creating account.";
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
