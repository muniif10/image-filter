from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

def enumerate_directory(directory_path):
    items = []
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}
    for root, dirs, files in os.walk(directory_path):
        for name in files:
            if os.path.splitext(name)[1].lower() in valid_extensions:
                items.append(os.path.join(root, name))
    return items

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        global contents
        contents = enumerate_directory(directory)
        if contents:
            load_image()
        else:
            messagebox.showinfo("No Images Found", "No images found in the selected directory.")

# Initialize main window
root = tk.Tk()
root.geometry("800x450")
root.title("Image Viewer")

# Set a style for the buttons
style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=6, relief="flat", background="#f0f0f0", foreground="#333")
style.map("TButton", background=[("active", "#d9d9d9")])
style.configure("Rounded.TButton", relief="flat", padding=6)

# Select Dir
button_select_dir = ttk.Button(root, text="Select Directory", command=select_directory, style="TButton")
button_select_dir.pack(side=tk.TOP)

# Set up the canvas
canvas = tk.Canvas(root, bg="lightgray")
canvas.pack(fill=tk.BOTH, expand=True)

# Image display variables
count = 0
padding = 20
contents = []
images_to_delete = []
original_img = None

# Function to resize and update the image on the canvas
def resize_image(canvas_width, canvas_height):
    global tk_img, original_img
    if original_img is None:
        return

    max_width = canvas_width - 2 * padding
    max_height = canvas_height - 2 * padding
    original_width, original_height = original_img.size

    scale = min(max_width / original_width, max_height / original_height)
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    resized_img = original_img.resize((new_width, new_height), Image.LANCZOS)
    tk_img = ImageTk.PhotoImage(resized_img)
    canvas.itemconfig(image_id, image=tk_img)
    canvas.coords(image_id, (canvas_width // 2, canvas_height // 2))

# Function to load and display the current image
def load_image():
    global tk_img, original_img
    if contents:
        original_img = Image.open(contents[count])
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        resize_image(canvas_width, canvas_height)
        update_delete_button()

# Function to toggle the deletion status of the current image without dialogs
def toggle_delete():
    current_image = contents[count]
    if current_image in images_to_delete:
        images_to_delete.remove(current_image)
    else:
        images_to_delete.append(current_image)
    update_delete_button()

# Update delete button color based on deletion status
def update_delete_button():
    if contents[count] in images_to_delete:
        button_delete.config(text="Marked for Deletion", style="DeleteSelected.TButton")
    else:
        button_delete.config(text="Delete", style="Delete.TButton")

# Function to apply deletion of images
def apply_deletion():
    global images_to_delete, contents, count
    if not images_to_delete:
        messagebox.showinfo("No Images to Delete", "There are no images marked for deletion.")
        return

    confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected images?")
    if confirm:
        for image in images_to_delete:
            try:
                os.remove(image)
                contents.remove(image)
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete {os.path.basename(image)}: {e}")

        images_to_delete.clear()
        if contents:
            load_image()
        else:
            messagebox.showinfo("No Images Left", "No images to display.")
            root.destroy()

# Image navigation functions
def increment():
    global count
    count = (count + 1) % len(contents)
    load_image()

def decrement():
    global count
    count = (count - 1) % len(contents)
    load_image()

# Create the canvas image holder
tk_img = ImageTk.PhotoImage(Image.new("RGB", (1, 1)))  # Placeholder image
image_id = canvas.create_image(0, 0, image=tk_img, anchor=tk.CENTER)

# Bind the canvas resize event to resize the image dynamically
canvas.bind("<Configure>", lambda event: resize_image(event.width, event.height))

# Keyboard bindings
root.bind("<KeyPress-Right>", lambda event: increment())
root.bind("<KeyPress-Left>", lambda event: decrement())
root.bind("<KeyPress-q>", lambda event: root.destroy())
root.bind("<KeyPress-d>", lambda event: toggle_delete())

# Set custom styles for delete buttons
style.configure("Delete.TButton", background="#f66", relief="flat", font=("Arial", 12, "bold"))
style.configure("DeleteSelected.TButton", background="#6f6", relief="flat", font=("Arial", 12, "bold"))

# Buttons with rounded corners and custom styles
button_next = ttk.Button(root, text="Next", command=increment, style="Rounded.TButton")
button_next.pack(side=tk.RIGHT, padx=10, pady=10)

button_prev = ttk.Button(root, text="Previous", command=decrement, style="Rounded.TButton")
button_prev.pack(side=tk.LEFT, padx=10, pady=10)

button_delete = ttk.Button(root, text="Delete", command=toggle_delete, style="Delete.TButton")
button_delete.pack(side=tk.BOTTOM, pady=10)

button_apply = ttk.Button(root, text="Apply Deletion", command=apply_deletion, style="TButton")
button_apply.pack(side=tk.BOTTOM, pady=5)

# Run the application
root.mainloop()
