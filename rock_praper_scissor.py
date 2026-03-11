#rock paper scissor game
import random
def rps_game(user_choice):
    choice=['rock','paper','scissor']
    random_choice=random.choice(choice)
    print("Computer choice:",random_choice)
    if user_choice==random_choice:
        return "match draw"
    elif(user_choice=='rock' and random_choice=='scissor') or (user_choice=='paper' and random_choice=='rock') or (user_choice=='scissor' and random_choice=='paper'):
        return "you win"
    else:
        return "you lose"
user_choice=input("enter your choice (rock/paper/scissor): ").lower()
if user_choice in ['rock','paper','scissor']:
    print(rps_game(user_choice))
else:
    print("invalid choice, please choose rock, paper or scissor")
    