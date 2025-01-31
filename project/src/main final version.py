import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk, ImageSequence
import random
import string
import pygame
import os

# Initialize pygame for sound
pygame.mixer.init()

# Load sound effects
SOUND_PATH = os.path.join(os.path.dirname(__file__))
with open(os.path.join(SOUND_PATH, "victory.wav"), 'rb') as victory_file:
    correct_sound = pygame.mixer.Sound(victory_file)
with open(os.path.join(SOUND_PATH, "defeat.wav"), 'rb') as defeat_file:
    wrong_sound = pygame.mixer.Sound(defeat_file)

# Global variables
root = None
word_pressed = ''
previous = [0, 0]
route = [0, 0]
current_words = []
found_words = []
grid = []
buttons = []
check_labels = []
score = 0
computer_score = 0
wrong_attempts = 0
max_attempts = 5
time_left = 180
is_vs_ai = False
game_active = False
size = 12
timer_label = None
attempts_label = None
score_label = None
ai_score_label = None
welcome_frame = None
frame1 = None
frame2 = None
frame3 = None
name_entry = None
category_var = None
difficulty_var = None
vs_ai_var = None
player_name = ""
current_category = ""
current_difficulty = ""
gif_label = None

def load_categories():
    """Load word categories from files"""
    categories = {}
    base_path = os.path.join(os.path.dirname(__file__), "files")
    
    for category in ['animals', 'fruits', 'places','sports','colors']:
        try:
            with open(os.path.join(base_path, f"{category}.txt"), 'r') as f:
                words = [word.strip().upper() for word in f.readlines() if word.strip()]
                categories[category] = words
        except FileNotFoundError:
            messagebox.showerror("Error", f"Could not load {category}.txt")
            categories[category] = []
    
    return categories

def create_header():
    """Create game header"""
    header_frame = tk.Frame(root)
    header_frame.pack(fill=tk.X, side=tk.TOP)
    
    tk.Label(header_frame, text='Word Search Game',
            font=('Helvetica', 23, 'bold'),
            fg='blue').pack(expand=True, fill=tk.X, pady=12)

def create_footer():
    """Create game footer"""
    footer_frame = tk.Frame(root)
    footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=12)
    
    tk.Label(footer_frame, text='Team Error 404').pack(expand=True, fill=tk.X)

def button_press(x, y):
    """Handle button press event"""
    global word_pressed, previous, route
    
    if not game_active:
        return
    
    if len(word_pressed) == 0:
        previous = [x, y]
        word_pressed = grid[x][y]
        buttons[x][y].configure(bg='yellow', fg='#255059')
    
    elif (len(word_pressed) == 1 and
          (x - previous[0])**2 <= 1 and
          (y - previous[1])**2 <= 1 and
          [x, y] != previous):
        word_pressed += grid[x][y]
        buttons[x][y].configure(bg='yellow', fg='#255059')
        route = [x - previous[0], y - previous[1]]
        previous = [x, y]
    
    elif (len(word_pressed) > 1 and
          x - previous[0] == route[0] and
          y - previous[1] == route[1]):
        word_pressed += grid[x][y]
        buttons[x][y].configure(bg='yellow', fg='#255059')
        previous = [x, y]

def colour_word(valid):
    """Color the selected word"""
    global route
    
    route[0] *= -1
    route[1] *= -1
    
    for i in range(len(word_pressed)):
        x = previous[0] + i * route[0]
        y = previous[1] + i * route[1]
        
        if valid:
            buttons[x][y].config(bg='#535edb', fg='white')
        else:
            buttons[x][y].config(bg='#255059', fg='white')

