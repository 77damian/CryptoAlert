const API_URL = ""; // Relative url since it's served from same domain

async function fetchCoins() {
    try {
        const response = await fetch(`${API_URL}/coins/`);
        const coins = await response.json();
        renderCoins(coins);
        populateCoinSelect(coins);
    } catch (error) {
        console.error("Error fetching coins:", error);
    }
}

async function fetchUsers() {
    try {
        const response = await fetch(`${API_URL}/users/`);
        const users = await response.json();
        renderUsers(users);
    } catch (error) {
        console.error("Error fetching users:", error);
    }
}

async function fetchPrices() {
    try {
        await fetch(`${API_URL}/fetch-prices`, { method: 'POST' });
        alert('Updated prices in the database!');
    } catch (error) {
        console.error("Error fetching prices:", error);
    }
}

async function deleteCoin(id) {
    if(confirm('Are you sure you want to delete?')) {
        await fetch(`${API_URL}/coins/${id}`, { method: 'DELETE' });
        fetchCoins();
    }
}

async function deleteUser(id) {
    if(confirm('Are you sure you want to delete the user?')) {
        await fetch(`${API_URL}/users/${id}`, { method: 'DELETE' });
        fetchUsers();
    }
}

function renderCoins(coins) {
    const tableBody = document.querySelector('#coins-table tbody');
    const adminTableBody = document.querySelector('#admin-coins-table tbody');
    tableBody.innerHTML = '';
    adminTableBody.innerHTML = '';
    
    coins.forEach(coin => {
        // Dashboard table
        tableBody.innerHTML += `
            <tr>
                <td>${coin.name}</td>
                <td><span class="badge bg-secondary">${coin.symbol}</span></td>
                <td>
                    <strong>${coin.latest_price ? '$' + coin.latest_price.toFixed(2) : 'No data'}</strong>
                </td>
            </tr>
        `;
        
        // Admin table
        adminTableBody.innerHTML += `
            <tr>
                <td>${coin.id}</td>
                <td>${coin.symbol}</td>
                <td>${coin.coingecko_id}</td>
                <td><button class="btn btn-sm btn-danger" onclick="deleteCoin(${coin.id})">Delete</button></td>
            </tr>
        `;
    });
}

function renderUsers(users) {
    const tableBody = document.querySelector('#admin-users-table tbody');
    tableBody.innerHTML = '';
    users.forEach(user => {
        tableBody.innerHTML += `
            <tr>
                <td>${user.id}</td>
                <td>${user.email}</td>
                <td><button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})">Delete</button></td>
            </tr>
        `;
    });
}

function populateCoinSelect(coins) {
    const select = document.getElementById('alert-coin-id');
    select.innerHTML = '';
    coins.forEach(coin => {
        select.innerHTML += `<option value="${coin.id}">${coin.name} (${coin.symbol})</option>`;
    });
}

// Add Coin Form
document.getElementById('add-coin-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        symbol: document.getElementById('coin-symbol').value,
        name: document.getElementById('coin-name').value,
        coingecko_id: document.getElementById('coin-cg-id').value
    };
    
    await fetch(`${API_URL}/coins/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    e.target.reset();
    fetchCoins();
});

// Add User Form
document.getElementById('add-user-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        email: document.getElementById('user-email').value
    };
    
    await fetch(`${API_URL}/users/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    e.target.reset();
    fetchUsers();
});

// ----------------------------------------------------
// ALERTS - Fetching, adding, and deleting logic
// ----------------------------------------------------

async function fetchAlerts() {
    try {
        const response = await fetch(`${API_URL}/alerts/`);
        const alerts = await response.json();
        renderAlerts(alerts);
    } catch (error) {
        console.error("Error fetching alerts:", error);
    }
}

async function deleteAlert(id) {
    if(confirm('Are you sure you want to delete this alert?')) {
        await fetch(`${API_URL}/alerts/${id}`, { method: 'DELETE' });
        fetchAlerts();
    }
}

function renderAlerts(alerts) {
    const tableBody = document.querySelector('#alerts-table tbody');
    tableBody.innerHTML = '';
    
    // Mapping technical names to English (for readability)
    const conditionMap = {
        'price_below': 'Price below',
        'price_above': 'Price above',
        'change_24h_below': '24h drop below',
        'change_24h_above': '24h rise above'
    };

    alerts.forEach(alert => {
        const conditionText = conditionMap[alert.condition] || alert.condition;
        const coinName = alert.coin ? alert.coin.symbol : `ID: ${alert.coin_id}`;
        
        tableBody.innerHTML += `
            <tr>
                <td>${alert.id}</td>
                <td>${alert.user_id}</td>
                <td><span class="badge bg-secondary">${coinName}</span></td>
                <td>${conditionText}</td>
                <td><strong>${alert.target_value}</strong></td>
                <td><button class="btn btn-sm btn-danger" onclick="deleteAlert(${alert.id})">Delete</button></td>
            </tr>
        `;
    });
}

// Handling the add alert form
document.getElementById('add-alert-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        user_id: parseInt(document.getElementById('alert-user-id').value),
        coin_id: parseInt(document.getElementById('alert-coin-id').value),
        condition: document.getElementById('alert-condition').value,
        target_value: parseFloat(document.getElementById('alert-target-value').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/alerts/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            e.target.reset();
            fetchAlerts(); // Refresh the alerts list
            alert("New alert added!");
        } else {
            const errorData = await response.json();
            alert("Error: " + errorData.detail);
        }
    } catch (error) {
        console.error("Error creating alert:", error);
    }
});

// Init - runs after page load
window.onload = () => {
    fetchCoins();
    fetchUsers();
    fetchAlerts();
};
