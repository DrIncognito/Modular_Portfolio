import random
import os
from modular_portfolio.modular_core.interface import BasePlugin

class GameEngine:
    """Core game engine with various games"""
    
    def __init__(self):
        self.games = {
            'rock_paper_scissors': self.rock_paper_scissors,
            'guessing_game': self.guessing_game,
            'hangman': self.hangman,
            'word_scramble': self.word_scramble,
            'dice_roll': self.dice_roll
        }
        
        # Word lists for games
        self.hangman_words = [
            'python', 'programming', 'computer', 'keyboard', 'monitor', 'software',
            'hardware', 'algorithm', 'function', 'variable', 'debugging', 'coding',
            'development', 'application', 'database', 'framework', 'library'
        ]
        
        self.scramble_words = [
            'challenge', 'adventure', 'mystery', 'treasure', 'journey', 'discovery',
            'knowledge', 'wisdom', 'learning', 'education', 'creativity', 'innovation'
        ]
    
    def rock_paper_scissors(self, user_input=None, mode='cli'):
        """Rock Paper Scissors game"""
        choices = ['rock', 'paper', 'scissors']
        
        if mode == 'cli':
            if user_input is None:
                print("\n🎮 Rock Paper Scissors!")
                print("Choose: rock, paper, or scissors (or 'quit' to exit)")
                user_choice = input("Your choice: ").lower().strip()
                if user_choice == 'quit':
                    return "Thanks for playing!"
                if user_choice not in choices:
                    return "Invalid choice! Please choose rock, paper, or scissors."
            else:
                user_choice = user_input.lower().strip()
                if user_choice not in choices:
                    return "Invalid choice! Please choose rock, paper, or scissors."
        else:
            user_choice = user_input.lower().strip() if user_input else 'rock'
            if user_choice not in choices:
                return {"error": "Invalid choice! Please choose rock, paper, or scissors."}
        
        computer_choice = random.choice(choices)
        
        # Determine winner
        if user_choice == computer_choice:
            result = "It's a tie!"
        elif (user_choice == 'rock' and computer_choice == 'scissors') or \
             (user_choice == 'paper' and computer_choice == 'rock') or \
             (user_choice == 'scissors' and computer_choice == 'paper'):
            result = "You win!"
        else:
            result = "Computer wins!"
        
        game_result = f"You chose: {user_choice}\nComputer chose: {computer_choice}\n{result}"
        
        if mode == 'cli':
            print(game_result)
            return game_result
        else:
            return {
                "user_choice": user_choice,
                "computer_choice": computer_choice,
                "result": result,
                "message": game_result
            }
    
    def guessing_game(self, user_input=None, mode='cli', target=None, attempts=None):
        """Number guessing game"""
        if target is None:
            target = random.randint(1, 100)
        if attempts is None:
            attempts = 0
        
        max_attempts = 10
        
        if mode == 'cli':
            if user_input is None:
                print(f"\n🎮 Guessing Game!")
                print(f"I'm thinking of a number between 1 and 100.")
                print(f"You have {max_attempts} attempts to guess it!")
                
                while attempts < max_attempts:
                    try:
                        guess = int(input(f"Attempt {attempts + 1}: Enter your guess: "))
                        attempts += 1
                        
                        if guess == target:
                            return f"🎉 Congratulations! You guessed {target} in {attempts} attempts!"
                        elif guess < target:
                            print("Too low! Try higher.")
                        else:
                            print("Too high! Try lower.")
                    except ValueError:
                        print("Please enter a valid number!")
                
                return f"😞 Game over! The number was {target}. Better luck next time!"
        else:
            if user_input is None:
                return {
                    "message": f"I'm thinking of a number between 1 and 100. You have {max_attempts} attempts!",
                    "target": target,
                    "attempts": attempts,
                    "max_attempts": max_attempts
                }
            
            try:
                guess = int(user_input)
                attempts += 1
                
                if guess == target:
                    return {
                        "success": True,
                        "message": f"🎉 Congratulations! You guessed {target} in {attempts} attempts!",
                        "attempts": attempts
                    }
                elif attempts >= max_attempts:
                    return {
                        "game_over": True,
                        "message": f"😞 Game over! The number was {target}. Better luck next time!",
                        "target": target
                    }
                elif guess < target:
                    return {
                        "message": f"Too low! Try higher. Attempt {attempts}/{max_attempts}",
                        "target": target,
                        "attempts": attempts,
                        "hint": "higher"
                    }
                else:
                    return {
                        "message": f"Too high! Try lower. Attempt {attempts}/{max_attempts}",
                        "target": target,
                        "attempts": attempts,
                        "hint": "lower"
                    }
            except ValueError:
                return {"error": "Please enter a valid number!"}
    
    def hangman(self, user_input=None, mode='cli', word=None, guessed_letters=None, wrong_guesses=None):
        """Hangman word guessing game"""
        if word is None:
            word = random.choice(self.hangman_words).upper()
        if guessed_letters is None:
            guessed_letters = set()
        if wrong_guesses is None:
            wrong_guesses = 0
            
        max_wrong = 6
        
        def display_word():
            return ' '.join([letter if letter in guessed_letters else '_' for letter in word])
        
        def hangman_drawing(wrong):
            stages = [
                "",
                "  |",
                "  |\n  |",
                "  |\n  |\n  |",
                "  +---+\n  |   |\n      |\n      |\n      |\n      |",
                "  +---+\n  |   |\n  O   |\n      |\n      |\n      |",
                "  +---+\n  |   |\n  O   |\n  |   |\n      |\n      |",
                "  +---+\n  |   |\n  O   |\n /|   |\n      |\n      |",
                "  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n      |",
                "  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n      |",
                "  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n      |"
            ]
            return stages[min(wrong, len(stages) - 1)]
        
        if mode == 'cli':
            if user_input is None:
                print("\n🎮 Hangman!")
                print(f"Word: {display_word()}")
                print(f"Wrong guesses: {wrong_guesses}/{max_wrong}")
                print(hangman_drawing(wrong_guesses))
                
                while wrong_guesses < max_wrong and '_' in display_word():
                    guess = input("Guess a letter: ").upper().strip()
                    
                    if len(guess) != 1 or not guess.isalpha():
                        print("Please enter a single letter!")
                        continue
                    
                    if guess in guessed_letters:
                        print("You already guessed that letter!")
                        continue
                    
                    guessed_letters.add(guess)
                    
                    if guess in word:
                        print(f"Good guess! '{guess}' is in the word.")
                    else:
                        wrong_guesses += 1
                        print(f"Sorry, '{guess}' is not in the word.")
                    
                    print(f"\nWord: {display_word()}")
                    print(f"Wrong guesses: {wrong_guesses}/{max_wrong}")
                    print(hangman_drawing(wrong_guesses))
                
                if '_' not in display_word():
                    return f"🎉 Congratulations! You guessed the word: {word}"
                else:
                    return f"😞 Game over! The word was: {word}"
        else:
            if user_input is None:
                return {
                    "word_display": display_word(),
                    "wrong_guesses": wrong_guesses,
                    "max_wrong": max_wrong,
                    "guessed_letters": list(guessed_letters),
                    "hangman_art": hangman_drawing(wrong_guesses),
                    "game_state": "playing"
                }
            
            guess = user_input.upper().strip()
            
            if len(guess) != 1 or not guess.isalpha():
                return {"error": "Please enter a single letter!"}
            
            if guess in guessed_letters:
                return {"error": "You already guessed that letter!"}
            
            guessed_letters.add(guess)
            
            if guess in word:
                message = f"Good guess! '{guess}' is in the word."
            else:
                wrong_guesses += 1
                message = f"Sorry, '{guess}' is not in the word."
            
            word_display = display_word()
            
            if '_' not in word_display:
                return {
                    "success": True,
                    "message": f"🎉 Congratulations! You guessed the word: {word}",
                    "word": word,
                    "word_display": word_display
                }
            elif wrong_guesses >= max_wrong:
                return {
                    "game_over": True,
                    "message": f"😞 Game over! The word was: {word}",
                    "word": word,
                    "hangman_art": hangman_drawing(wrong_guesses)
                }
            else:
                return {
                    "message": message,
                    "word_display": word_display,
                    "wrong_guesses": wrong_guesses,
                    "max_wrong": max_wrong,
                    "guessed_letters": list(guessed_letters),
                    "hangman_art": hangman_drawing(wrong_guesses),
                    "game_state": "playing"
                }
    
    def word_scramble(self, user_input=None, mode='cli', word=None):
        """Word scramble game"""
        if word is None:
            word = random.choice(self.scramble_words)
        
        scrambled = ''.join(random.sample(word, len(word)))
        
        if mode == 'cli':
            if user_input is None:
                print(f"\n🎮 Word Scramble!")
                print(f"Unscramble this word: {scrambled.upper()}")
                print(f"Hint: It's {len(word)} letters long")
                
                guess = input("Your answer: ").lower().strip()
                
                if guess == word:
                    return f"🎉 Correct! The word was '{word}'"
                else:
                    return f"😞 Sorry! The correct word was '{word}'"
        else:
            if user_input is None:
                return {
                    "scrambled": scrambled.upper(),
                    "length": len(word),
                    "original": word
                }
            
            guess = user_input.lower().strip()
            
            if guess == word:
                return {
                    "success": True,
                    "message": f"🎉 Correct! The word was '{word}'"
                }
            else:
                return {
                    "success": False,
                    "message": f"😞 Sorry! The correct word was '{word}'"
                }
    
    def dice_roll(self, user_input=None, mode='cli', num_dice=1, dice_sides=6):
        """Dice rolling game with customizable dice sides"""
        # Parse input for dice notation (e.g., "2d20", "3d6", "1d100")
        if user_input and isinstance(user_input, str):
            user_input = user_input.strip().lower()
            if 'd' in user_input:
                try:
                    parts = user_input.split('d')
                    if len(parts) == 2:
                        num_dice = int(parts[0]) if parts[0] else 1
                        dice_sides = int(parts[1])
                    else:
                        # If no number before 'd', assume 1 die
                        num_dice = 1
                        dice_sides = int(parts[1])
                except ValueError:
                    # Fall back to defaults if parsing fails
                    num_dice = 1
                    dice_sides = 6
            else:
                try:
                    num_dice = int(user_input)
                    dice_sides = 6  # Default to d6
                except ValueError:
                    num_dice = 1
                    dice_sides = 6
        elif user_input and isinstance(user_input, int):
            num_dice = user_input
            dice_sides = 6
        
        # Validate ranges
        num_dice = max(1, min(20, num_dice))  # Max 20 dice
        valid_dice_sides = [4, 6, 8, 10, 12, 20, 100]
        if dice_sides not in valid_dice_sides:
            dice_sides = 6  # Default to d6 if invalid
        
        rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
        total = sum(rolls)
        
        # Create dice notation string
        dice_notation = f"{num_dice}d{dice_sides}"
        
        # Create emoji representation based on dice type
        dice_emoji = {
            4: "🔺",    # d4 - triangle
            6: "🎲",    # d6 - standard die
            8: "🔸",    # d8 - diamond
            10: "🔟",   # d10 - ten
            12: "🔷",   # d12 - dodecagon
            20: "⭐",   # d20 - star
            100: "💯"   # d100 - hundred
        }
        
        emoji = dice_emoji.get(dice_sides, "🎲")
        
        if num_dice == 1:
            result = f"{emoji} Rolled {dice_notation}: {rolls[0]}"
        else:
            result = f"{emoji} Rolled {dice_notation}: {rolls}\nTotal: {total}"
        
        if mode == 'cli':
            print(f"\n{result}")
            return result
        else:
            return {
                "rolls": rolls,
                "total": total,
                "num_dice": num_dice,
                "dice_sides": dice_sides,
                "dice_notation": dice_notation,
                "emoji": emoji,
                "message": result
            }

