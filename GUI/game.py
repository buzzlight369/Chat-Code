import tkinter as tk
from tkinter import ttk

# Create the main window
root = tk.Tk()
root.title("chatgame")
root.geometry("600x400")
root.configure(bg="midnight blue")

# Title Label
title_label = tk.Label(
    root,
    text="game for chat",
    font=("Arial", 24, "bold"),
    fg="gold",
    bg="midnight blue"
)
title_label.pack(pady=20)

# Question Label
question_label = tk.Label(
    root,
    text="What is the capital of France?",
    font=("Arial", 16),
    fg="white",
    bg="midnight blue",
    wraplength=550,
    justify="center"
)
question_label.pack(pady=10)

# Frame for choices
choices_frame = tk.Frame(root, bg="midnight blue")
choices_frame.pack(pady=10)

# Four answer buttons
choice_buttons = {}
choices = ["A) Paris", "B) Berlin", "C) Rome", "D) Madrid"]

for choice in choices:
    btn = tk.Button(
        choices_frame,
        text=choice,
        font=("Arial", 14),
        width=30,
        bg="navy",
        fg="white",
        activebackground="gold",
        activeforeground="black"
    )
    btn.pack(pady=5)
    choice_buttons[choice] = btn

# Timer label
timer_label = tk.Label(
    root,
    text="Time Left: 30s",
    font=("Arial", 16),
    fg="white",
    bg="midnight blue"
)
timer_label.pack(pady=20)

# Lifeline buttons (optional)
lifeline_frame = tk.Frame(root, bg="midnight blue")
lifeline_frame.pack(pady=10)

lifelines = ["50:50", "Ask the Audience", "Phone a Friend"]
for lifeline in lifelines:
    btn = tk.Button(
        lifeline_frame,
        text=lifeline,
        font=("Arial", 12),
        width=15,
        bg="dark green",
        fg="white"
    )
    btn.pack(side="left", padx=10)

root.mainloop()