def check_word():
    """Check if selected word is valid"""
    global word_pressed, wrong_attempts, score, game_active
    
    if not game_active:
        return
    
    if word_pressed in current_words and word_pressed not in found_words:
        # Word found
        found_words.append(word_pressed)
        score += len(word_pressed)
        score_label.config(text=f"Score: {score}")
        
        # Update display
        for label in check_labels:
            if label['text'] == word_pressed:
                label.configure(font=('Helvetica', 1),
                              fg='#f0f0f0', bg='#f0f0f0')
        
        # Color word
        colour_word(True)
        pygame.mixer.Sound.play(correct_sound)
        
        # Computer's turn
        if is_vs_ai:
            root.after(1000, computer_turn)
        
        # Check for game end
        if len(found_words) == len(current_words):
            game_over(True)
    
    else:
        # Wrong word
        wrong_attempts += 1
        attempts_label.config(
            text=f"Attempts Left: {max_attempts - wrong_attempts}")
        
        colour_word(False)
        pygame.mixer.Sound.play(wrong_sound)
        
        if wrong_attempts >= max_attempts:
            game_over(False)
    
    # Reset selection
    word_pressed = ''
    previous[0] = previous[1] = 0

def computer_turn():
    """AI opponent's turn"""
    global computer_score, found_words
    
    if not game_active:
        return
    
    # Get unfound words
    available_words = [word for word in current_words if word not in found_words]
    if not available_words:
        return
        
    # AI randomly selects a word
    selected_word = random.choice(available_words)
    found_words.append(selected_word)
    computer_score += len(selected_word)
    
    # Update AI score display
    if 'ai_score_label' in globals():
        ai_score_label.config(text=f"AI Score: {computer_score}")
    
    # Update word list display
    for label in check_labels:
        if label['text'] == selected_word:
            label.configure(font=('Helvetica', 1),
                          fg='#f0f0f0', bg='#f0f0f0')
    
    # Find and color the word in the grid
    word_found = False
    for i in range(size):
        for j in range(size):
            # Check all 8 directions
            directions = [
                (0, 1),   # right
                (1, 0),   # down
                (1, 1),   # diagonal down-right
                (-1, 1),  # diagonal up-right
                (0, -1),  # left
                (-1, 0),  # up
                (-1, -1), # diagonal up-left
                (1, -1)   # diagonal down-left
            ]
            
            for di, dj in directions:
                # Check if word fits in this direction
                if (0 <= i + di * (len(selected_word)-1) < size and 
                    0 <= j + dj * (len(selected_word)-1) < size):
                    # Read word in this direction
                    word = ''
                    coords = []
                    for k in range(len(selected_word)):
                        row = i + di * k
                        col = j + dj * k
                        word += grid[row][col]
                        coords.append((row, col))
                    
                    # If word matches, color all cells
                    if word == selected_word:
                        for row, col in coords:
                            buttons[row][col].config(bg='#ff9999', fg='white')
                        word_found = True
                        break
            
            if word_found:
                break
        if word_found:
            break
    
    # Check for game end
    if len(found_words) == len(current_words):
        game_over(score > computer_score)

def reveal_remaining_words():
    """Reveal all remaining words on the grid"""
    global current_words, found_words
    remaining_words = [word for word in current_words if word not in found_words]
    
    for word in remaining_words:
        for x in range(size):
            for y in range(size):
                # Check all 8 directions
                directions = [(0,1), (1,0), (1,1), (-1,0), (0,-1), (-1,-1), (1,-1), (-1,1)]
                for dx, dy in directions:
                    # Try to match word starting at this position and direction
                    matched = True
                    for i, letter in enumerate(word):
                        new_x, new_y = x + i*dx, y + i*dy
                        if (new_x < 0 or new_x >= size or 
                            new_y < 0 or new_y >= size or 
                            grid[new_x][new_y] != letter):
                            matched = False
                            break
                    
                    if matched:
                        # Word found, highlight it
                        for i in range(len(word)):
                            new_x, new_y = x + i*dx, y + i*dy
                            buttons[new_x][new_y].configure(bg='red', fg='white')

