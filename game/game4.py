import random
import sys
import os

# Import speak from backend
try:
    from backend.TextToSpeech import speak
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from backend.TextToSpeech import speak

def start_game():
    choices = ["rock", "paper", "scissors"]
    
    welcome_msg = "Welcome to Rock, Paper, Scissors!"
    print(welcome_msg)
    speak(welcome_msg)
    
    player_score = 0
    computer_score = 0
    
    while True:
        print(f"\nScore: You {player_score} - {computer_score} Computer")
        speak(f"The score is {player_score} to {computer_score}")
        
        prompt = "Enter rock, paper, or scissors (or 'quit' to stop): "
        print(prompt)
        speak("Choose rock, paper, or scissors")
        
        user_choice = input().lower().strip()
        
        if user_choice == 'quit':
            break
        
        if user_choice not in choices:
            msg = "Invalid choice. Please try again."
            print(msg)
            speak(msg)
            continue
            
        computer_choice = random.choice(choices)
        
        msg = f"Computer chose {computer_choice}."
        print(msg)
        speak(msg)
        
        if user_choice == computer_choice:
            msg = "It's a tie!"
        elif (user_choice == "rock" and computer_choice == "scissors") or \
             (user_choice == "paper" and computer_choice == "rock") or \
             (user_choice == "scissors" and computer_choice == "paper"):
            msg = "You win this round!"
            player_score += 1
        else:
            msg = "Computer wins this round!"
            computer_score += 1
            
        print(msg)
        speak(msg)
        
    final_msg = f"Final Score - You: {player_score}, Computer: {computer_score}. Thanks for playing!"
    print(f"\n{final_msg}")
    speak(final_msg)

if __name__ == "__main__":
    start_game()
