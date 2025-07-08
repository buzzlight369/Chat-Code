import tkinter as tk
import socket
import threading
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

SERVER = os.getenv("SERVER")
PORT = int(os.getenv("PORT"))
NICKNAME = os.getenv("NICKNAME")
TOKEN = os.getenv("TOKEN")
CHANNEL = os.getenv("CHANNEL")

votes = {
    "a": set(),
    "b": set(),
}

root = tk.Tk()
root.title("You get to choose the star of the show!")
root.geometry("600x500")
root.configure(bg="midnight blue")

title_label = tk.Label(
    root,
    text="",
    font=("Arial", 24, "bold"),
    fg="gold",
    bg="midnight blue"
)
title_label.pack(pady=20)

question_label = tk.Label(
    root,
    text="You get to choose the star of the show!",
    font=("Arial", 16),
    fg="white",
    bg="midnight blue",
    wraplength=550,
    justify="center"
)
question_label.pack(pady=10)

winner_label = tk.Label(
    root,
    text="",
    font=("Arial", 18, "bold"),
    fg="white",
    bg="midnight blue"
)
winner_label.pack(pady=10)

choices_frame = tk.Frame(root, bg="midnight blue")
choices_frame.pack(pady=10)

choice_buttons = {}
choices = ["A)", "B)"]
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

timer_label = tk.Label(
    root,
    text="Time Left: 30s",
    font=("Arial", 16),
    fg="white",
    bg="midnight blue"
)
timer_label.pack(pady=20)

# Frame to hold control buttons
control_frame = tk.Frame(root, bg="midnight blue")
control_frame.pack(pady=10)

time_left = 30
timer_running = False

def update_buttons():
    total_votes = sum(len(v) for v in votes.values())
    for key, btn in zip(["a", "b"], choice_buttons.values()):
        count = len(votes[key])
        percentage = (count / total_votes * 100) if total_votes else 0
        original_text = btn.cget("text").split("(")[0].strip()
        btn.config(text=f"{original_text} ({count} votes, {percentage:.1f}%)")

def connect_to_twitch():
    sock = socket.socket()
    sock.connect((SERVER, PORT))
    sock.send(f"PASS {TOKEN}\r\n".encode("utf-8"))
    sock.send(f"NICK {NICKNAME}\r\n".encode("utf-8"))
    sock.send(f"JOIN {CHANNEL}\r\n".encode("utf-8"))

    def loop():
        while True:
            try:
                resp = sock.recv(2048).decode("utf-8")
                if resp.startswith("PING"):
                    sock.send("PONG\r\n".encode("utf-8"))
                    continue

                if "PRIVMSG" in resp:
                    username = resp.split("!", 1)[0][1:]
                    message = resp.split("PRIVMSG", 1)[1].split(":", 1)[1].strip().lower()

                    if timer_running and message in votes and not any(username in v for v in votes.values()):
                        votes[message].add(username)
                        root.after(0, update_buttons)

            except Exception as e:
                print("Error:", e)
                break

    threading.Thread(target=loop, daemon=True).start()

def start_voting():
    global time_left, timer_running
    if not timer_running:
        time_left = 30
        timer_running = True
        winner_label.config(text="", fg="white")
        for btn in choice_buttons.values():
            btn.config(state="normal", bg="navy", fg="white")
        update_buttons()
        countdown()

def reset_voting():
    global time_left, votes, timer_running
    time_left = 30
    timer_running = False
    votes = {"a": set(), "b": set()}
    timer_label.config(text=f"Time Left: {time_left}s")
    winner_label.config(text="", fg="white")
    for btn in choice_buttons.values():
        btn.config(state="normal", bg="navy", fg="white")
    update_buttons()

def countdown():
    global time_left, timer_running
    if timer_running:
        timer_label.config(text=f"Time Left: {time_left}s")
        if time_left > 0:
            time_left -= 1
            root.after(1000, countdown)
        else:
            timer_running = False
            end_question()

def end_question():
    winner_key, winner_users = max(votes.items(), key=lambda x: len(x[1]), default=(None, []))
    
    if winner_key:
        winner_text = f"Winner is {winner_key.upper()} with {len(winner_users)} votes!"
        winner_label.config(text=winner_text, fg="gold")

        for key, btn in zip(["a", "b"], choice_buttons.values()):
            if key == winner_key:
                btn.config(bg="gold", fg="black")
            else:
                btn.config(state="disabled", bg="gray", fg="white")
    else:
        winner_label.config(text="No votes received.", fg="red")

    print("Voting ended.")

start_button = tk.Button(
    control_frame,
    text="Start",
    font=("Arial", 14),
    bg="green",
    fg="white",
    width=10,
    command=start_voting
)
start_button.pack(side="left", padx=10)

reset_button = tk.Button(
    control_frame,
    text="Reset",
    font=("Arial", 14),
    bg="red",
    fg="white",
    width=10,
    command=reset_voting
)
reset_button.pack(side="left", padx=10)

connect_to_twitch()
root.mainloop()
