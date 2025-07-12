import tkinter as tk
from tkinter import ttk  
import socket
import threading
import platform

# --- Constants ---
SERVER = "irc.chat.twitch.tv"
PORT = 6667
NICKNAME = "just_a_viewer_bot"
TOKEN = "oauth:py0i8vdls2a9uiuntiqgqdwviwu566"  # should be in env variable but for testing its constant
CHANNEL = "#k1m6a"

# --- App logic and timer setup---
votes = {"a": set(), "b": set()}
time_left = 30 # 300 seconds for 5 minutes
timer_running = False

# --- UI Setup ---
root = tk.Tk()
root.title("5minutes left to vote!")
root.geometry("600x520")

# --- Style Configuration ---
style = ttk.Style(root)
style.theme_use('clam')

# Detect the operating system
os_name = platform.system()

if os_name == "Darwin": # macOS
    # Use the native macOS theme
    if 'aqua' in style.theme_names(): 
        style.theme_use('aqua')
    else:
        
        style.theme_use('clam')
elif os_name == "Windows":
    
    style.theme_use('clam')
    
elif os_name == "Linux":
    
    style.theme_use('clam')
else:
    # Default fallback 
    style.theme_use('clam')

# General window background
style.configure('TFrame', background='green')

# Label styles
style.configure('Title.TLabel', background='green', foreground='gold', font=("Arial", 24, "bold"))
style.configure('Normal.TLabel', background='green', foreground='white', font=("Arial", 16))
style.configure('Winner.TLabel', background='green', foreground='gold', font=("Arial", 18, "bold"))
style.configure('Loser.TLabel', background='green', foreground='red', font=("Arial", 18, "bold"))

# Button styles
style.configure('Choice.TButton', font=("Arial", 14), width=35, background='navy', foreground='white')
style.map('Choice.TButton',
          background=[('active', 'gold')],
          foreground=[('active', 'black')])

style.configure('Winner.TButton', font=("Arial", 14), width=35, background='gold', foreground='black')
style.configure('Disabled.TButton', font=("Arial", 14), width=35, background='gray', foreground='#ccc')

style.configure('Start.TButton', font=("Arial", 14), width=10, background='green', foreground='white')
style.map('Start.TButton', background=[('active', '#00C000')])

style.configure('Reset.TButton', font=("Arial", 14), width=10, background='red', foreground='white')
style.map('Reset.TButton', background=[('active', '#FF5050')])

# --- UI Widgets ---
main_frame = ttk.Frame(root, style='TFrame')
main_frame.pack(fill="both", expand=True)

title_label = ttk.Label(main_frame, text="5minutes left to vote!", style='Title.TLabel')
title_label.pack(pady=20)

question_label = ttk.Label(main_frame, text="Vote for the star of the show by typing 'a' or 'b' in the Twitch chat!", style='Normal.TLabel', wraplength=550, justify="center")
question_label.pack(pady=10)

winner_label = ttk.Label(main_frame, text="", style='Winner.TLabel')
winner_label.pack(pady=10)

choices_frame = ttk.Frame(main_frame, style='TFrame')
choices_frame.pack(pady=10)

choice_buttons = {}
choices = ["A", "B"]
for choice_char in choices: # Use 'A' and 'B' as choices
    btn = ttk.Button(choices_frame, text=choice_char, style='Choice.TButton')
    btn.pack(pady=5)
    choice_buttons[choice_char.lower()] = btn # Store 'a' and 'b' as keys

timer_label = ttk.Label(main_frame, text=f"Time Left: {time_left}s", style='Normal.TLabel')
timer_label.pack(pady=20)

control_frame = ttk.Frame(main_frame, style='TFrame')
control_frame.pack(pady=10)

# --- Functions ---
def update_buttons():
    total_votes = sum(len(v) for v in votes.values())
    for key, btn in choice_buttons.items(): # Use .items() to get key and button
        count = len(votes[key])
        percentage = (count / total_votes * 100) if total_votes else 0
        original_text = btn.cget("text").split("(")[0].strip()
        btn.config(text=f"{original_text} ({count} votes, {percentage:.1f}%)")

