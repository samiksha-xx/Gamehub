import wx
import random
import pygame 
import os     
def get_sound_path(filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, filename)
SOUND_ENABLED = False 

#audio
pygame.mixer.init()
SOUNDS = {
        "click": pygame.mixer.Sound(get_sound_path("click.mp3")),
        "win": pygame.mixer.Sound(get_sound_path("win.mp3")),
        "lose": pygame.mixer.Sound(get_sound_path("lose.mp3")),
        "tie": pygame.mixer.Sound(get_sound_path("tie.mp3")),
        "powerup": pygame.mixer.Sound(get_sound_path("powerup.mp3"))
    }
SOUND_ENABLED = True
def play_sound(name):
    if SOUND_ENABLED and name in SOUNDS:
        SOUNDS[name].play()
    
#COLORS
BABY_PINK = (255, 182, 193)
PURPLE    = (140, 82, 255)
BABY_BLUE = (137, 207, 240)
BLACK     = (0, 0, 0)
WHITE     = (255, 255, 255)

#GAME STATE
user_score = 0
comp_score = 0

# power-up active flags
shield_active = False
double_active = False
reverse_active = False

# cooldown counters 
shield_cd = 0
double_cd = 0
reverse_cd = 0

# round and game controls
round_number = 0           
powerups_used = 0          

#GAME LOGIC
def reset_game():
    global user_score, comp_score
    global round_number, powerups_used
    global shield_cd, double_cd, reverse_cd
    global shield_active, double_active, reverse_active

    user_score = 0
    comp_score = 0
    round_number = 0
    powerups_used = 0

    # clear any active power-ups and cooldowns
    shield_active = double_active = reverse_active = False
    shield_cd = double_cd = reverse_cd = 0

    # update UI
    score.SetLabel("Player: 0   |   Computer: 0")
    sresult.SetLabel("New Game Started! 10 Rounds")
    vsdisp.SetLabel("🤜   vs   🤛")
    panel.Refresh()

