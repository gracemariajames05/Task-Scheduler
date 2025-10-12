# rewards.py
import random
from plyer import notification

MOTIVATIONS = [
    "Great job! Keep the momentum going! 💪",
    "You’re crushing it! 🌟",
    "Task completed! Take a short break 😌",
    "Another one done! You got this! 🚀",
    "Awesome work! Keep smashing those goals! 🎯"
]

def reward_user(points, message=None):
    """Show a desktop notification + optional console print (no terminal UI)"""
    msg = message or random.choice(MOTIVATIONS)
    full = f"{msg} — Total points: {points}"
    try:
        notification.notify(title="Rewards", message=full, timeout=6)
    except Exception:
        # fallback: nothing (no terminal output)
        pass
