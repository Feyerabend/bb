import tkinter as tk
from tkinter import messagebox

# Sample product data
products = [
    {"id": 1, "name": "Product A", "price": 10, "description": "Description of Product A"},
    {"id": 2, "name": "Product B", "price": 20, "description": "Description of Product B"},
    {"id": 3, "name": "Product C", "price": 30, "description": "Description of Product C"},
]

# Function to view product details
def view_product(product):
    messagebox.showinfo("Product Details", f"Name: {product['name']}\n"
                                           f"Price: ${product['price']}\n"
                                           f"Description: {product['description']}")

# Create main window
root = tk.Tk()
root.title("Product Listing")

# Create and display product widgets
for product in products:
    frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    frame.pack(pady=5, padx=10, fill="x")

    label = tk.Label(frame, text=f"{product['name']} - ${product['price']}")
    label.pack(side="left", padx=10)

    button = tk.Button(frame, text="View Details", command=lambda p=product: view_product(p))
    button.pack(side="right")

root.mainloop()
