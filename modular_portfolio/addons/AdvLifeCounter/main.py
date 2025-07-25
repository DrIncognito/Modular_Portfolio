import json
from modular_portfolio.modular_core.interface import BasePlugin

class Counter:
    """Individual counter for a player"""
    def __init__(self, name, value=0, min_val=None, max_val=None, color="#007bff"):
        self.name = name
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.color = color
        self.history = [value]  # Track value changes
    
    def modify(self, amount):
        """Modify counter value with bounds checking"""
        new_value = self.value + amount
        
        if self.min_val is not None and new_value < self.min_val:
            new_value = self.min_val
        if self.max_val is not None and new_value > self.max_val:
            new_value = self.max_val
            
        self.value = new_value
        self.history.append(new_value)
        return new_value
    
    def set_value(self, value):
        """Set counter to specific value"""
        if self.min_val is not None and value < self.min_val:
            value = self.min_val
        if self.max_val is not None and value > self.max_val:
            value = self.max_val
            
        self.value = value
        self.history.append(value)
        return value
    
    def reset(self):
        """Reset counter to initial value"""
        initial_value = self.history[0] if self.history else 0
        self.value = initial_value
        self.history = [initial_value]
    
    def to_dict(self):
        """Convert counter to dictionary for serialization"""
        return {
            'name': self.name,
            'value': self.value,
            'min_val': self.min_val,
            'max_val': self.max_val,
            'color': self.color,
            'history': self.history
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create counter from dictionary"""
        counter = cls(
            data['name'], 
            data['value'], 
            data.get('min_val'), 
            data.get('max_val'), 
            data.get('color', '#007bff')
        )
        counter.history = data.get('history', [data['value']])
        return counter

class Player:
    """Player with multiple counters"""
    def __init__(self, name, player_id=None):
        self.name = name
        self.id = player_id or f"player_{hash(name) % 10000}"
        self.counters = {}
        self.active = True
    
    def add_counter(self, counter_name, initial_value=0, min_val=None, max_val=None, color="#007bff"):
        """Add a new counter to the player"""
        self.counters[counter_name] = Counter(counter_name, initial_value, min_val, max_val, color)
    
    def get_counter(self, counter_name):
        """Get a specific counter"""
        return self.counters.get(counter_name)
    
    def modify_counter(self, counter_name, amount):
        """Modify a counter's value"""
        if counter_name in self.counters:
            return self.counters[counter_name].modify(amount)
        return None
    
    def set_counter(self, counter_name, value):
        """Set a counter to a specific value"""
        if counter_name in self.counters:
            return self.counters[counter_name].set_value(value)
        return None
    
    def reset_all_counters(self):
        """Reset all counters to their initial values"""
        for counter in self.counters.values():
            counter.reset()
    
    def to_dict(self):
        """Convert player to dictionary for serialization"""
        return {
            'name': self.name,
            'id': self.id,
            'active': self.active,
            'counters': {name: counter.to_dict() for name, counter in self.counters.items()}
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create player from dictionary"""
        player = cls(data['name'], data.get('id'))
        player.active = data.get('active', True)
        for name, counter_data in data.get('counters', {}).items():
            player.counters[name] = Counter.from_dict(counter_data)
        return player

class GameSession:
    """Manages a game session with multiple players"""
    def __init__(self, num_players=2):
        self.players = []
        self.counter_templates = {}
        self.session_name = f"Game Session {hash(str(num_players)) % 1000}"
        self.setup_default_templates()
    
    def setup_default_templates(self):
        """Setup default counter templates"""
        self.counter_templates = {
            'Life': {'value': 20, 'min_val': 0, 'max_val': None, 'color': '#dc3545'},
            'Poison': {'value': 0, 'min_val': 0, 'max_val': 10, 'color': '#28a745'},
            'Energy': {'value': 0, 'min_val': 0, 'max_val': None, 'color': '#ffc107'},
            'Experience': {'value': 0, 'min_val': None, 'max_val': None, 'color': '#17a2b8'},
            'Mana': {'value': 0, 'min_val': 0, 'max_val': None, 'color': '#6f42c1'},
            'Commander Damage': {'value': 0, 'min_val': 0, 'max_val': 21, 'color': '#fd7e14'},
            'Tokens': {'value': 0, 'min_val': 0, 'max_val': None, 'color': '#20c997'},
            'Storm Count': {'value': 0, 'min_val': 0, 'max_val': None, 'color': '#6c757d'}
            
        }
    
    def add_counter_template(self, name, value=0, min_val=None, max_val=None, color="#007bff"):
        """Add a custom counter template"""
        self.counter_templates[name] = {
            'value': value,
            'min_val': min_val,
            'max_val': max_val,
            'color': color
        }
    
    def create_players(self, player_names, selected_counters):
        """Create players with selected counter types"""
        self.players = []
        for i, name in enumerate(player_names):
            player = Player(name, f"player_{i}")
            
            # Add selected counters to each player
            for counter_name in selected_counters:
                if counter_name in self.counter_templates:
                    template = self.counter_templates[counter_name]
                    player.add_counter(
                        counter_name,
                        template['value'],
                        template['min_val'],
                        template['max_val'],
                        template['color']
                    )
            
            self.players.append(player)
    
    def get_player(self, player_id):
        """Get player by ID"""
        for player in self.players:
            if player.id == player_id:
                return player
        return None
    
    def get_game_state(self):
        """Get current game state as dictionary"""
        return {
            'session_name': self.session_name,
            'players': [player.to_dict() for player in self.players],
            'counter_templates': self.counter_templates
        }
    
    def reset_game(self):
        """Reset all players' counters"""
        for player in self.players:
            player.reset_all_counters()

class AdvLifeCounter(BasePlugin):
    def run(self, mode: str):
        # Initialize session state
        if not hasattr(self, 'session'):
            self.session = None
        if not hasattr(self, 'saved_sessions'):
            self.saved_sessions = {}
            
        if mode == 'cli':
            return self._run_cli()
        elif mode == 'web':
            return self._run_web()
        elif mode == 'gui':
            return self._run_gui()
    
    def _run_cli(self):
        """CLI interface for life counter"""
        print("\n🎮 Advanced Life Counter 🎮")
        print("Perfect for Magic: The Gathering, D&D, and other games!")
        
        while True:
            try:
                if self.session is None:
                    self._cli_setup_game()
                else:
                    self._cli_game_loop()
            except KeyboardInterrupt:
                print("\n\nThanks for using Advanced Life Counter! 🎮")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
    
    def _cli_setup_game(self):
        """Setup a new game session via CLI"""
        print("\n=== Game Setup ===")
        
        # Get number of players
        while True:
            try:
                num_players = int(input("Number of players (2-8): "))
                if 2 <= num_players <= 8:
                    break
                print("Please enter a number between 2 and 8.")
            except ValueError:
                print("Please enter a valid number.")
        
        self.session = GameSession(num_players)
        
        # Get player names
        player_names = []
        for i in range(num_players):
            name = input(f"Enter name for Player {i+1}: ").strip()
            if not name:
                name = f"Player {i+1}"
            player_names.append(name)
        
        # Show available counter types
        print("\n=== Available Counter Types ===")
        counter_list = list(self.session.counter_templates.keys())
        for i, counter in enumerate(counter_list, 1):
            template = self.session.counter_templates[counter]
            min_str = f"min: {template['min_val']}" if template['min_val'] is not None else "no min"
            max_str = f"max: {template['max_val']}" if template['max_val'] is not None else "no max"
            print(f"{i:2d}. {counter} (default: {template['value']}, {min_str}, {max_str})")
        
        # Select counters
        print("\nSelect counter types (enter numbers separated by spaces, or 'all' for all counters):")
        counter_input = input("Counters to use: ").strip()
        
        if counter_input.lower() == 'all':
            selected_counters = counter_list
        else:
            try:
                indices = [int(x) - 1 for x in counter_input.split()]
                selected_counters = [counter_list[i] for i in indices if 0 <= i < len(counter_list)]
            except (ValueError, IndexError):
                print("Invalid selection, using default counters (Life, Poison).")
                selected_counters = ['Life', 'Poison']
        
        if not selected_counters:
            selected_counters = ['Life']
        
        # Create players with selected counters
        self.session.create_players(player_names, selected_counters)
        
        print(f"\n✅ Game setup complete! Tracking {len(selected_counters)} counter types for {num_players} players.")
        print(f"Counters: {', '.join(selected_counters)}")
    
    def _cli_game_loop(self):
        """Main game loop for CLI"""
        while True:
            # Display current state
            print("\n" + "="*60)
            print(f"🎮 {self.session.session_name}")
            print("="*60)
            
            for player in self.session.players:
                if player.active:
                    print(f"\n👤 {player.name}:")
                    for counter_name, counter in player.counters.items():
                        bounds = ""
                        if counter.min_val is not None or counter.max_val is not None:
                            min_str = str(counter.min_val) if counter.min_val is not None else "∞"
                            max_str = str(counter.max_val) if counter.max_val is not None else "∞"
                            bounds = f" [{min_str}-{max_str}]"
                        print(f"  {counter_name}: {counter.value}{bounds}")
            
            # Show options
            print("\n=== Options ===")
            print("1. Modify counter")
            print("2. Set counter to specific value")
            print("3. Reset all counters")
            print("4. Add custom counter")
            print("5. View counter history")
            print("6. New game")
            print("7. Exit")
            
            choice = input("\nChoose option (1-7): ").strip()
            
            if choice == '1':
                self._cli_modify_counter()
            elif choice == '2':
                self._cli_set_counter()
            elif choice == '3':
                self._cli_reset_counters()
            elif choice == '4':
                self._cli_add_custom_counter()
            elif choice == '5':
                self._cli_view_history()
            elif choice == '6':
                self.session = None
                break
            elif choice == '7':
                return
            else:
                print("Invalid choice. Please select 1-7.")
    
    def _cli_modify_counter(self):
        """Modify a counter value"""
        # Select player
        print("\nSelect player:")
        for i, player in enumerate(self.session.players):
            if player.active:
                print(f"{i+1}. {player.name}")
        
        try:
            player_idx = int(input("Player number: ")) - 1
            player = self.session.players[player_idx]
        except (ValueError, IndexError):
            print("Invalid player selection.")
            return
        
        # Select counter
        print(f"\nSelect counter for {player.name}:")
        counter_names = list(player.counters.keys())
        for i, name in enumerate(counter_names):
            counter = player.counters[name]
            print(f"{i+1}. {name}: {counter.value}")
        
        try:
            counter_idx = int(input("Counter number: ")) - 1
            counter_name = counter_names[counter_idx]
        except (ValueError, IndexError):
            print("Invalid counter selection.")
            return
        
        # Get modification amount
        try:
            amount = int(input(f"Amount to add/subtract (+ or -): "))
            new_value = player.modify_counter(counter_name, amount)
            print(f"✅ {player.name}'s {counter_name} is now {new_value}")
        except ValueError:
            print("Invalid amount. Please enter a number.")
    
    def _cli_set_counter(self):
        """Set counter to specific value"""
        # Similar to modify but sets absolute value
        print("\nSelect player:")
        for i, player in enumerate(self.session.players):
            if player.active:
                print(f"{i+1}. {player.name}")
        
        try:
            player_idx = int(input("Player number: ")) - 1
            player = self.session.players[player_idx]
        except (ValueError, IndexError):
            print("Invalid player selection.")
            return
        
        print(f"\nSelect counter for {player.name}:")
        counter_names = list(player.counters.keys())
        for i, name in enumerate(counter_names):
            counter = player.counters[name]
            print(f"{i+1}. {name}: {counter.value}")
        
        try:
            counter_idx = int(input("Counter number: ")) - 1
            counter_name = counter_names[counter_idx]
        except (ValueError, IndexError):
            print("Invalid counter selection.")
            return
        
        try:
            value = int(input(f"Set {counter_name} to: "))
            new_value = player.set_counter(counter_name, value)
            print(f"✅ {player.name}'s {counter_name} set to {new_value}")
        except ValueError:
            print("Invalid value. Please enter a number.")
    
    def _cli_reset_counters(self):
        """Reset all counters to initial values"""
        confirm = input("Reset all counters for all players? (y/N): ").lower()
        if confirm == 'y':
            self.session.reset_game()
            print("✅ All counters reset to initial values.")
    
    def _cli_add_custom_counter(self):
        """Add a custom counter type"""
        name = input("Counter name: ").strip()
        if not name:
            print("Counter name cannot be empty.")
            return
        
        try:
            value = int(input(f"Initial value for {name}: "))
            
            min_input = input("Minimum value (press Enter for no minimum): ").strip()
            min_val = int(min_input) if min_input else None
            
            max_input = input("Maximum value (press Enter for no maximum): ").strip()
            max_val = int(max_input) if max_input else None
            
            # Add to all players
            for player in self.session.players:
                player.add_counter(name, value, min_val, max_val)
            
            print(f"✅ Added {name} counter to all players.")
            
        except ValueError:
            print("Invalid input. Please enter valid numbers.")
    
    def _cli_view_history(self):
        """View counter history for a player"""
        print("\nSelect player:")
        for i, player in enumerate(self.session.players):
            if player.active:
                print(f"{i+1}. {player.name}")
        
        try:
            player_idx = int(input("Player number: ")) - 1
            player = self.session.players[player_idx]
        except (ValueError, IndexError):
            print("Invalid player selection.")
            return
        
        print(f"\n📈 History for {player.name}:")
        for counter_name, counter in player.counters.items():
            print(f"{counter_name}: {' → '.join(map(str, counter.history))}")
    
    def _run_web(self):
        """Web interface - returns None to use template"""
        return None
    
    def _run_gui(self):
        """GUI interface for life counter"""
        try:
            from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                                       QPushButton, QLabel, QSpinBox, QLineEdit, QComboBox,
                                       QMessageBox, QDialog, QGridLayout, QColorDialog,
                                       QCheckBox, QScrollArea, QFrame)
            from PyQt5.QtCore import Qt
            from PyQt5.QtGui import QFont
            
            app = QApplication.instance() or QApplication([])
            
            if self.session is None:
                self._gui_setup_game()
            else:
                self._gui_game_window()
                
        except ImportError:
            print("PyQt5 not available. GUI mode requires PyQt5.")
    
    def _gui_setup_game(self):
        """GUI game setup dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QSpinBox, QLabel, QLineEdit, QCheckBox
        
        dialog = QDialog()
        dialog.setWindowTitle("Advanced Life Counter - Setup")
        dialog.setFixedSize(500, 600)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🎮 Advanced Life Counter Setup")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Number of players
        players_layout = QHBoxLayout()
        players_layout.addWidget(QLabel("Number of players:"))
        players_spinbox = QSpinBox()
        players_spinbox.setRange(2, 8)
        players_spinbox.setValue(2)
        players_layout.addWidget(players_spinbox)
        layout.addLayout(players_layout)
        
        # Player names (will be populated dynamically)
        names_widget = QWidget()
        names_layout = QVBoxLayout(names_widget)
        player_name_inputs = []
        
        def update_player_names():
            # Clear existing inputs
            for i in reversed(range(names_layout.count())):
                names_layout.itemAt(i).widget().setParent(None)
            player_name_inputs.clear()
            
            # Add new inputs
            for i in range(players_spinbox.value()):
                name_input = QLineEdit()
                name_input.setPlaceholderText(f"Player {i+1} name")
                names_layout.addWidget(name_input)
                player_name_inputs.append(name_input)
        
        players_spinbox.valueChanged.connect(update_player_names)
        update_player_names()  # Initial setup
        
        layout.addWidget(QLabel("Player names:"))
        layout.addWidget(names_widget)
        
        # Counter selection
        layout.addWidget(QLabel("Select counter types:"))
        
        self.session = GameSession()  # Temporary session for templates
        counter_checkboxes = {}
        
        for counter_name, template in self.session.counter_templates.items():
            checkbox = QCheckBox(f"{counter_name} (default: {template['value']})")
            if counter_name in ['Life', 'Poison']:  # Default selections
                checkbox.setChecked(True)
            counter_checkboxes[counter_name] = checkbox
            layout.addWidget(checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        start_button = QPushButton("Start Game")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(start_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        def start_game():
            # Get player names
            names = []
            for input_widget in player_name_inputs:
                name = input_widget.text().strip()
                if not name:
                    name = input_widget.placeholderText()
                names.append(name)
            
            # Get selected counters
            selected_counters = []
            for counter_name, checkbox in counter_checkboxes.items():
                if checkbox.isChecked():
                    selected_counters.append(counter_name)
            
            if not selected_counters:
                QMessageBox.warning(dialog, "Warning", "Please select at least one counter type.")
                return
            
            # Create session
            self.session.create_players(names, selected_counters)
            dialog.accept()
            self._gui_game_window()
        
        start_button.clicked.connect(start_game)
        cancel_button.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def _gui_game_window(self):
        """Main GUI game window"""
        from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                   QPushButton, QLabel, QSpinBox, QGridLayout, QFrame)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        window = QMainWindow()
        window.setWindowTitle(f"Advanced Life Counter - {self.session.session_name}")
        window.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        reset_button = QPushButton("Reset All")
        new_game_button = QPushButton("New Game")
        controls_layout.addWidget(reset_button)
        controls_layout.addWidget(new_game_button)
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)
        
        # Players grid
        players_widget = QWidget()
        grid_layout = QGridLayout(players_widget)
        
        # Calculate grid dimensions
        num_players = len(self.session.players)
        cols = min(3, num_players)
        rows = (num_players + cols - 1) // cols
        
        for i, player in enumerate(self.session.players):
            row = i // cols
            col = i % cols
            
            player_frame = self._create_player_widget(player)
            grid_layout.addWidget(player_frame, row, col)
        
        main_layout.addWidget(players_widget)
        
        # Connect buttons
        def reset_all():
            self.session.reset_game()
            window.close()
            self._gui_game_window()  # Refresh window
        
        def new_game():
            self.session = None
            window.close()
            self._gui_setup_game()
        
        reset_button.clicked.connect(reset_all)
        new_game_button.clicked.connect(new_game)
        
        window.show()
    
    def _create_player_widget(self, player):
        """Create a widget for a single player"""
        from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox
        from PyQt5.QtCore import Qt
        
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("QFrame { border: 2px solid #ddd; border-radius: 10px; padding: 5px; }")
        
        layout = QVBoxLayout(frame)
        
        # Player name
        name_label = QLabel(f"👤 {player.name}")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        layout.addWidget(name_label)
        
        # Counters
        for counter_name, counter in player.counters.items():
            counter_layout = QHBoxLayout()
            
            # Counter name and value
            counter_label = QLabel(f"{counter_name}: {counter.value}")
            counter_label.setStyleSheet(f"color: {counter.color}; font-weight: bold;")
            counter_layout.addWidget(counter_label)
            
            # Modify buttons
            minus_btn = QPushButton("-")
            minus_btn.setFixedSize(30, 30)
            plus_btn = QPushButton("+")
            plus_btn.setFixedSize(30, 30)
            
            # Spinbox for custom amounts
            amount_spinbox = QSpinBox()
            amount_spinbox.setRange(-999, 999)
            amount_spinbox.setValue(1)
            amount_spinbox.setFixedWidth(60)
            
            counter_layout.addWidget(minus_btn)
            counter_layout.addWidget(amount_spinbox)
            counter_layout.addWidget(plus_btn)
            
            layout.addLayout(counter_layout)
            
            # Connect buttons
            def make_modify_func(p, c_name, amount_widget, label_widget):
                def modify_positive():
                    amount = amount_widget.value()
                    new_val = p.modify_counter(c_name, amount)
                    counter_obj = p.get_counter(c_name)
                    label_widget.setText(f"{c_name}: {new_val}")
                
                def modify_negative():
                    amount = -amount_widget.value()
                    new_val = p.modify_counter(c_name, amount)
                    counter_obj = p.get_counter(c_name)
                    label_widget.setText(f"{c_name}: {new_val}")
                
                return modify_positive, modify_negative
            
            plus_func, minus_func = make_modify_func(player, counter_name, amount_spinbox, counter_label)
            plus_btn.clicked.connect(plus_func)
            minus_btn.clicked.connect(minus_func)
        
        return frame
        
