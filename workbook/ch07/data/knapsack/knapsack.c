<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Knapsack Problem Visualization</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        table {
            border-collapse: collapse;
            margin: 20px 0;
            width: 100%;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #f2f2f2;
        }
        .highlight {
            background-color: #ffffcc;
        }
        .selected {
            background-color: #d4edda;
        }
        .controls {
            margin-bottom: 20px;
        }
        .visualization {
            display: flex;
            margin-top: 20px;
        }
        .knapsack {
            border: 2px solid #333;
            padding: 10px;
            min-height: 200px;
            width: 200px;
            margin-right: 20px;
        }
        .items {
            display: flex;
            flex-wrap: wrap;
        }
        .item {
            border: 1px solid #333;
            padding: 5px;
            margin: 5px;
            cursor: pointer;
            text-align: center;
        }
        .item.in-knapsack {
            background-color: #d4edda;
        }
        button {
            padding: 8px 16px;
            margin-right: 10px;
            cursor: pointer;
        }
        #capacity-display {
            margin-top: 10px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>Knapsack Problem Visualization</h1>
    
    <div class="controls">
        <h2>Controls</h2>
        <div>
            <label for="capacity">Knapsack Capacity:</label>
            <input type="number" id="capacity" min="1" value="50">
        </div>
        <div>
            <button id="add-item">Add Item</button>
            <button id="solve">Solve</button>
            <button id="reset">Reset</button>
        </div>
    </div>
    
    <div class="items-container">
        <h2>Available Items</h2>
        <table id="items-table">
            <thead>
                <tr>
                    <th>Item</th>
                    <th>Value</th>
                    <th>Weight</th>
                    <th>Value/Weight</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody id="items-body">
                <tr>
                    <td>Item 1</td>
                    <td><input type="number" class="item-value" value="60" min="1"></td>
                    <td><input type="number" class="item-weight" value="10" min="1"></td>
                    <td class="value-weight-ratio">6.0</td>
                    <td><button class="remove-item">Remove</button></td>
                </tr>
                <tr>
                    <td>Item 2</td>
                    <td><input type="number" class="item-value" value="100" min="1"></td>
                    <td><input type="number" class="item-weight" value="20" min="1"></td>
                    <td class="value-weight-ratio">5.0</td>
                    <td><button class="remove-item">Remove</button></td>
                </tr>
                <tr>
                    <td>Item 3</td>
                    <td><input type="number" class="item-value" value="120" min="1"></td>
                    <td><input type="number" class="item-weight" value="30" min="1"></td>
                    <td class="value-weight-ratio">4.0</td>
                    <td><button class="remove-item">Remove</button></td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <div class="visualization">
        <div>
            <h2>Knapsack</h2>
            <div class="knapsack" id="knapsack">
                <!-- Items will be added here -->
            </div>
            <div id="capacity-display">Capacity: 50/50</div>
            <div id="total-value">Total Value: 0</div>
        </div>
        <div>
            <h2>Solution</h2>
            <div id="solution">
                <p>Click "Solve" to find the optimal solution.</p>
            </div>
        </div>
    </div>
    
    <div class="dp-table-container" style="display: none;">
        <h2>Dynamic Programming Table</h2>
        <table id="dp-table">
            <!-- DP table will be generated here -->
        </table>
    </div>
    
    <script>
        // Initialize variables
        let nextItemId = 4;
        let currentWeight = 0;
        let currentValue = 0;
        let selectedItems = [];
        
        // Get DOM elements
        const capacityInput = document.getElementById('capacity');
        const addItemButton = document.getElementById('add-item');
        const solveButton = document.getElementById('solve');
        const resetButton = document.getElementById('reset');
        const itemsTable = document.getElementById('items-table');
        const itemsBody = document.getElementById('items-body');
        const knapsack = document.getElementById('knapsack');
        const capacityDisplay = document.getElementById('capacity-display');
        const totalValueDisplay = document.getElementById('total-value');
        const solutionDiv = document.getElementById('solution');
        const dpTableContainer = document.querySelector('.dp-table-container');
        const dpTable = document.getElementById('dp-table');
        
        // Update value-weight ratios
        function updateRatios() {
            const rows = itemsBody.querySelectorAll('tr');
            rows.forEach(row => {
                const value = parseInt(row.querySelector('.item-value').value);
                const weight = parseInt(row.querySelector('.item-weight').value);
                const ratio = value / weight;
                row.querySelector('.value-weight-ratio').textContent = ratio.toFixed(1);
            });
        }
        
        // Add event listeners to update ratios when values change
        itemsBody.addEventListener('change', updateRatios);
        
        // Add item button click handler
        addItemButton.addEventListener('click', () => {
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td>Item ${nextItemId}</td>
                <td><input type="number" class="item-value" value="50" min="1"></td>
                <td><input type="number" class="item-weight" value="10" min="1"></td>
                <td class="value-weight-ratio">5.0</td>
                <td><button class="remove-item">Remove</button></td>
            `;
            itemsBody.appendChild(newRow);
            nextItemId++;
            updateRatios();
        });
        
        // Remove item button click handler
        itemsBody.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-item')) {
                e.target.closest('tr').remove();
            }
        });
        
        // Solve button click handler
        solveButton.addEventListener('click', () => {
            // Get capacity and items
            const capacity = parseInt(capacityInput.value);
            const items = getItems();
            
            // Solve using dynamic programming
            const [maxValue, solution, dpMatrix] = knapsackDP(capacity, items);
            
            // Display solution
            displaySolution(maxValue, solution, items);
            
            // Display DP table
            displayDPTable(dpMatrix, capacity, items);
        });
        
        // Reset button click handler
        resetButton.addEventListener('click', () => {
            knapsack.innerHTML = '';
            currentWeight = 0;
            currentValue = 0;
            selectedItems = [];
            updateCapacityDisplay();
            solutionDiv.innerHTML = '<p>Click "Solve" to find the optimal solution.</p>';
            dpTableContainer.style.display = 'none';
        });
        
        // Get items from the table
        function getItems() {
            const items = [];
            const rows = itemsBody.querySelectorAll('tr');
            rows.forEach((row, index) => {
                const value = parseInt(row.querySelector('.item-value').value);
                const weight = parseInt(row.querySelector('.item-weight').value);
                items.push({ id: index + 1, value, weight });
            });
            return items;
        }
        
        // Knapsack DP algorithm
        function knapsackDP(capacity, items) {
            const n = items.length;
            const dp = Array(n + 1).fill().map(() => Array(capacity + 1).fill(0));
            
            for (let i = 1; i <= n; i++) {
                for (let w = 0; w <= capacity; w++) {
                    if (items[i-1].weight <= w) {
                        dp[i][w] = Math.max(
                            items[i-1].value + dp[i-1][w - items[i-1].weight],
                            dp[i-1][w]
                        );
                    } else {
                        dp[i][w] = dp[i-1][w];
                    }
                }
            }
            
            // Backtrack to find selected items
            const selected = [];
            let w = capacity;
            for (let i = n; i > 0 && w > 0; i--) {
                if (dp[i][w] !== dp[i-1][w]) {
                    selected.push(items[i-1]);
                    w -= items[i-1].weight;
                }
            }
            
            return [dp[n][capacity], selected, dp];
        }
        
        // Display solution
        function displaySolution(maxValue, solution, items) {
            // Clear knapsack
            knapsack.innerHTML = '';
            currentWeight = 0;
            currentValue = 0;
            selectedItems = solution;
            
            // Add selected items to knapsack
            solution.forEach(item => {
                const itemElement = document.createElement('div');
                itemElement.classList.add('item', 'in-knapsack');
                itemElement.textContent = `Item ${item.id} (V:${item.value}, W:${item.weight})`;
                knapsack.appendChild(itemElement);
                
                currentWeight += item.weight;
                currentValue += item.value;
            });
            
            // Update capacity display
            updateCapacityDisplay();
            
            // Update solution text
            solutionDiv.innerHTML = `
                <p>Optimal solution found:</p>
                <p>Maximum value: ${maxValue}</p>
                <p>Selected items: ${solution.map(item => `Item ${item.id}`).join(', ')}</p>
                <p>Total weight: ${solution.reduce((sum, item) => sum + item.weight, 0)}</p>
            `;
        }
        
        // Display DP table
        function displayDPTable(dp, capacity, items) {
            dpTableContainer.style.display = 'block';
            dpTable.innerHTML = '';
            
            // Create header row
            const headerRow = document.createElement('tr');
            headerRow.innerHTML = '<th>Item / Capacity</th>';
            for (let w = 0; w <= capacity; w++) {
                headerRow.innerHTML += `<th>${w}</th>`;
            }
            dpTable.appendChild(headerRow);
            
            // Create data rows
            for (let i = 0; i <= items.length; i++) {
                const row = document.createElement('tr');
                if (i === 0) {
                    row.innerHTML = '<td>0 (no items)</td>';
                } else {
                    row.innerHTML = `<td>Item ${items[i-1].id} (V:${items[i-1].value}, W:${items[i-1].weight})</td>`;
                }
                
                for (let w = 0; w <= capacity; w++) {
                    const cell = document.createElement('td');
                    cell.textContent = dp[i][w];
                    
                    // Highlight cells that represent the solution path
                    if (i > 0 && w >= items[i-1].weight && 
                        dp[i][w] === items[i-1].value + dp[i-1][w - items[i-1].weight]) {
                        cell.classList.add('highlight');
                    }
                    
                    row.appendChild(cell);
                }
                dpTable.appendChild(row);
            }
        }
        
        // Update capacity display
        function updateCapacityDisplay() {
            const capacity = parseInt(capacityInput.value);
            capacityDisplay.textContent = `Capacity: ${currentWeight}/${capacity}`;
            totalValueDisplay.textContent = `Total Value: ${currentValue}`;
        }
        
        // Initialize
        updateRatios();
        updateCapacityDisplay();
    </script>
</body>
</html>