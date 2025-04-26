// DOM Elements
const itemForm = document.getElementById('item-form');
const nameInput = document.getElementById('name');
const descriptionInput = document.getElementById('description');
const itemsTable = document.getElementById('items-table');

// API URL
const API_URL = 'http://localhost:8080/items';

// Fetch all items
function fetchItems() {
    fetch(API_URL)
        .then(response => response.json())
        .then(items => renderItems(items))
        .catch(error => console.error('Error fetching items:', error));
}

// Create an item
function createItem(item) {
    fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(item)
    })
    .then(response => response.json())
    .then(() => {
        fetchItems();
        nameInput.value = '';
        descriptionInput.value = '';
    })
    .catch(error => console.error('Error creating item:', error));
}

// Update an item
function updateItem(id, item) {
    fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(item)
    })
    .then(response => response.json())
    .then(() => fetchItems())
    .catch(error => console.error('Error updating item:', error));
}

// Delete an item
function deleteItem(id) {
    fetch(`${API_URL}/${id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(() => fetchItems())
    .catch(error => console.error('Error deleting item:', error));
}

// Render items in the table
function renderItems(items) {
    itemsTable.innerHTML = '';
    
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