def update_timer():
    """Update the game timer"""
    global time_left, game_active
    
    if not game_active:
        return
    
    if time_left > 0:
        minutes = time_left // 60
        seconds = time_left % 60
        timer_label.config(
            text=f"Time Left: {minutes:02d}:{seconds:02d}")
        time_left -= 1
        root.after(1000, update_timer)
    else:
        reveal_remaining_words()
        root.after(2000, lambda: game_over(False))  # Wait 2 seconds to show the words before game over

def update_gif(label, frames, frame_index, delay):
    """Update the GIF animation frame"""
    global gif_label
    if gif_label is None or not gif_label.winfo_exists():
        return
    
    frame = frames[frame_index]
    frame_index = (frame_index + 1) % len(frames)
    label.configure(image=frame)
    root.after(delay, lambda: update_gif(label, frames, frame_index, delay))

def show_end_screen(won):
    """Show the animated end screen"""
    global gif_label
    
    # Remove existing gif_label if it exists
    if gif_label is not None and gif_label.winfo_exists():
        gif_label.destroy()
    
    # Create a new top-level window for the end screen
    end_window = tk.Toplevel(root)
    end_window.title("Game Over")
    
    # Set window size and position it in the center
    window_width = 400
    window_height = 700
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    end_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Load the appropriate GIF
    gif_path = os.path.join(SOUND_PATH, "victory.gif" if won else "defeat.gif")
    gif = Image.open(gif_path)
    
    # Convert all frames to PhotoImage
    frames = []
    for frame in ImageSequence.Iterator(gif):
        frame = frame.resize((300, 300), Image.LANCZOS)
        frames.append(ImageTk.PhotoImage(frame))
    
    # Create label for GIF
    gif_label = tk.Label(end_window)
    gif_label.pack(pady=20)
    
    # Add message
    if is_vs_ai:
        if score == computer_score:
            message = "It's a Draw!"
        else:
            message = f"{'You Won!' if score > computer_score else 'AI Won!'}"
    else:
        message = "Congratulations! You Won!" if won else "Game Over! Better luck next time!"
    tk.Label(end_window, text=message, font=('Helvetica', 16, 'bold')).pack(pady=10)
    
    # Add scores frame
    scores_frame = tk.Frame(end_window)
    scores_frame.pack(pady=10)
    
    # Add final score(s)
    if is_vs_ai:
        tk.Label(scores_frame, text=f"Your Score: {score}", font=('Helvetica', 14, 'bold'), fg='blue').pack(pady=5)
        tk.Label(scores_frame, text=f"AI Score: {computer_score}", font=('Helvetica', 14, 'bold'), fg='red').pack(pady=5)
    else:
        tk.Label(scores_frame, text=f"Final Score: {score}", font=('Helvetica', 14, 'bold'), fg='blue').pack(pady=10)
    
    # Add buttons frame
    buttons_frame = tk.Frame(end_window)
    buttons_frame.pack(pady=10)
    
    # Add play again button
    ttk.Button(buttons_frame, text="Play Again", command=lambda: [end_window.destroy(), reset_game()]).pack(side=tk.LEFT, padx=10)
    
    # Add exit button
    ttk.Button(buttons_frame, text="Exit Game", command=lambda: [end_window.destroy(), root.destroy()]).pack(side=tk.LEFT, padx=10)
    
    # Start GIF animation
    update_gif(gif_label, frames, 0, gif.info.get('duration', 100))

def game_over(won=False):
    """Handle game over state"""
    global game_active
    game_active = False
    
    if won:
        correct_sound.play()
    else:
        wrong_sound.play()
    
    show_end_screen(won)

def reset_game():
    """Reset the game state"""
    global word_pressed, previous, route, current_words, found_words
    global score, computer_score, wrong_attempts, game_active, time_left
    
    word_pressed = ''
    previous = [0, 0]
    route = [0, 0]
    current_words = []
    found_words = []
    score = 0
    computer_score = 0
    wrong_attempts = 0
    game_active = False
    time_left = 180
    
    frame1.destroy()
    frame2.destroy()
    frame3.destroy()
    create_welcome_screen()

