import socket
import threading
import tkinter as tk
from tkinter import Canvas

# Twitch IRC settings
SERVER = "irc.chat.twitch.tv"
PORT = 6667
NICKNAME = "just_a_viewer_bot"
TOKEN = "oauth:py0i8vdls2a9uiuntiqgqdwviwu566"
CHANNEL = "#k1m6a"

votes = {
    "a": set(),
    "b": set(),
    "c": set(),
    "d": set()
}

# GUI Setup
root = tk.Tk()
root.title("Twitch Multi-Vote Tracker (A/B/C/D)")

canvas = Canvas(root, width=500, height=300, bg="black")
canvas.pack(padx=10, pady=10)

label = tk.Label(root, text="", font=("Arial", 14), fg="white", bg="black")
label.pack()

bar_colors = {"a": "red", "b": "blue", "c": "green", "d": "yellow"}
bar_labels = {"a": "A", "b": "B", "c": "C", "d": "D"}

def update_visuals():
    canvas.delete("all")
    total_height = 200
    max_votes = max((len(v) for v in votes.values()), default=1)
    bar_width = 80
    spacing = 30

    sorted_votes = sorted(votes.items(), key=lambda x: len(x[1]), reverse=True)
    label_text = "Leaderboard: " + " | ".join([f"{bar_labels[k]}: {len(v)}" for k, v in sorted_votes])
    label.config(text=label_text)

    for idx, (key, user_set) in enumerate(votes.items()):
        bar_height = (len(user_set) / max_votes) * total_height if max_votes else 0
        x0 = spacing + idx * (bar_width + spacing)
        y0 = total_height - bar_height + 50
        x1 = x0 + bar_width
        y1 = total_height + 50
        canvas.create_rectangle(x0, y0, x1, y1, fill=bar_colors[key])
        canvas.create_text((x0 + x1)//2, y0 - 15, text=f"{bar_labels[key]}: {len(user_set)}", fill="white")

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
                    if message in votes and not any(username in v for v in votes.values()):
                        votes[message].add(username)
                        update_visuals()
            except Exception as e:
                print("Error:", e)
                break

    threading.Thread(target=loop, daemon=True).start()

connect_to_twitch()
root.mainloop()