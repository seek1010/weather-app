import tkinter as tk

root = tk.Tk()
root.title("Minimal Tkinter Test")
root.geometry("500x300")
root.configure(bg="lightblue")

label = tk.Label(root, text="If you see this window → Tkinter works!\n\nClose me to continue.", font=("Arial", 14), bg="lightblue")
label.pack(pady=80)

print("Window should be visible now...")

root.mainloop()