def create_welcome_screen():
    """Create the welcome/setup screen"""
    global welcome_frame, name_entry, category_var, difficulty_var, vs_ai_var
    
    welcome_frame = tk.Frame(root, bg='#f0f0f0')
    welcome_frame.pack(pady=56, padx=180)
    
    # Player name
    tk.Label(welcome_frame, text="Name",
            font=('Helvetica', 15), fg='#456263',
            bg='#f0f0f0').grid(row=0, padx=10, pady=6)
    name_entry = tk.Entry(welcome_frame)
    name_entry.grid(row=0, column=1, ipady=6, ipadx=10)
    
    # Game level
    tk.Label(welcome_frame, text="Game Level",
            font=('Helvetica', 15), fg='#456263',
            bg='#f0f0f0').grid(row=1)
    difficulty_var = tk.StringVar(value="Normal")
    ttk.Combobox(welcome_frame,
                textvariable=difficulty_var,
                values=['Mini', 'Normal', 'Pro', 'Pro Max'],
                font=('Helvetica', 12)).grid(row=1, column=1,
                                           ipady=6, ipadx=10)
    
    # Category
    tk.Label(welcome_frame, text="Category",
            font=('Helvetica', 15), fg='#456263',
            bg='#f0f0f0').grid(row=2, pady=6)
    categories = load_categories()
    category_var = tk.StringVar(value=list(categories.keys())[0])
    ttk.Combobox(welcome_frame,
                textvariable=category_var,
                values=list(categories.keys()),
                font=('Helvetica', 12)).grid(row=2, column=1,
                                           ipady=6, ipadx=10)
    
    # VS AI mode
    vs_ai_var = tk.BooleanVar()
    tk.Checkbutton(welcome_frame, text="VS AI Mode",
                  variable=vs_ai_var,
                  font=('Helvetica', 12),
                  bg='#f0f0f0').grid(row=3, columnspan=2)
    
    # Button frame
    button_frame = tk.Frame(welcome_frame, bg='#f0f0f0')
    button_frame.grid(row=4, columnspan=2, pady=8)
    
    # Start button
    tk.Button(button_frame, text="New Game",
             command=start_game,
             font=('Helvetica', 12),
             bg='blue', fg='white',
             width=10).pack(side=tk.LEFT, padx=5)
    
    # Load button
    tk.Button(button_frame, text="Load Game",
             command=load_saved_game,
             font=('Helvetica', 12),
             bg='green', fg='white',
             width=10).pack(side=tk.LEFT, padx=5)

