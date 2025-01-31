Word Search Game

A feature-rich word search puzzle game with multiple difficulty levels, categories, and an AI opponent mode.

Installation

1. Ensure you have Python 3.x installed on your system
2. Install required dependencies:
   ```
   pip install pygame Pillow tkinter
   ```

Project Structure

```
word-search/
├── DOC/
│   └── report.pdf
├── SRC/
│   ├── main.py
│   ├── victory.wav
│   ├── defeat.wav
│   ├── victory.gif
│   ├── defeat.gif
│   └── files/
│       ├── animals.txt
│       ├── fruits.txt
│       ├── places.txt
│       ├── sports.txt
│       └── colors.txt
└── README.txt
```

Features

- Multiple difficulty levels: Mini, Normal, Pro, and Pro Max
- Various word categories: Animals, Fruits, Places, Sports, and Colors
- AI opponent mode
- Save/Load game functionality
- Score tracking
- Sound effects and animations
- Time-based challenges
- Limited attempts system

 How to Play

1. Run the game:
   ```
   python main.py
   ```

2. In the welcome screen:
   - Enter your name
   - Select difficulty level
   - Choose word category
   - Toggle AI opponent mode (optional)
   - Click "New Game" to start or "Load Game" to continue a saved game

3. Gameplay:
   - Find words by clicking and dragging through letters
   - Words can be placed horizontally, vertically, or diagonally
   - Click "Check Word" to verify your selection
   - Monitor your remaining time and attempts
   - Use "Save Game" to save your progress

Difficulty Levels

- Mini: 8x8 grid, 4 words, easier words (3-5 letters)
- Normal: 10x10 grid, 6 words, medium words (4-6 letters)
- Pro: 12x12 grid, 8 words, harder words (5-8 letters)
- Pro Max: 15x15 grid, 10 words, challenging words (6-10 letters)

Save/Load Feature

- Games can be saved at any time using the "Save Game" button
- Saved games are stored as .txt files in the game directory
- Load previously saved games using the "Load Game" button

Demo Video Link
https://drive.google.com/file/d/10SM1XUmV02s84zu8tYlCskItHACv1t72/view?usp=sharing

Credits

Created by Team Error 404
Sound effects and animations included
