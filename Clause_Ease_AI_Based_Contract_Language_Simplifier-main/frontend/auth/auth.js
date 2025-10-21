const API_BASE_URL = 'http://localhost:5000/api';
let isLoginMode = false;

function showMessage(message, isError = false) {
    const msgElement = document.getElementById('auth-message');
    if (msgElement) {
        msgElement.textContent = message;
        msgElement.className = 'message ' + (isError ? 'error' : 'success');
        msgElement.style.display = 'block';
    }
}

function clearMessage() {
    const msgElement = document.getElementById('auth-message');
    if (msgElement) {
        msgElement.style.display = 'none';
        msgElement.className = 'message';
        msgElement.textContent = '';
    }
}

function showRegister() {
    isLoginMode = false;
    
    document.getElementById('auth-title').textContent = 'Create Your Account';
    document.getElementById('auth-subtitle').textContent = 'Get started with ClauseEase AI today';
    document.getElementById('submit-btn').textContent = 'Create Account';
    
    document.getElementById('username-group').style.display = 'flex';
    document.getElementById('confirm-password-group').style.display = 'flex';
    
    document.getElementById('username').required = true;
    document.getElementById('confirm-password').required = true;
    document.getElementById('password').setAttribute('autocomplete', 'new-password');
    
    document.getElementById('registerBtn').classList.add('active');
    document.getElementById('loginBtn').classList.remove('active');
    
    document.getElementById('authForm').reset();
    clearMessage();
    window.location.hash = '';
}

function showLogin() {
    isLoginMode = true;
    
    document.getElementById('auth-title').textContent = 'Sign In';
    document.getElementById('auth-subtitle').textContent = 'Access your contract simplification tools';
    document.getElementById('submit-btn').textContent = 'Sign In';
    
    document.getElementById('username-group').style.display = 'none';
    document.getElementById('confirm-password-group').style.display = 'none';
    
    document.getElementById('username').required = false;
    document.getElementById('confirm-password').required = false;
    document.getElementById('password').setAttribute('autocomplete', 'current-password');
    
    document.getElementById('loginBtn').classList.add('active');
    document.getElementById('registerBtn').classList.remove('active');
    
    document.getElementById('authForm').reset();
    clearMessage();
    window.location.hash = 'login';
}

function handleFormSubmit(event) {
    event.preventDefault();
    
    if (isLoginMode) {
        handleLogin(event);
    } else {
        handleRegister(event);
    }
}

window.addEventListener('DOMContentLoaded', function() {
    if (window.location.hash === '#login') {
        showLogin();
    } else {
        showRegister();
    }
});

async function handleLogin(event) {
    event.preventDefault();
    clearMessage();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;

    if (!email || !password) {
        showMessage('Please fill in all fields', true);
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('username', data.username);

            showMessage('Login successful! Redirecting...');

            setTimeout(() => {
                window.location.href = '../landing/index.html';
            }, 1000);
        } else {
            showMessage(data.message || 'Login failed', true);
        }
    } catch (error) {
        showMessage('Connection error. Please try again.', true);
        console.error('Login error:', error);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    clearMessage();

    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (!username || !email || !password || !confirmPassword) {
        showMessage('Please fill in all fields', true);
        return;
    }

    if (username.length < 3) {
        showMessage('Username must be at least 3 characters', true);
        return;
    }

    if (password.length < 6) {
        showMessage('Password must be at least 6 characters', true);
        return;
    }

    if (password !== confirmPassword) {
        showMessage('Passwords do not match', true);
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showMessage('Please enter a valid email address', true);
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('Registration successful! You can now sign in.');

            setTimeout(() => {
                showLogin();
            }, 2000);
        } else {
            showMessage(data.message || 'Registration failed', true);
        }
    } catch (error) {
        showMessage('Connection error. Please try again.', true);
        console.error('Register error:', error);
    }
}