def check_game_end():
    if round_number >= 10:
        if user_score > comp_score:
            msg = "🎉 YOU WON THE GAME! 🎉"
        elif comp_score > user_score:
            msg = "💀 COMPUTER WON THE GAME! 💀"
        else:
            msg = "🤝 GAME DRAW! 🤝"
        dlg = wx.MessageDialog(frame, msg, "Game Over", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        reset_game()

def play(user_choice):
    global user_score, comp_score
    global shield_active, double_active, reverse_active
    global shield_cd, double_cd, reverse_cd
    global round_number

    # increment round count at start of the round
    round_number += 1
    emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂"}
    options = ["rock", "paper", "scissors"]
    comp = random.choice(options)

    # determine base outcome
    if user_choice == comp:
        result = "It's a Tie!"
        outcome = "tie"
    elif user_choice == "rock":
        if comp == "scissors":
            result = "You Win! Rock smashes Scissors"
            outcome = "win"
        else:
            result = "You Lose! Paper covers Rock"
            outcome = "lose"
    elif user_choice == "paper":
        if comp == "rock":
            result = "You Win! Paper covers Rock"
            outcome = "win"
        else:
            result = "You Lose! Scissors cuts Paper"
            outcome = "lose"
    elif user_choice == "scissors":
        if comp == "paper":
            result = "You Win! Scissors cuts Paper"
            outcome = "win"
        else:
            result = "You Lose! Rock smashes Scissors"
            outcome = "lose"
    else:
        result = "Invalid move"
        outcome = "tie"

    # APPLY POWER UPS
    # REVERSAL
    if reverse_active:
        play_sound("powerup")
        if outcome == "win":
            outcome = "lose"
            result = "Reversed! You Actually Lose!"
        elif outcome == "lose":
            outcome = "win"
            result = "Reversed! You Actually Win!"
        reverse_active = False
        reverse_cd = 3

    # SHIELD
    if shield_active and outcome == "lose":
        play_sound("powerup")
        outcome = "tie"
        result = "Shield Blocked the Loss! No one scores."
        shield_active = False
        shield_cd = 3
    
    # Check for outcome and play sound before double scoring changes the score
    if outcome == "win":
        play_sound("win")
    elif outcome == "lose":
        play_sound("lose")
    elif outcome == "tie":
        play_sound("tie")

    # DOUBLE ATTACK
    if double_active and outcome == "win":
        user_score += 2
        double_active = False
        double_cd = 3
    else:
        if outcome == "win":
            user_score += 1
        elif outcome == "lose":
            comp_score += 1
    # UPDATE UI
    vsdisp.SetLabel(f"{emojis.get(user_choice, '?')}   vs   {emojis.get(comp, '?')}")
    sresult.SetLabel(f"{result}   (Round {round_number}/10)")
    score.SetLabel(f"Player: {user_score}   |   Computer: {comp_score}")

    # REDUCE COOLDOWNS
    if shield_cd > 0:
        shield_cd -= 1
    if double_cd > 0:
        double_cd -= 1
    if reverse_cd > 0:
        reverse_cd -= 1

    # check if game ended
    check_game_end()
    panel.Layout()

#HANDLERS 
def on_rock(event): 
    play_sound("click")
    play("rock")
def on_paper(event): 
    play_sound("click")
    play("paper")
def on_scissors(event): 
    play_sound("click")
    play("scissors")

#POWER-UPS
def use_shield(event):
    global shield_active, shield_cd, powerups_used

    # total powerup limit check
    if powerups_used >= 2:
        sresult.SetLabel("Limit reached! Only 2 powerups allowed per game.")
        play_sound("click") 
        return
    if shield_cd == 0 and not shield_active:
        shield_active = True
        powerups_used += 1
        sresult.SetLabel("Shield Activated! 🛡")
        play_sound("powerup") 
    elif shield_active:
        sresult.SetLabel("Shield already active this round.")
        play_sound("click") 
    else:
        sresult.SetLabel(f"Shield Cooldown: {shield_cd} rounds")
        play_sound("click") 

def use_double(event):
    global double_active, double_cd, powerups_used

    if powerups_used >= 2:
        sresult.SetLabel("Limit reached! Only 2 powerups allowed per game.")
        play_sound("click") 
        return
    if double_cd == 0 and not double_active:
        double_active = True
        powerups_used += 1
        sresult.SetLabel("Double Attack Activated! ⚡")
        play_sound("powerup") 
    elif double_active:
        sresult.SetLabel("Double Attack already active this round.")
        play_sound("click") 
    else:
        sresult.SetLabel(f"Double Cooldown: {double_cd} rounds")
        play_sound("click") 

def use_reverse(event):
    global reverse_active, reverse_cd, powerups_used

    if powerups_used >= 2:
        sresult.SetLabel("Limit reached! Only 2 powerups allowed per game.")
        play_sound("click") 
        return
    if reverse_cd == 0 and not reverse_active:
        reverse_active = True
        powerups_used += 1
        sresult.SetLabel("Reversal Activated! 🔄")
        play_sound("powerup") 
    elif reverse_active:
        sresult.SetLabel("Reversal already active this round.")
        play_sound("click") 
    else:
        sresult.SetLabel(f"Reversal Cooldown: {reverse_cd} rounds")
        play_sound("click") 

#GUI SETUP
app = wx.App()
frame = wx.Frame(None, title="Rock Paper Scissors", size=(500, 700))
panel = wx.Panel(frame)
panel.SetBackgroundColour(BLACK)
main_sizer = wx.BoxSizer(wx.VERTICAL)

# Title
label_title = wx.StaticText(panel, label="ROCK   PAPER   SCISSORS")
label_title.SetFont(wx.Font(26, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
label_title.SetForegroundColour(PURPLE)
main_sizer.Add(label_title, 0, wx.ALL | wx.CENTER, 30)

# Score
score = wx.StaticText(panel, label="Player: 0   |   Computer: 0")
score.SetFont(wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
score.SetForegroundColour(BABY_BLUE)
main_sizer.Add(score, 0, wx.ALL | wx.CENTER, 15)

# Versus display
vsdisp = wx.StaticText(panel, label="🤜   vs   🤛")
vsdisp.SetFont(wx.Font(44, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
vsdisp.SetForegroundColour(WHITE)
main_sizer.Add(vsdisp, 0, wx.ALL | wx.CENTER, 35)

# Result text
sresult = wx.StaticText(panel, label="Choose your move!")
sresult.SetFont(wx.Font(18, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD))
sresult.SetForegroundColour(PURPLE)
main_sizer.Add(sresult, 0, wx.ALL | wx.CENTER, 20)

# Buttons row
btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

def make_button(text, handler, color):
    btn = wx.Button(panel, label=text, size=(130, 55))
    btn.SetBackgroundColour(color)
    btn.SetForegroundColour(BLACK)
    btn.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
    btn.Bind(wx.EVT_BUTTON, handler)
    return btn

btn_sizer.Add(make_button("ROCK 🪨", on_rock, BABY_PINK), 0, wx.ALL, 10)
btn_sizer.Add(make_button("PAPER 📄", on_paper, PURPLE), 0, wx.ALL, 10)
btn_sizer.Add(make_button("SCISSORS ✂", on_scissors, BABY_BLUE), 0, wx.ALL, 10)
main_sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 25)

# Power-up buttons
power_sizer = wx.BoxSizer(wx.HORIZONTAL)
power_sizer.Add(make_button("SHIELD 🛡", use_shield, BABY_PINK), 0, wx.ALL, 10)
power_sizer.Add(make_button("DOUBLE ⚡", use_double, BABY_BLUE), 0, wx.ALL, 10)
power_sizer.Add(make_button("REVERSE 🔄", use_reverse, PURPLE), 0, wx.ALL, 10)
main_sizer.Add(power_sizer, 0, wx.ALL | wx.CENTER, 10)
panel.SetSizer(main_sizer)
frame.Show()
app.MainLoop()