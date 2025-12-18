import wx
import random
import pygame
import os
import sys 

try:
    file = __file__
except NameError:
    file = getattr(sys, 'argv', [''])[0]

def get_sound_path(filename):
    base_dir = os.path.dirname(os.path.abspath(file))
    return os.path.join(base_dir, filename)

SOUND_ENABLED = False
SOUNDS = {}

try:
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    SOUNDS = {
        "click": pygame.mixer.Sound(get_sound_path("click.mp3")),
        "win": pygame.mixer.Sound(get_sound_path("win.mp3")),
        "lose": pygame.mixer.Sound(get_sound_path("lose.mp3")),
        "tie": pygame.mixer.Sound(get_sound_path("tie.mp3")),
        "powerup": pygame.mixer.Sound(get_sound_path("powerup.mp3"))
    }
    SOUND_ENABLED = True
except Exception:
    SOUND_ENABLED = False
    pass

def play_sound(name):
    if SOUND_ENABLED and name in SOUNDS:
        try:
            SOUNDS[name].play()
        except:
            pass

#Colors
BABY_PINK = (255, 182, 193)
PURPLE    = (140, 82, 255)
BABY_BLUE = (137, 207, 240)
BLACK     = (0, 0, 0)
WHITE     = (255, 255, 255)


app = wx.App()
frame = wx.Frame(None, title="🎮 Game Hub", size=(520, 760))
panel = wx.Panel(frame)
panel.SetBackgroundColour(BLACK)
main_sizer = wx.BoxSizer(wx.VERTICAL)

menu_panel = wx.Panel(panel)
menu_panel.SetBackgroundColour(BLACK)
menu_sizer = wx.BoxSizer(wx.VERTICAL)

