// Finance AI App JavaScript

// Utility: Get registered users from localStorage
function getUsers() {
    const users = localStorage.getItem('users');
    return users ? JSON.parse(users) : [];
}

function saveUsers(users) {
    localStorage.setItem('users', JSON.stringify(users));
}

// Register a new user
function registerUser() {
    const username = document.getElementById('registerUsername').value.trim();
    const password = document.getElementById('registerPassword').value;
    const msg = document.getElementById('registerMsg');
    msg.textContent = '';
    if (!username || !password) {
        msg.textContent = 'Please enter a username and password.';
        return;
    }
    const users = getUsers();
    if (users.find(u => u.username === username)) {
        msg.textContent = 'Username already exists. Please choose another.';
        return;
    }
    // Simple password encoding (not secure, demonstration only)
    const encodedPassword = btoa(password);
    users.push({ username, password: encodedPassword });
    saveUsers(users);
    msg.classList.remove('text-danger');
    msg.classList.add('text-success');
    msg.textContent = 'Registration successful. You can now log in.';
    // Clear inputs
    document.getElementById('registerUsername').value = '';
    document.getElementById('registerPassword').value = '';
}

// Login existing user
function loginUser() {
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;
    const msg = document.getElementById('loginMsg');
    msg.textContent = '';
    if (!username || !password) {
        msg.textContent = 'Please enter your username and password.';
        return;
    }
    const users = getUsers();
    const user = users.find(u => u.username === username);
    if (!user || user.password !== btoa(password)) {
        msg.textContent = 'Invalid credentials. Please try again.';
        return;
    }
    // Set current user and show dashboard
    localStorage.setItem('currentUser', username);
    document.getElementById('loginUsername').value = '';
    document.getElementById('loginPassword').value = '';
    showDashboard();
}

function logoutUser() {
    localStorage.removeItem('currentUser');
    // Hide dashboard and show auth section
    document.getElementById('dashboardSection').style.display = 'none';
    document.getElementById('authSection').style.display = 'block';
    document.getElementById('logoutBtn').style.display = 'none';
}

function getTransactions(username) {
    const data = localStorage.getItem(`transactions_${username}`);
    return data ? JSON.parse(data) : [];
}

function saveTransactions(username, transactions) {
    localStorage.setItem(`transactions_${username}`, JSON.stringify(transactions));
}

// Categorize transaction based on description and type
function categorizeTransaction(description, type) {
    if (type === 'income') {
        return 'Income';
    }
    const desc = description.toLowerCase();
    const categories = {
        'Food & Groceries': ['grocery', 'supermarket', 'food', 'restaurant', 'cafe'],
        'Housing': ['rent', 'mortgage', 'apartment', 'house'],
        'Utilities': ['electricity', 'water', 'gas', 'internet', 'phone', 'utility'],
        'Transportation': ['bus', 'train', 'uber', 'taxi', 'fuel', 'petrol', 'diesel'],
        'Entertainment': ['movie', 'netflix', 'spotify', 'concert', 'game'],
        'Healthcare': ['doctor', 'pharmacy', 'hospital', 'medicine'],
        'Shopping': ['clothes', 'amazon', 'shopping', 'mall'],
        'Education': ['tuition', 'school', 'course', 'college', 'book'],
        'Travel': ['flight', 'hotel', 'airbnb', 'travel'],
        'Subscription': ['subscription', 'membership', 'plan']
    };
    for (const [category, keywords] of Object.entries(categories)) {
        if (keywords.some(kw => desc.includes(kw))) {
            return category;
        }
    }
    return 'Other';
}

