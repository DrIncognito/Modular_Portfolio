# Advanced Life Counter Plugin

A highly customizable life counter plugin for tracking multiple players with various counter types. Perfect for Magic: The Gathering, D&D, and other tabletop games!

## Features

🎮 **Multi-Player Support**: Track 2-8 players simultaneously
⚙️ **Highly Customizable**: Create custom counters with names, colors, and constraints
🎯 **Constraint System**: Set minimum and maximum values for any counter
📊 **History Tracking**: View the complete history of counter changes
🎨 **Color-Coded**: Each counter type has its own color for easy identification
🔄 **Flexible Operations**: Modify, set, or reset counters individually or in bulk
💻 **Multi-Interface**: Works in CLI, Web, and GUI modes

## Default Counter Types

The plugin comes with 8 pre-configured counter types commonly used in tabletop gaming:

- **Life** (20, min: 0) - Red color, standard life tracking
- **Poison** (0, min: 0, max: 10) - Green color, poison counter tracking  
- **Energy** (0, min: 0) - Yellow color, energy resource tracking
- **Experience** (0) - Blue color, experience points
- **Mana** (0, min: 0) - Purple color, mana pool tracking
- **Commander Damage** (0, min: 0, max: 21) - Orange color, Commander format
- **Tokens** (0, min: 0) - Teal color, creature tokens
- **Storm Count** (0, min: 0) - Gray color, storm mechanic

## Usage

### CLI Mode
```bash
# Start the plugin in CLI mode
python start.py --addon AdvancedLifeCounter --mode cli
```

**CLI Features:**
- Interactive setup with player count and counter selection
- Real-time counter modification with +/- operations
- Set counters to specific values
- View counter history for any player
- Add custom counter types during gameplay
- Reset all counters or start a new game

### Web Mode
```bash
# Start the plugin in web mode
python start.py --addon AdvancedLifeCounter --mode web
```

**Web Features:**
- Modern, responsive interface
- Color-coded counter displays
- Click-to-modify counters
- Visual feedback with animations
- Real-time updates across all players

### GUI Mode
```bash
# Start the plugin in GUI mode  
python start.py --addon AdvancedLifeCounter --mode gui
```

**GUI Features:**
- Native desktop interface using PyQt5
- Grid layout for multiple players
- Spinbox controls for precise adjustments
- Visual player cards with color-coded counters

## Game Setup

1. **Choose Player Count**: Select 2-8 players
2. **Enter Player Names**: Customize each player's display name
3. **Select Counter Types**: Choose from default counters or add custom ones
4. **Start Playing**: Begin tracking with full customization

## Customization Options

### Counter Configuration
- **Name**: Custom counter names (e.g., "Health", "Shield", "Ammo")
- **Initial Value**: Starting value for new games
- **Minimum Value**: Optional lower bound (prevents going below)
- **Maximum Value**: Optional upper bound (prevents going above)
- **Color**: Visual color coding for easy identification

### Player Management
- Individual player tracking with unique IDs
- Player activation/deactivation
- Bulk operations across all players
- History tracking per player

## Advanced Features

### Counter History
Every counter maintains a complete history of value changes, allowing you to:
- Review past modifications
- Track game progression
- Identify patterns or mistakes
- Revert to previous states (manual)

### Constraint System
Set intelligent bounds on your counters:
- **Life**: Minimum 0 (can't go negative)
- **Poison**: Maximum 10 (game ends at 10)
- **Commander Damage**: Maximum 21 (lethal threshold)
- **Custom**: Set any min/max combination

### Bulk Operations
Efficiently manage multiple counters:
- Reset all counters to initial values
- Add new counter types to all players
- Modify multiple counters simultaneously

## Perfect For

- **Magic: The Gathering**: Life, poison, energy, commander damage
- **Dungeons & Dragons**: Hit points, spell slots, experience
- **Board Games**: Victory points, resources, turn tracking
- **Custom Games**: Any numeric tracking needs

## Technical Details

- **Language**: Python 3.x
- **GUI Framework**: PyQt5 (optional)
- **Web Framework**: Flask integration
- **Data Persistence**: JSON serialization
- **Architecture**: Object-oriented with Counter, Player, and GameSession classes

## Installation

The plugin is included with the Modular Portfolio system and requires no additional dependencies for CLI mode. For GUI mode, PyQt5 is required:

```bash
pip install PyQt5
```

## Examples

### Magic: The Gathering Game
```
Players: Alice, Bob, Charlie, Diana
Counters: Life (20), Poison (0), Energy (0), Commander Damage (0)
```

### D&D Session
```
Players: Warrior, Mage, Rogue, Cleric  
Counters: Health (varies), Spell Slots (varies), Experience (0)
```

### Custom Board Game
```
Players: Player 1, Player 2, Player 3
Counters: Victory Points (0), Resources (10), Actions (3)
```

Start tracking your game today with the Advanced Life Counter plugin! 🎮

## Example
See `addons/example_tool/` for a complete demo plugin.
