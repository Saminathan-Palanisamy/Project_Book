document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const response = await fetch('http://127.0.0.1:8000/users/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, email, password })
    });

    const result = await response.json();
    const messageDiv = document.getElementById('registerMessage');

    if (response.ok) {
        messageDiv.style.color = 'green';
        messageDiv.textContent = result.message || 'Registration successful! You can now log in.';
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1000);
        document.getElementById('registerForm').reset();
    } else {
        messageDiv.style.color = 'red';
        messageDiv.textContent = result.detail || 'Registration failed!';
    }
});