class Gamenight(BasePlugin):
    def __init__(self):
        self.engine = GameEngine()
    
    def run(self, mode: str):
        if mode == 'cli':
            return self._run_cli()
        elif mode == 'web':
            return self._run_web()
        elif mode == 'gui':
            return self._run_gui()
    
    def _run_cli(self):
        """CLI interface for games"""
        print("\n🎮 Welcome to Game Night! 🎮")
        print("Available games:")
        print("1. Rock Paper Scissors")
        print("2. Number Guessing Game")
        print("3. Hangman")
        print("4. Word Scramble")
        print("5. Dice Roll")
        print("6. Exit")
        
        while True:
            try:
                choice = input("\nChoose a game (1-6): ").strip()
                
                if choice == '1':
                    while True:
                        self.engine.rock_paper_scissors(mode='cli')
                        if input("\nPlay again? (y/n): ").lower() != 'y':
                            break
                elif choice == '2':
                    self.engine.guessing_game(mode='cli')
                elif choice == '3':
                    self.engine.hangman(mode='cli')
                elif choice == '4':
                    self.engine.word_scramble(mode='cli')
                elif choice == '5':
                    print("\n🎲 Dice Roll Options:")
                    print("Enter dice in format: [number]d[sides] (e.g., 2d20, 1d6, 3d10)")
                    print("Or just enter number of dice (defaults to d6)")
                    print("Available dice: d4, d6, d8, d10, d12, d20, d100")
                    dice_input = input("Dice to roll (e.g., 2d20 or just 3): ").strip()
                    if not dice_input:
                        dice_input = "1d6"
                    self.engine.dice_roll(dice_input, mode='cli')
                elif choice == '6':
                    print("Thanks for playing! 🎮")
                    break
                else:
                    print("Invalid choice! Please choose 1-6.")
                    
            except KeyboardInterrupt:
                print("\n\nThanks for playing! 🎮")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
    
    def _run_web(self):
        """Web interface - returns None to use template"""
        return None
    
    def _run_gui(self):
        """GUI interface for games"""
        try:
            from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                                       QPushButton, QLabel, QInputDialog, 
                                       QMessageBox, QComboBox)
            from PyQt5.QtCore import Qt
            
            app = QApplication.instance() or QApplication([])
            
            # Create main window
            window = QWidget()
            window.setWindowTitle("Game Night 🎮")
            window.setGeometry(300, 300, 400, 300)
            
            layout = QVBoxLayout()
            
            # Title
            title = QLabel("🎮 Welcome to Game Night! 🎮")
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
            layout.addWidget(title)
            
            # Game buttons
            games = [
                ("Rock Paper Scissors", self._gui_rock_paper_scissors),
                ("Number Guessing Game", self._gui_guessing_game),
                ("Hangman", self._gui_hangman),
                ("Word Scramble", self._gui_word_scramble),
                ("Dice Roll", self._gui_dice_roll)
            ]
            
            for game_name, game_func in games:
                btn = QPushButton(game_name)
                btn.clicked.connect(game_func)
                btn.setStyleSheet("padding: 10px; margin: 5px; font-size: 14px;")
                layout.addWidget(btn)
            
            window.setLayout(layout)
            window.show()
            
        except ImportError:
            print("PyQt5 not available. GUI mode requires PyQt5.")
    
    def _gui_rock_paper_scissors(self):
        """GUI Rock Paper Scissors"""
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        
        choices = ['rock', 'paper', 'scissors']
        choice, ok = QInputDialog.getItem(None, "Rock Paper Scissors", 
                                        "Choose your weapon:", choices, 0, False)
        if ok:
            result = self.engine.rock_paper_scissors(choice, mode='gui')
            QMessageBox.information(None, "Result", result['message'])
    
    def _gui_guessing_game(self):
        """GUI Guessing Game"""
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        
        target = random.randint(1, 100)
        attempts = 0
        max_attempts = 10
        
        QMessageBox.information(None, "Guessing Game", 
                               f"I'm thinking of a number between 1 and 100.\nYou have {max_attempts} attempts!")
        
        while attempts < max_attempts:
            guess, ok = QInputDialog.getInt(None, "Guessing Game", 
                                          f"Attempt {attempts + 1}/{max_attempts}:\nEnter your guess (1-100):", 
                                          50, 1, 100)
            if not ok:
                break
                
            result = self.engine.guessing_game(str(guess), mode='gui', target=target, attempts=attempts)
            attempts = result.get('attempts', attempts + 1)
            
            if result.get('success'):
                QMessageBox.information(None, "Congratulations!", result['message'])
                break
            elif result.get('game_over'):
                QMessageBox.information(None, "Game Over", result['message'])
                break
            else:
                QMessageBox.information(None, "Keep Trying!", result['message'])
    
    def _gui_hangman(self):
        """GUI Hangman"""
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        
        word = random.choice(self.engine.hangman_words).upper()
        guessed_letters = set()
        wrong_guesses = 0
        max_wrong = 6
        
        while wrong_guesses < max_wrong:
            current_state = self.engine.hangman(None, mode='gui', word=word, 
                                              guessed_letters=guessed_letters, wrong_guesses=wrong_guesses)
            
            if current_state.get('success'):
                QMessageBox.information(None, "Congratulations!", current_state['message'])
                break
            elif current_state.get('game_over'):
                QMessageBox.information(None, "Game Over", current_state['message'])
                break
            
            display_text = f"Word: {current_state['word_display']}\n"
            display_text += f"Wrong guesses: {current_state['wrong_guesses']}/{current_state['max_wrong']}\n"
            display_text += f"Guessed letters: {', '.join(sorted(current_state['guessed_letters']))}\n\n"
            display_text += current_state['hangman_art']
            
            letter, ok = QInputDialog.getText(None, "Hangman", 
                                            f"{display_text}\n\nGuess a letter:")
            if not ok or not letter:
                break
                
            result = self.engine.hangman(letter, mode='gui', word=word, 
                                       guessed_letters=guessed_letters, wrong_guesses=wrong_guesses)
            
            if result.get('error'):
                QMessageBox.warning(None, "Invalid Input", result['error'])
                continue
                
            guessed_letters = set(result.get('guessed_letters', []))
            wrong_guesses = result.get('wrong_guesses', 0)
            
            if result.get('success'):
                QMessageBox.information(None, "Congratulations!", result['message'])
                break
            elif result.get('game_over'):
                QMessageBox.information(None, "Game Over", result['message'])
                break
    
    def _gui_word_scramble(self):
        """GUI Word Scramble"""
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        
        word = random.choice(self.engine.scramble_words)
        scrambled_info = self.engine.word_scramble(None, mode='gui', word=word)
        
        guess, ok = QInputDialog.getText(None, "Word Scramble", 
                                       f"Unscramble this word: {scrambled_info['scrambled']}\n"
                                       f"Hint: It's {scrambled_info['length']} letters long\n\n"
                                       f"Your answer:")
        if ok:
            result = self.engine.word_scramble(guess, mode='gui', word=word)
            QMessageBox.information(None, "Result", result['message'])
    
    def _gui_dice_roll(self):
        """GUI Dice Roll with customizable dice"""
        from PyQt5.QtWidgets import QInputDialog, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QSpinBox, QComboBox, QPushButton, QLabel
        
        # Create custom dialog for dice selection
        dialog = QDialog()
        dialog.setWindowTitle("Dice Roll Configuration")
        dialog.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        # Number of dice
        num_layout = QHBoxLayout()
        num_layout.addWidget(QLabel("Number of dice:"))
        num_spinbox = QSpinBox()
        num_spinbox.setRange(1, 20)
        num_spinbox.setValue(1)
        num_layout.addWidget(num_spinbox)
        layout.addLayout(num_layout)
        
        # Dice type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Dice type:"))
        dice_combo = QComboBox()
        dice_options = [
            ("d4 🔺", 4),
            ("d6 🎲", 6), 
            ("d8 🔸", 8),
            ("d10 🔟", 10),
            ("d12 🔷", 12),
            ("d20 ⭐", 20),
            ("d100 💯", 100)
        ]
        for label, value in dice_options:
            dice_combo.addItem(label, value)
        dice_combo.setCurrentIndex(1)  # Default to d6
        type_layout.addWidget(dice_combo)
        layout.addLayout(type_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        roll_button = QPushButton("Roll Dice!")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(roll_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # Connect buttons
        result_data = {"rolled": False}
        
        def roll_dice():
            num_dice = num_spinbox.value()
            dice_sides = dice_combo.currentData()
            dice_notation = f"{num_dice}d{dice_sides}"
            
            result = self.engine.dice_roll(dice_notation, mode='gui')
            
            # Create detailed result message
            message = f"🎲 {result['dice_notation']} Roll Result:\n\n"
            message += f"Rolls: {result['rolls']}\n"
            if result['num_dice'] > 1:
                message += f"Total: {result['total']}\n"
            message += f"\nDice: {result['emoji']} {dice_sides}-sided"
            
            QMessageBox.information(None, "Dice Roll Result", message)
            result_data["rolled"] = True
            dialog.accept()
        
        def cancel():
            dialog.reject()
        
        roll_button.clicked.connect(roll_dice)
        cancel_button.clicked.connect(cancel)
        
        dialog.exec_()