def load_saved_game():
    """Load game state from txt file"""
    global current_words, found_words, max_attempts, time_left
    global is_vs_ai, game_active, score, computer_score, wrong_attempts, grid
    global player_name, current_category, current_difficulty, size
    
    # Get filename from user
    filename = simpledialog.askstring("Load Game", "Enter filename to load (with .txt extension):", initialvalue="saved_game.txt")
    if not filename:  # User cancelled
        return
    if not filename.endswith('.txt'):
        filename += '.txt'
        
    save_path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(save_path, 'r') as f:
            lines = f.readlines()
            
            # Parse player info
            player_name = lines[0].split(": ")[1].strip()
            current_category = lines[1].split(": ")[1].strip()
            current_difficulty = lines[2].split(": ")[1].strip()
            is_vs_ai = lines[3].split(": ")[1].strip() == "True"
            
            # Set size based on difficulty
            if current_difficulty == "Mini":
                size = 8
            elif current_difficulty == "Normal":
                size = 10
            elif current_difficulty == "Pro":
                size = 12
            else:  # Pro Max
                size = 15
                
            # Parse scores
            score = int(lines[4].split(": ")[1])
            computer_score = int(lines[5].split(": ")[1])
            
            # Parse game state
            time_left = int(lines[6].split(": ")[1])
            wrong_attempts = int(lines[7].split(": ")[1])
            max_attempts = int(lines[8].split(": ")[1])
            
            # Parse words
            current_words = lines[9].split(": ")[1].strip().split(",")
            found_words = lines[10].split(": ")[1].strip().split(",")
            if found_words == ['']: found_words = []  # Handle empty found words
            
            # Parse and load grid
            grid_start = lines.index("Grid:\n") + 1
            grid = []
            for i in range(size):
                row = lines[grid_start + i].strip().split(",")
                grid.append(row)
                
            # Update entry fields
            name_entry.delete(0, tk.END)
            name_entry.insert(0, player_name)
            category_var.set(current_category)
            difficulty_var.set(current_difficulty)
            
            # Create game screen after grid is loaded
            create_game_screen()
            
            # Update grid display and status
            for i in range(size):
                for j in range(size):
                    buttons[i][j].config(text=grid[i][j])
            
            # Parse and restore grid status
            status_start = lines.index("Grid Status:\n") + 1
            for i in range(size):
                status_row = lines[status_start + i].strip().split(",")
                for j in range(size):
                    if status_row[j] == "1":  # Player found word
                        buttons[i][j].config(bg='#535edb', fg='white')
                    elif status_row[j] == "2":  # AI found word
                        buttons[i][j].config(bg='#ff9999', fg='white')
            
            # Update word list
            for word in found_words:
                for label in check_labels:
                    if label['text'] == word:
                        label.configure(font=('Helvetica', 1),
                                     fg='#f0f0f0', bg='#f0f0f0')
            
            # Start game
            game_active = True
            update_timer()
            
            messagebox.showinfo("Success", f"Game loaded successfully from {filename}!")
    except FileNotFoundError:
        messagebox.showerror("Error", f"Could not find save file: {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not load game: {str(e)}")

def create_game_screen():
    """Create the main game screen"""
    global frame1, frame2, frame3, check_labels, timer_label, attempts_label, score_label, ai_score_label
    global grid, buttons
    
    # Clear welcome screen
    if welcome_frame:
        welcome_frame.destroy()
    
    # Create main frames
    frame1 = tk.Frame(root, bg="white")
    frame1.pack(fill=tk.BOTH, side=tk.LEFT, expand=True,
                padx=20, pady=12)
    
    frame2 = tk.Frame(root, bg='white')
    frame2.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True,
                padx=20)
    
    frame3 = tk.Frame(root)
    frame3.pack(fill=tk.BOTH, side=tk.RIGHT, padx=20, pady=30)
    
    # Create labels for words
    check_labels = []
    for word in current_words:
        label = tk.Label(frame2, text=word,
                       font=('Helvetica', 12, 'bold'),
                       fg='#254359', bg='#cbe5f7',
                       width=20, height=1,  
                       relief=tk.RAISED, borderwidth=2)
        label.pack(pady=2)
        check_labels.append(label)
    
    # Timer, attempts and score
    timer_label = tk.Label(frame2,
                         text="Time Left: 03:00",
                         font=('Helvetica', 12),
                         bg='white')
    timer_label.pack(pady=5)
    
    attempts_label = tk.Label(frame2,
                           text=f"Attempts Left: {max_attempts}",
                           font=('Helvetica', 12),
                           bg='white')
    attempts_label.pack(pady=5)

    score_label = tk.Label(frame2,
                        text=f"Score: {score}",
                        font=('Helvetica', 12, 'bold'),
                        bg='white')
    score_label.pack(pady=5)

    # Add AI score label if in vs AI mode
    if is_vs_ai:
        ai_score_label = tk.Label(frame2,
                            text=f"AI Score: {computer_score}",
                            font=('Helvetica', 12, 'bold'),
                            fg='red',
                            bg='white')
        ai_score_label.pack(pady=5)
    
    # Check word button
    tk.Button(frame2, text="Check Word",
             command=check_word,
             height=1, width=15,
             bg="#70889c", fg='white',
             font=('Helvetica', 12, 'bold')).pack(pady=10)
    
    # Add Save button
    tk.Button(frame2, text="Save Game",
             command=save_game,
             height=1, width=15,
             bg="green", fg='white',
             font=('Helvetica', 12, 'bold')).pack(pady=5)
    
    # Add Exit button
    tk.Button(frame2, text="Exit Game",
             command=lambda: exit_game(),
             height=1, width=15,
             bg="red", fg='white',
             font=('Helvetica', 12, 'bold')).pack(pady=5)
    
    # Initialize grid if it's empty
    if not grid:
        grid = [['' for _ in range(size)] for _ in range(size)]
        # Place words
        for word in current_words:
            place_word(word)
        # Fill remaining spaces
        for x in range(size):
            for y in range(size):
                if not grid[x][y]:
                    grid[x][y] = random.choice(string.ascii_uppercase)
    
    # Create buttons grid
    buttons = []
    for x in range(size):
        button_row = []
        for y in range(size):
            button = tk.Button(
                frame1,
                text=grid[x][y],
                bg='#255059',
                fg='white',
                width=2,
                height=1,
                font=('Helvetica', 12, 'bold'),
                relief=tk.RAISED,
                borderwidth=2,
                command=lambda x=x, y=y: button_press(x, y))
            button.grid(row=x, column=y, padx=2, pady=2)
            button_row.append(button)
        buttons.append(button_row)

