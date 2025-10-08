function fetchUsers() {
    fetch('http://127.0.0.1:8000/users/')
        .then(response => response.json())
        .then(users => {
            const tbody = document.querySelector('#usersTable tbody');
            tbody.innerHTML = '';
            users.forEach(user => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.email}</td>
                    <td>
                        <button onclick="deleteUser(${user.id})">Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        });
}

document.getElementById('addUserForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const username = document.getElementById('newUsername').value;
    const email = document.getElementById('newEmail').value;
    const password = document.getElementById('newPassword').value;

    fetch('http://127.0.0.1:8000/users/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
    })
    .then(response => response.json())
    .then(result => {
        document.getElementById('userMessage').textContent = 'User added!';
        fetchUsers();
        document.getElementById('addUserForm').reset();
    });
});

function deleteUser(id) {
    fetch(`http://127.0.0.1:8000/users/${id}`, {
        method: 'DELETE'
    })
    .then(response => {
        document.getElementById('userMessage').textContent = 'User deleted!';
        fetchUsers();
    });
}

// Fetch users when the section is shown
document.querySelector('a[onclick="showSection(\'users\')"]').addEventListener('click', fetchUsers);