# Connect to Twitch IRC
SERVER = "irc.chat.twitch.tv"
PORT = 6667
NICKNAME = "just_a_viewer_bot"
TOKEN = "oauth:py0i8vdls2a9uiuntiqgqdwviwu566"  # should be in env variable but for testing its constant
CHANNEL = "#k1m6a"

def connect_to_twitch():
    try:
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
                        # Only count votes if timer is running and the message is a valid choice
                        if timer_running and message in votes and not any(username in v for v in votes.values()):
                            votes[message].add(username)
                            root.after(0, update_buttons) # Schedule UI update on main thread
                except Exception as e:
                    print("Error in Twitch thread:", e)
                    break
        threading.Thread(target=loop, daemon=True).start()
    except Exception as e:
        print(f"Could not connect to Twitch: {e}. Running without Twitch connection.")


def start_voting():
    global time_left, timer_running
    if not timer_running: # Only start if not already running
        time_left = 30
        timer_running = True
        winner_label.config(text="") # Clear any previous winner message
        winner_label.configure(style='Winner.TLabel') # Reset winner label style
        timer_label.config(text=f"Time Left: {time_left}s")
        for btn in choice_buttons.values():
            btn.configure(style='Choice.TButton')
            btn.state(['!disabled'])
        update_buttons() # Update button text to show 0 votes
        countdown() # Start the countdown

def reset_voting():
    global time_left, votes, timer_running
    time_left = 30
    timer_running = False
    votes = {"a": set(), "b": set()} # Clear votes
    timer_label.config(text=f"Time Left: {time_left}s")
    winner_label.config(text="") # Clear winner message
    winner_label.configure(style='Winner.TLabel') # Reset winner label style
    # Reset choice buttons to initial state and enable them
    for btn in choice_buttons.values():
        btn.configure(style='Choice.TButton')
        btn.state(['!disabled'])
    update_buttons() # Update button text to reflect 0 votes

def countdown():
    ### Manages the countdown timer for the voting period.
    global time_left, timer_running
    if timer_running: # Only proceed if timer is meant to be running
        timer_label.config(text=f"Time Left: {time_left}s")
        if time_left > 0:
            time_left -= 1
            root.after(1000, countdown) 
        else:
            # Time is up!
            timer_running = False # Stop the timer
            end_question() # Call the function that handles result display

def end_question():
    ### Finalizes the voting process, determines the winner, and updates the UI.
    global timer_running
    timer_running = False # Ensure timer is marked as stopped

    vote_counts = {choice: len(users) for choice, users in votes.items()}
    max_votes = max(vote_counts.values(), default=0)

    # Find all choices tied for max votes
    tied_choices = [k for k, count in vote_counts.items() if count == max_votes and max_votes > 0]

    # Disable all choice buttons regardless of outcome
    for btn in choice_buttons.values():
        btn.state(['disabled'])

    if len(tied_choices) > 1:
        # There is a tie
        tied_text = ", ".join(c.upper() for c in tied_choices)
        winner_label.config(
            text=f"It's a tie between: {tied_text} ({max_votes} votes each)",
            style='Winner.TLabel' # Use the defined style for ties/winners
        )
        # Highlight tied buttons with 'Winner.TButton' style
        for key, btn in choice_buttons.items():
            if key in tied_choices:
                btn.configure(style='Winner.TButton')
            else:
                btn.configure(style='Disabled.TButton') # Disable non-tied
    elif len(tied_choices) == 1:
        # Single winner
        winner_key = tied_choices[0]
        winner_text = f"Winner is {winner_key.upper()} with {max_votes} votes!"
        winner_label.config(text=winner_text, style='Winner.TLabel') # Use the defined style

        for key, btn in choice_buttons.items():
            if key == winner_key:
                btn.configure(style='Winner.TButton') # Apply winner style
            else:
                btn.configure(style='Loser.TButton') # Apply loser style
    else:
        # No votes received at all (max_votes was 0)
        winner_label.config(text="No votes received.", style='Loser.TLabel')
        # All buttons are already disabled above

    print("Voting ended.")


# Control buttons
start_button = ttk.Button(control_frame, text="Start", style='Start.TButton', command=start_voting)
start_button.pack(side="left", padx=10)

reset_button = ttk.Button(control_frame, text="Reset", style='Reset.TButton', command=reset_voting)
reset_button.pack(side="left", padx=10)

# --- Start Application ---
connect_to_twitch()
root.mainloop()