def place_word(word):
    """Place a word in the grid"""
    placed = False
    max_attempts = 200  
    attempts = max_attempts
    
    # Try simpler directions first, then more complex ones
    directions = [
        [0, 1],   # horizontal right
        [1, 0],   # vertical down
        [1, 1],   # diagonal down-right
        [-1, 0],  # vertical up
        [0, -1],  # horizontal left
        [-1, -1], # diagonal up-left
        [-1, 1],  # diagonal up-right
        [1, -1]   # diagonal down-left
    ]
    
    while not placed and attempts > 0:
        # Try directions in order for first half of attempts
        if attempts > max_attempts / 2:
            direction = directions[attempts % len(directions)]
        else:
            # Random direction for remaining attempts
            direction = random.choice(directions)
        
        # Try to place near the center first
        center = size // 2
        if attempts > max_attempts / 2:
            x = random.randint(center - 3, center + 3)
            y = random.randint(center - 3, center + 3)
            # Keep coordinates in bounds
            x = max(0, min(x, size - 1))
            y = max(0, min(y, size - 1))
        else:
            # Random position for remaining attempts
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)
        
        if can_place_word(word, x, y, direction):
            fill_word(word, x, y, direction)
            placed = True
        
        attempts -= 1
    
    return placed

def can_place_word(word, x, y, direction):
    """Check if word can be placed at position"""
    # Check bounds
    end_x = x + len(word) * direction[0]
    end_y = y + len(word) * direction[1]
    
    if (end_x >= size or end_x < 0 or
        end_y >= size or end_y < 0):
        return False
    
    # Check each position along the word path
    intersections = 0
    for i in range(len(word)):
        curr_x = x + direction[0] * i
        curr_y = y + direction[1] * i
        
        # If there's a letter there already
        if grid[curr_x][curr_y]:
            # Allow intersection only if it's the same letter
            if grid[curr_x][curr_y] != word[i]:
                return False
            intersections += 1
            
            # Don't allow too many intersections
            if intersections > len(word) // 3:
                return False
    
    return True

def fill_word(word, x, y, direction):
    """Fill word in grid"""
    for i in range(len(word)):
        curr_x = x + direction[0] * i
        curr_y = y + direction[1] * i
        grid[curr_x][curr_y] = word[i]

