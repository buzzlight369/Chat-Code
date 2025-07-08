import tkinter as tk
import socket
import threading

# Twitch IRC settings
SERVER = "irc.chat.twitch.tv"
PORT = 6667
NICKNAME = "just_a_viewer_bot"
TOKEN = "oauth:py0i8vdls2a9uiuntiqgqdwviwu566"     # << your hard-coded token
CHANNEL = "#k1m6a"

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
    text="Choose between the options!",
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

# ✅ WINNER LABEL
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
choices = ["A) Paris", "B) Berlin",]
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

def update_buttons():
    total_votes = sum(len(v) for v in votes.values())
    for key, btn in zip(["a", "b", "c", "d"], choice_buttons.values()):
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

                    if message in votes and not any(username in v for v in votes.values()):
                        votes[message].add(username)
                        root.after(0, update_buttons)

            except Exception as e:
                print("Error:", e)
                break

    threading.Thread(target=loop, daemon=True).start()

time_left = 30

def countdown():
    global time_left
    timer_label.config(text=f"Time Left: {time_left}s")
    if time_left > 0:
        time_left -= 1
        root.after(1000, countdown)
    else:
        end_question()

def end_question():
    winner_key, winner_users = max(votes.items(), key=lambda x: len(x[1]), default=(None, []))
    
    if winner_key:
        winner_text = f"Winner is {winner_key.upper()} with {len(winner_users)} votes!"
        winner_label.config(text=winner_text, fg="gold")

        for key, btn in zip(["a", "b",], choice_buttons.values()):
            if key == winner_key:
                btn.config(bg="gold", fg="black")
            else:
                btn.config(state="disabled", bg="gray", fg="white")
    else:
        winner_label.config(text="No votes received.", fg="red")

    print("Voting ended.")

connect_to_twitch()
countdown()
root.mainloop()
