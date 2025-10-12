# rewards.py
import random

# List of motivational messages
MOTIVATIONS = [
    "Great job! Keep the momentum going! 🤗",
    "You’re crushing it! 🌟",
    "Task completed! Time for a short break 🍵",
    "Another one done! You got this! 🚀",
    "Awesome work! Keep smashing those goals! 🎯"
]

def reward_user(points):
    """
    Call this function after completing a task.
    points: total points after completion
    """
    message = random.choice(MOTIVATIONS)
    print(f"\n🎉 {message} — Total points: {points}\n")