def start_game():
    """Initialize and start a new game"""
    global current_words, found_words, max_attempts, time_left
    global is_vs_ai, game_active, player_name, current_category, current_difficulty, size
    
    # Validate inputs
    if not name_entry.get():
        messagebox.showerror("Error", "Please enter your name")
        return
    
    # Store player info
    player_name = name_entry.get()
    current_category = category_var.get()
    current_difficulty = difficulty_var.get()
    
    # Set game parameters
    is_vs_ai = vs_ai_var.get()
    
    # Get words for selected category
    categories = load_categories()
    available_words = categories.get(current_category, [])
    if not available_words:
        messagebox.showerror("Error",
                           f"No words available for category: {current_category}")
        return
    
    # Select random words based on difficulty
    if current_difficulty == "Mini":
        num_words = 4
        attempts_per_word = 3
        time_per_word = 40
        min_length = 3
        max_length = 5
        size = 8  # Smaller grid for easier difficulty
    elif current_difficulty == "Normal":
        num_words = 6
        attempts_per_word = 2
        time_per_word = 40
        min_length = 4
        max_length = 6
        size = 10  # Medium grid size
    elif current_difficulty == "Pro":
        num_words = 8
        attempts_per_word = 1
        time_per_word = 40
        min_length = 5
        max_length = 8
        size = 12  # Larger grid for more challenge
    else:  # Pro Max
        num_words = 10
        attempts_per_word = 1
        time_per_word = 40
        min_length = 6
        max_length = 10
        size = 15  # Largest grid for maximum challenge
    
    # Filter words by length based on difficulty
    filtered_words = [word for word in available_words if min_length <= len(word) <= max_length]
    if not filtered_words:
        messagebox.showerror("Error", f"No words available for the selected difficulty in category: {current_category}")
        return
    
    # Select words and set game parameters
    current_words = random.sample(filtered_words, min(num_words, len(filtered_words)))
    found_words = []
    max_attempts = len(current_words) * attempts_per_word
    time_left = len(current_words) * time_per_word
    
    # Create game screen
    create_game_screen()
    
    # Start game
    game_active = True
    update_timer()

def save_game():
    """Save current game state to txt file"""
    if not game_active:
        messagebox.showwarning("Warning", "No active game to save!")
        return
        
    # Get filename from user
    filename = simpledialog.askstring("Save Game", "Enter filename (with .txt extension):", initialvalue="saved_game.txt")
    if not filename:  # User cancelled
        return
    if not filename.endswith('.txt'):
        filename += '.txt'
        
    save_path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(save_path, 'w') as f:
            # Save player info
            f.write(f"Player: {player_name}\n")
            f.write(f"Category: {current_category}\n")
            f.write(f"Difficulty: {current_difficulty}\n")
            f.write(f"VS AI: {is_vs_ai}\n")
            
            # Save scores
            f.write(f"Score: {score}\n")
            f.write(f"Computer Score: {computer_score}\n")
            
            # Save game state
            f.write(f"Time Left: {time_left}\n")
            f.write(f"Wrong Attempts: {wrong_attempts}\n")
            f.write(f"Max Attempts: {max_attempts}\n")
            
            # Save words
            f.write("Current Words: " + ",".join(current_words) + "\n")
            f.write("Found Words: " + ",".join(found_words) + "\n")
            
            # Save grid
            f.write("Grid:\n")
            for row in grid:
                f.write(",".join(str(cell) for cell in row) + "\n")
            
            # Save grid status (found words highlighting)
            f.write("Grid Status:\n")
            for i in range(size):
                status_row = []
                for j in range(size):
                    bg_color = buttons[i][j].cget('bg')
                    if bg_color == '#535edb':  # Player found word (blue)
                        status_row.append("1")
                    elif bg_color == '#ff9999':  # AI found word (red)
                        status_row.append("2")
                    else:  # Not found
                        status_row.append("0")
                f.write(",".join(status_row) + "\n")
        
        messagebox.showinfo("Success", f"Game saved successfully as {filename}!")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save game: {str(e)}")

def exit_game():
    """Exit the game"""
    if messagebox.askyesno("Exit", "Would you like to save before exiting?"):
        save_game()
    if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?"):
        root.quit()

def main():
    """Main function"""
    global root
    
    root = tk.Tk()
    root.title("Word Search Game")
    
    create_header()
    create_welcome_screen()
    create_footer()
    
    root.mainloop()

if __name__ == "__main__":
    main()