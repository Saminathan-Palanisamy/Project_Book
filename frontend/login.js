document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('http://127.0.0.1:8000/users/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });

    const result = await response.json();
    const messageDiv = document.getElementById('loginMessage');

    if (response.ok) {
    messageDiv.style.color = 'green';
    messageDiv.textContent = result.message || 'Login successful!';
    // Redirect to dashboard after a short delay
    setTimeout(() => {
        window.location.href = 'dashboard.html';
    }, 1000); // 1 second delay for user to see the message
} else {
    messageDiv.style.color = 'red';
    messageDiv.textContent = result.detail || 'Login failed!';
    }
});