menu_title = wx.StaticText(menu_panel, label="🎮 GAME MENU 🎮")
menu_title.SetFont(wx.Font(28, wx.FONTFAMILY_DEFAULT,
                           wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
menu_title.SetForegroundColour(PURPLE)

menu_sizer.Add(menu_title, 0, wx.ALL | wx.CENTER, 40)

def menu_btn(text, handler):
    b = wx.Button(menu_panel, label=text, size=(300, 60))
    b.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT,
                      wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
    b.Bind(wx.EVT_BUTTON, handler)
    return b

def open_bowling_game(e):
    play_sound("click")
    try:
        BowlingFrame(frame)
    except NameError:
        wx.MessageBox("Bowling Game class is missing.", "Error", wx.OK | wx.ICON_ERROR)

def open_ttt(e):
    play_sound("click")
    try:
        TicTacToe(frame)
    except NameError:
        wx.MessageBox("TicTacToe class is missing.", "Error", wx.OK | wx.ICON_ERROR)

menu_sizer.Add(menu_btn("Rock Paper Scissors", lambda e: show_rps()),
                0, wx.ALL | wx.CENTER, 20)
menu_sizer.Add(menu_btn("Bowling Game", lambda e: open_bowling_game(e)),
                0, wx.ALL | wx.CENTER, 20)
menu_sizer.Add(menu_btn("Tic Tac Toe", lambda e: open_ttt(e)),
                0, wx.ALL | wx.CENTER, 20)

menu_panel.SetSizer(menu_sizer)

user_score = 0
comp_score = 0
round_number = 0
POWERUP_LIMIT = 2
powerups_used = 0 

shield_active = False
double_active = False
reverse_active = False

shield_cd = 0 
double_cd = 0 
reverse_cd = 0 

def check_game_end():
    if round_number >= 10:
        if user_score > comp_score:
            msg = "🎉 YOU WON THE GAME! 🎉"
            play_sound("win")
        elif comp_score > user_score:
            msg = "💀 COMPUTER WON THE GAME! 💀"
            play_sound("lose")
        else:
            msg = "🤝 GAME DRAW! 🤝"
            play_sound("tie")
            
        dlg = wx.MessageDialog(frame, msg, "Game Over", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        reset_game()
        return True
    return False

def reset_game():
    global user_score, comp_score
    global round_number, powerups_used
    global shield_cd, double_cd, reverse_cd
    global shield_active, double_active, reverse_active

    user_score = 0
    comp_score = 0
    round_number = 0
    powerups_used = 0

    shield_active = double_active = reverse_active = False
    shield_cd = double_cd = reverse_cd = 0

    score.SetLabel("Player: 0 | Computer: 0")
    sresult.SetLabel("New Game Started! 10 Rounds")
    vsdisp.SetLabel("🤜    vs    🤛")
    frame.Layout()

def play(choice):
    global user_score, comp_score, round_number
    global shield_active, double_active, reverse_active
    global shield_cd, double_cd, reverse_cd

    if round_number >= 10:
        check_game_end()
        play_sound("click")
        return

    round_number += 1
    options = ["rock", "paper", "scissors"]
    comp = random.choice(options)
    emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂"}

    # Determine base outcome
    if choice == comp:
        outcome = "tie"
    elif (choice == "rock" and comp == "scissors") or \
          (choice == "paper" and comp == "rock") or \
          (choice == "scissors" and comp == "paper"):
        outcome = "win"
    else:
        outcome = "lose"

    #APPLY POWER-UPS
    double_points = False

    if reverse_active:
        play_sound("powerup")
        if outcome == "win":
            outcome = "lose"
        elif outcome == "lose":
            outcome = "win"
        reverse_active = False
        reverse_cd = 3
    
    if shield_active and outcome == "lose":
        play_sound("powerup")
        outcome = "tie" 
        shield_active = False
        shield_cd = 3

    if outcome == "win":
        if double_active:
            user_score += 2
            double_points = True
            double_active = False
            double_cd = 3
        else:
            user_score += 1
        play_sound("win")
    elif outcome == "lose":
        comp_score += 1
        play_sound("lose")
    else:
        play_sound("tie")

    #UPDATE UI
    vsdisp.SetLabel(f"{emojis[choice]}    vs    {emojis[comp]}")
    score.SetLabel(f"Player: {user_score} | Computer: {comp_score}")
    
    result_msg = ""
    if reverse_cd == 3:
        result_msg += "REVERSED! "
    if shield_cd == 3:
        result_msg += "SHIELD BLOCK! "
    if double_points:
        result_msg += "DOUBLE SCORE! "
        
    if outcome == "win":
        result_msg += "You Win!"
    elif outcome == "lose":
        result_msg += "You Lose!"
    else:
        result_msg += "It's a Tie!"
        
    sresult.SetLabel(f"{result_msg} (Round {round_number}/10)")

    #REDUCE COOLDOWNS
    if shield_cd > 0: shield_cd -= 1
    if double_cd > 0: double_cd -= 1
    if reverse_cd > 0: reverse_cd -= 1
    
    check_game_end()
    frame.Layout() 


#POWER-UP HANDLERS
def use_powerup(powerup_name):
    global shield_active, double_active, reverse_active
    global shield_cd, double_cd, reverse_cd, powerups_used
    
    if round_number >= 10:
        sresult.SetLabel("Game over! Start a new game.")
        play_sound("click")
        return

    if powerups_used >= POWERUP_LIMIT:
        sresult.SetLabel(f"Limit reached! Only {POWERUP_LIMIT} powerups allowed per game.")
        play_sound("click")
        return
        
    if powerup_name == "shield":
        if shield_cd == 0 and not shield_active:
            shield_active = True
            powerups_used += 1
            sresult.SetLabel("Shield Activated! 🛡 (Next move is protected)")
            play_sound("powerup")
        elif shield_active:
            sresult.SetLabel("Shield already active this round.")
            play_sound("click")
        else:
            sresult.SetLabel(f"Shield Cooldown: {shield_cd} rounds")
            play_sound("click")
            
    elif powerup_name == "double":
        if double_cd == 0 and not double_active:
            double_active = True
            powerups_used += 1
            sresult.SetLabel("Double Attack Activated! ⚡ (Next win gets 2 points)")
            play_sound("powerup")
        elif double_active:
            sresult.SetLabel("Double Attack already active this round.")
            play_sound("click")
        else:
            sresult.SetLabel(f"Double Cooldown: {double_cd} rounds")
            play_sound("click")
            
    elif powerup_name == "reverse":
        if reverse_cd == 0 and not reverse_active:
            reverse_active = True
            powerups_used += 1
            sresult.SetLabel("Reversal Activated! 🔄 (Next result is flipped)")
            play_sound("powerup")
        elif reverse_active:
            sresult.SetLabel("Reversal already active this round.")
            play_sound("click")
        else:
            sresult.SetLabel(f"Reversal Cooldown: {reverse_cd} rounds")
            play_sound("click")
    frame.Layout()

rps_panel = wx.Panel(panel)
rps_panel.SetBackgroundColour(BLACK)
rps_sizer = wx.BoxSizer(wx.VERTICAL)

title = wx.StaticText(rps_panel, label="ROCK PAPER SCISSORS")
title.SetFont(wx.Font(24, wx.FONTFAMILY_DEFAULT,
                      wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
title.SetForegroundColour(PURPLE)

score = wx.StaticText(rps_panel, label="Player: 0 | Computer: 0")
score.SetForegroundColour(BABY_BLUE)
score.SetFont(wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

vsdisp = wx.StaticText(rps_panel, label="🤜    vs    🤛")
vsdisp.SetFont(wx.Font(44, wx.FONTFAMILY_DEFAULT,
                      wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
vsdisp.SetForegroundColour(WHITE)

sresult = wx.StaticText(rps_panel, label="Choose your move 👇 (10 Rounds)")
sresult.SetForegroundColour(PURPLE)
sresult.SetFont(wx.Font(18, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD))

def rps_btn(text, handler, color, size=(140, 50)):
    b = wx.Button(rps_panel, label=text, size=size)
    b.SetBackgroundColour(color)
    b.SetForegroundColour(BLACK)
    b.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT,
                      wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
    b.Bind(wx.EVT_BUTTON, handler)
    return b

# RPS SIZER LAYOUT
rps_sizer.Add(title, 0, wx.ALL | wx.CENTER, 20)
rps_sizer.Add(score, 0, wx.ALL | wx.CENTER, 10)
rps_sizer.Add(vsdisp, 0, wx.ALL | wx.CENTER, 20)
rps_sizer.Add(sresult, 0, wx.ALL | wx.CENTER, 10)

# 1. Standard Moves
moves = wx.BoxSizer(wx.HORIZONTAL)
moves.Add(rps_btn("🪨 ROCK", lambda e: play("rock"), BABY_PINK), 1, wx.ALL, 5)
moves.Add(rps_btn("📄 PAPER", lambda e: play("paper"), BABY_BLUE), 1, wx.ALL, 5)
moves.Add(rps_btn("✂ SCISSORS", lambda e: play("scissors"), PURPLE), 1, wx.ALL, 5)
rps_sizer.Add(moves, 0, wx.CENTER | wx.TOP, 15)

# 2. Power-up Buttons
power_ups = wx.BoxSizer(wx.HORIZONTAL)
power_ups.Add(rps_btn("SHIELD 🛡", lambda e: use_powerup("shield"), BABY_PINK, size=(140, 40)), 1, wx.ALL, 5)
power_ups.Add(rps_btn("DOUBLE ⚡", lambda e: use_powerup("double"), BABY_BLUE, size=(140, 40)), 1, wx.ALL, 5)
power_ups.Add(rps_btn("REVERSE 🔄", lambda e: use_powerup("reverse"), PURPLE, size=(140, 40)), 1, wx.ALL, 5)
rps_sizer.Add(power_ups, 0, wx.CENTER | wx.TOP, 20)
rps_sizer.Add(wx.StaticText(rps_panel, label=f"Power-ups Limit: {POWERUP_LIMIT} uses per 10 rounds."), 0, wx.CENTER | wx.TOP, 5)


# 3. Game Control Buttons
control_btns = wx.BoxSizer(wx.HORIZONTAL)
back_btn = wx.Button(rps_panel, label="⬅ Back to Menu")
back_btn.Bind(wx.EVT_BUTTON, lambda e: show_menu())
control_btns.Add(back_btn, 1, wx.ALL, 5)

new_game_btn = wx.Button(rps_panel, label="🔁 New Game")
new_game_btn.Bind(wx.EVT_BUTTON, lambda e: reset_game())
control_btns.Add(new_game_btn, 1, wx.ALL, 5)

rps_sizer.Add(control_btns, 0, wx.CENTER | wx.EXPAND | wx.TOP, 20)

rps_panel.SetSizer(rps_sizer)

class BowlingFrame(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="Bowling Game", size=(500, 600))
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(BABY_BLUE)

        self.ball_x = 250
        self.ball_y = 480
        self.ball_moving = False
        self.score = 0

        self.pins = []
        self.reset_pins()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.animate_ball)
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)

        self.score_text = wx.StaticText(self.panel, label="🎯 Score: 0", pos=(20, 520))
        roll_btn = wx.Button(self.panel, label="🎳 ROLL", pos=(210, 520))
        roll_btn.Bind(wx.EVT_BUTTON, self.roll)
        
        back_btn_bowling = wx.Button(self.panel, label="Close", pos=(400, 520))
        back_btn_bowling.Bind(wx.EVT_BUTTON, lambda e: self.Destroy())

        self.Show()

    def reset_pins(self):
        self.pins.clear()
        for r in range(4):
            for c in range(r + 1):
                self.pins.append([230 + c * 22 - r * 11, 120 + r * 22, False])

    def roll(self, event):
        if not self.ball_moving:
            play_sound("click")
            self.ball_moving = True
            self.ball_y = 480
            self.timer.Start(15)

    def animate_ball(self, event):
        self.ball_y -= 8
        if self.ball_y <= 160:
            self.hit_pins()
            self.timer.Stop()
            self.ball_moving = False
            self.ball_y = 480
        self.panel.Refresh()

    def hit_pins(self):
        knocked = 0
        for pin in self.pins:
            if not pin[2] and random.choice([True, False]):
                pin[2] = True
                knocked += 1
        self.score += knocked
        self.score_text.SetLabel(f"🎯 Score: {self.score}")
        if knocked > 0:
            play_sound("win")

    def on_paint(self, event):
        dc = wx.PaintDC(self.panel)
        dc.SetBrush(wx.Brush(wx.Colour(210, 180, 140)))
        dc.DrawRectangle(100, 50, 300, 450)
        dc.SetBrush(wx.Brush(WHITE))
        for x, y, fallen in self.pins:
            if not fallen:
                dc.DrawRectangle(x, y, 10, 25)
        dc.SetBrush(wx.Brush(BLACK))
        dc.DrawCircle(self.ball_x, self.ball_y, 15)

#Tic Tac Toe Class
class TicTacToe(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="Tic Tac Toe", size=(360, 420))
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(BLACK)

        self.board = [""] * 9
        self.buttons = []

        grid = wx.GridSizer(3, 3, 5, 5)

        for i in range(9):
            b = wx.Button(self.panel, label="", size=(100, 100))
            b.SetFont(wx.Font(28, wx.FONTFAMILY_DEFAULT,
                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            b.Bind(wx.EVT_BUTTON, lambda e, i=i: self.player_move(i))
            self.buttons.append(b)
            grid.Add(b, 0, wx.EXPAND)

        self.status = wx.StaticText(self.panel, label="Your Turn (X)")
        self.status.SetForegroundColour(WHITE)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.ALL | wx.CENTER, 20)
        sizer.Add(self.status, 0, wx.ALL | wx.CENTER, 10)
        
        back_btn_ttt = wx.Button(self.panel, label="Close")
        back_btn_ttt.Bind(wx.EVT_BUTTON, lambda e: self.Destroy())
        sizer.Add(back_btn_ttt, 0, wx.ALL | wx.CENTER, 10)

        self.panel.SetSizer(sizer)
        self.Show()

    def player_move(self, i):
        if self.board[i] == "":
            self.board[i] = "X"
            self.buttons[i].SetLabel("X")
            play_sound("click")

            if self.check_win("X"):
                self.status.SetLabel("🎉 You Win!")
                play_sound("win")
                self.disable()
                return

            self.computer_move()

    def computer_move(self):
        empty = [i for i in range(9) if self.board[i] == ""]
        if not empty:
            self.status.SetLabel("😐 Tie!")
            play_sound("tie")
            self.disable()
            return

        i = random.choice(empty)
        self.board[i] = "O"
        self.buttons[i].SetLabel("O")

        if self.check_win("O"):
            self.status.SetLabel("💻 Computer Wins!")
            play_sound("lose")
            self.disable()

    def check_win(self, p):
        wins = [(0,1,2),(3,4,5),(6,7,8),
                (0,3,6),(1,4,7),(2,5,8),
                (0,4,8),(2,4,6)]
        return any(self.board[a]==self.board[b]==self.board[c]==p for a,b,c in wins)

    def disable(self):
        for b in self.buttons:
            b.Disable()

def show_menu():
    play_sound("click")
    reset_game()
    rps_panel.Hide()
    menu_panel.Show()
    panel.Layout()

def show_rps():
    play_sound("click")
    reset_game() 
    menu_panel.Hide()
    rps_panel.Show()
    panel.Layout()

main_sizer.Add(menu_panel, 1, wx.EXPAND)
main_sizer.Add(rps_panel, 1, wx.EXPAND)

panel.SetSizer(main_sizer)
rps_panel.Hide() 
frame.Show()
app.MainLoop()