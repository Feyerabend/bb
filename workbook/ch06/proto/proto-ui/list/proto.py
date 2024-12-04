import tkinter as tk

def show_message():
    label.config(text="Hello, this is a prototype!")

# simple GUI window
root = tk.Tk()
root.title("Prototype Window")

# button and label
button = tk.Button(root, text="Click me", command=show_message)
button.pack(pady=20)

label = tk.Label(root, text="")
label.pack(pady=20)

root.mainloop()
