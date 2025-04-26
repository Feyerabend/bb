// DOM Elements
const itemForm = document.getElementById('item-form');
const nameInput = document.getElementById('name');
const descriptionInput = document.getElementById('description');
const itemsTable = document.getElementById('items-table');
const lastRequestEl = document.getElementById('last-request');
const lastResponseEl = document.getElementById('last-response');

// JSON-RPC endpoint
const RPC_ENDPOINT = 'http://localhost:8080/jsonrpc';

// Request ID counter
let requestId = 1;

// Send JSON-RPC request
async function sendRequest(method, params) {
    const request = {
        jsonrpc: '2.0',
        method: method,
        params: params,
        id: requestId++
    };
    
    // Display request
    lastRequestEl.textContent = JSON.stringify(request, null, 2);
    
    try {
        const response = await fetch(RPC_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(request)
        });
        
        const data = await response.json();
        
        // Display response
        lastResponseEl.textContent = JSON.stringify(data, null, 2);
        
        if (data.error) {
            console.error('JSON-RPC error:', data.error);
            return null;
        }
        
        return data.result;
    } catch (error) {
        console.error('Fetch error:', error);
        lastResponseEl.textContent = `Error: ${error.message}`;
        return null;
    }
}

// Fetch all items
async function fetchItems() {
    const items = await sendRequest('item.read', {});
    if (items) {
        renderItems(items);
    }
}

// Create an item
async function createItem(item) {
    const result = await sendRequest('item.create', item);
    if (result) {
        nameInput.value = '';
        descriptionInput.value = '';
        fetchItems();
    }
}

// Update an item
async function updateItem(id, updates) {
    const result = await sendRequest('item.update', {
        id: id,
        updates: updates
    });
    if (result) {
        fetchItems();
    }
}

// Delete an item
async function deleteItem(id) {
    const result = await sendRequest('item.delete', { id: id });
    if (result) {
        fetchItems();
    }
}

// Render items in the table
function renderItems(items) {
    itemsTable.innerHTML = '';
    
    if (!Array.isArray(items)) {
        console.error('Expected array of items, got:', items);
        return;
    }
    
    items.forEach(item => {
        const row = document.createElement('tr');
        row.dataset.id = item.id;
        
        const nameCell = document.createElement('td');
        nameCell.textContent = item.name;
        
        const descCell = document.createElement('td');
        descCell.textContent = item.description || '';
        
        const actionsCell = document.createElement('td');
        
        const editBtn = document.createElement('button');
        editBtn.textContent = 'Edit';
        editBtn.addEventListener('click', () => enableEditMode(row, item));
        
        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.addEventListener('click', () => deleteItem(item.id));
        
        actionsCell.appendChild(editBtn);
        actionsCell.appendChild(deleteBtn);
        
        row.appendChild(nameCell);
        row.appendChild(descCell);
        row.appendChild(actionsCell);
        
        itemsTable.appendChild(row);
    });
}

// Enable edit mode for a row
function enableEditMode(row, item) {
    row.classList.add('edit-mode');
    
    const cells = row.querySelectorAll('td');
    
    // Create input for name
    const nameInput = document.createElement('input');
    nameInput.type = 'text';
    nameInput.value = item.name;
    cells[0].innerHTML = '';
    cells[0].appendChild(nameInput);
    
    // Create input for description
    const descInput = document.createElement('input');
    descInput.type = 'text';
    descInput.value = item.description || '';
    cells[1].innerHTML = '';
    cells[1].appendChild(descInput);
    
    // Replace buttons
    cells[2].innerHTML = '';
    
    const saveBtn = document.createElement('button');
    saveBtn.textContent = 'Save';
    saveBtn.addEventListener('click', () => {
        const updatedItem = {
            name: nameInput.value,
            description: descInput.value
        };
        updateItem(item.id, updatedItem);
    });
    
    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = 'Cancel';
    cancelBtn.addEventListener('click', () => fetchItems());
    
    cells[2].appendChild(saveBtn);
    cells[2].appendChild(cancelBtn);
}

// Add item form submit handler
itemForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const newItem = {
        name: nameInput.value,
        description: descriptionInput.value
    };
    
    createItem(newItem);
});

// Load items when page loads
document.addEventListener('DOMContentLoaded', fetchItems);