// Save a new transaction
function saveTransaction() {
    const username = localStorage.getItem('currentUser');
    if (!username) return;
    const dateInput = document.getElementById('transDate');
    const descriptionInput = document.getElementById('transDescription');
    const amountInput = document.getElementById('transAmount');
    const typeInput = document.getElementById('transType');
    const msg = document.getElementById('transMsg');
    msg.textContent = '';
    let date = dateInput.value;
    // If date is empty, default to today's date (ISO format) so the form isn't blocked by date input issues
    if (!date) {
        const today = new Date();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        const year = today.getFullYear();
        date = `${year}-${month}-${day}`;
    }
    const description = descriptionInput.value.trim();
    const amount = parseFloat(amountInput.value);
    const type = typeInput.value;
    if (!description || !amount || isNaN(amount)) {
        msg.classList.remove('text-success');
        msg.classList.add('text-danger');
        msg.textContent = 'Please fill in all fields correctly.';
        return;
    }
    const category = categorizeTransaction(description, type);
    const transactions = getTransactions(username);
    transactions.push({ date, description, amount, type, category });
    saveTransactions(username, transactions);
    // Clear form
    dateInput.value = '';
    descriptionInput.value = '';
    amountInput.value = '';
    typeInput.value = 'expense';
    msg.classList.remove('text-danger');
    msg.classList.add('text-success');
    msg.textContent = 'Transaction saved successfully!';
    updateDashboard();
}

let summaryChartInstance = null;

// Update dashboard UI
function updateDashboard() {
    const username = localStorage.getItem('currentUser');
    if (!username) return;
    const transactions = getTransactions(username);
    const body = document.getElementById('transactionsBody');
    body.innerHTML = '';
    // Populate table
    transactions.sort((a, b) => new Date(b.date) - new Date(a.date));
    transactions.forEach(tx => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${tx.date}</td><td>${tx.description}</td><td>${tx.type.charAt(0).toUpperCase() + tx.type.slice(1)}</td><td>${tx.category}</td><td class='text-end'>${tx.amount.toFixed(2)}</td>`;
        body.appendChild(row);
    });
    // Calculate totals by category
    const totals = {};
    let totalIncome = 0;
    let totalExpense = 0;
    transactions.forEach(tx => {
        const cat = tx.category;
        totals[cat] = (totals[cat] || 0) + (tx.type === 'income' ? tx.amount : tx.amount);
        if (tx.type === 'income') totalIncome += tx.amount;
        else totalExpense += tx.amount;
    });
    // Prepare data for chart (expenses only for categories excluding Income)
    const expenseCategories = [];
    const expenseAmounts = [];
    Object.keys(totals).forEach(cat => {
        if (cat !== 'Income') {
            expenseCategories.push(cat);
            expenseAmounts.push(totals[cat]);
        }
    });
    // Destroy existing chart
    if (summaryChartInstance) {
        summaryChartInstance.destroy();
    }
    const ctx = document.getElementById('summaryChart').getContext('2d');
    summaryChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: expenseCategories,
            datasets: [{
                data: expenseAmounts,
                backgroundColor: expenseCategories.map(() => getRandomColor()),
                hoverOffset: 4
            }]
        },
        options: {
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    // Update summary text
    const summaryText = document.getElementById('summaryText');
    let text = `<strong>Total Income:</strong> ₹${totalIncome.toFixed(2)}<br>`;
    text += `<strong>Total Expense:</strong> ₹${totalExpense.toFixed(2)}<br>`;
    if (expenseAmounts.length > 0) {
        // Find highest expense category
        let maxIndex = 0;
        expenseAmounts.forEach((val, idx) => { if (val > expenseAmounts[maxIndex]) maxIndex = idx; });
        const highestCat = expenseCategories[maxIndex];
        const highestVal = expenseAmounts[maxIndex];
        const percent = totalExpense > 0 ? ((highestVal / totalExpense) * 100).toFixed(1) : 0;
        text += `<strong>Highest Expense:</strong> ${highestCat} (₹${highestVal.toFixed(2)}, ${percent}% of expenses)`;
    }
    summaryText.innerHTML = text;
}

// Generate a random pastel color for charts
function getRandomColor() {
    const r = Math.floor((Math.random() * 156) + 100);
    const g = Math.floor((Math.random() * 156) + 100);
    const b = Math.floor((Math.random() * 156) + 100);
    return `rgb(${r},${g},${b})`;
}

// Show dashboard and hide auth section
function showDashboard() {
    const username = localStorage.getItem('currentUser');
    if (!username) return;
    document.getElementById('currentUserDisplay').textContent = username;
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('dashboardSection').style.display = 'block';
    document.getElementById('logoutBtn').style.display = 'block';
    updateDashboard();
}

// On page load, check if a user session exists
window.onload = function() {
    const username = localStorage.getItem('currentUser');
    if (username) {
        showDashboard();
    }
};
