# EVE Online API Tool Plugin

A comprehensive EVE Online ESI API integration plugin for the Modular Portfolio system. This plugin provides secure authentication, categorized endpoint access, and multi-interface support (CLI, Web, GUI) for interacting with the EVE Online API.

## Features

### 🔐 Secure Authentication
- **OAuth2 Flow**: Complete OAuth2 authentication using EVE Online SSO
- **Multi-Character Support**: Manage multiple character authentications simultaneously
- **Token Management**: Automatic token refresh and secure local storage
- **Scope Separation**: Clear distinction between public and private API endpoints

### 🚀 Comprehensive API Coverage
- **Character Information**: Basic info, skills, location, assets, corporation history
- **Market & Trading**: Orders, prices, market data, transaction history
- **Assets & Inventory**: Character and corporation assets, locations, names
- **Fleet Operations**: Fleet info, member management, operations
- **Universe Data**: Systems, stations, structures, regions, types
- **Combat & PvP**: Killmails, wars, sovereignty information
- **Communication**: Mail, notifications, calendar events, contacts
- **Corporation**: Corporate data, members, roles, structures

### 🖥️ Multi-Interface Support
- **CLI Interface**: Full-featured command-line interface with interactive menus
- **Web Interface**: Modern responsive web UI with tabbed categories
- **GUI Interface**: PyQt5-based desktop application with advanced features

### 🛡️ Security & Privacy
- **Local Storage**: All tokens stored locally in encrypted format
- **No Data Transmission**: No sensitive data transmitted to external servers
- **Scope Control**: Fine-grained permission control via ESI scopes
- **Secure Configuration**: Protected API credentials storage

## Installation

### Prerequisites
1. **EVE Online API Utility Library**:
   ```bash
   pip install eveonline-api-util
   ```
   Or from source:
   ```bash
   git clone https://github.com/DrIncognito/EveOnline_API_Util.git
   cd EveOnline_API_Util
   pip install -e .
   ```

2. **Optional Dependencies**:
   ```bash
   pip install PyQt5  # For GUI interface
   pip install requests  # For HTTP requests
   ```

### EVE Application Setup
1. Visit [EVE Developers](https://developers.eveonline.com/applications)
2. Click "Create New Application"
3. Fill in application details:
   - **Name**: Your application name
   - **Description**: Brief description
   - **Callback URL**: `http://localhost:8000/callback`
4. Select required scopes (see Scopes section below)
5. Note your **Client ID** and **Client Secret**

## Usage

### Command Line Interface (CLI)
```bash
# From the modular portfolio CLI
python -m modular_portfolio.cli

# Select EVE Online plugin and CLI mode
```

The CLI provides an interactive menu system with the following options:
1. **Authentication**: Manage character authentications
2. **Character Operations**: Access character-specific data
3. **Market & Trading**: Market data and trading information
4. **Assets & Inventory**: Asset management and inventory
5. **Fleet Operations**: Fleet management and operations
6. **Universe Data**: Public universe information
7. **Configuration**: API credentials and settings

### Web Interface
1. Start the Flask web server:
   ```bash
   python -m modular_portfolio.flask_app.app
   ```
2. Navigate to `http://localhost:5000/tool/EveOnline`
3. Configure API credentials if not already done
4. Authenticate characters as needed
5. Use the tabbed interface to access different API categories

### GUI Interface
```bash
# Launch GUI mode through the modular portfolio
python -m modular_portfolio.gui.dashboard

# Or directly run the EVE Online plugin in GUI mode
```

## Configuration

### Initial Setup
1. **Web Interface**: Use the configuration modal in the web interface
2. **CLI Interface**: Use the configuration menu option
3. **Manual Configuration**: Edit `~/.eve_portfolio/config.json`

### Configuration File Format
```json
{
  "client_id": "your_eve_application_client_id",
  "client_secret": "your_eve_application_client_secret",
  "redirect_uri": "http://localhost:8000/callback",
  "scopes": [
    "esi-characters.read_characters.v1",
    "esi-characters.read_corporation_history.v1",
    "esi-wallet.read_character_wallet.v1",
    "esi-assets.read_assets.v1",
    "esi-location.read_location.v1",
    "esi-skills.read_skills.v1",
    "esi-fleets.read_fleet.v1",
    "esi-markets.read_character_orders.v1"
  ]
}
```

## API Scopes

### Public Scopes (No Authentication Required)
- Universe data (systems, stations, market prices)
- Server status information
- Market group information
- General game data

### Private Scopes (Authentication Required)
- `esi-characters.read_characters.v1` - Basic character information
- `esi-characters.read_corporation_history.v1` - Corporation history
- `esi-wallet.read_character_wallet.v1` - Wallet balance and transactions
- `esi-assets.read_assets.v1` - Character assets
- `esi-location.read_location.v1` - Current location
- `esi-skills.read_skills.v1` - Character skills
- `esi-fleets.read_fleet.v1` - Fleet information
- `esi-markets.read_character_orders.v1` - Market orders

## API Categories

### Character
- **Basic Info**: Public character information and portrait
- **Corporation History**: Character's corporation membership history
- **Attributes**: Character attributes and implants
- **Skills**: Character skills and skill queue
- **Location**: Current location and ship information
- **Contacts**: Character contacts and standings

### Market & Trading
- **Character Orders**: Active market orders
- **Order History**: Historical market orders
- **Market Prices**: Current market prices
- **Market Groups**: Market group information
- **Region Orders**: Regional market data

### Assets & Inventory
- **Character Assets**: All character assets
- **Asset Locations**: Asset location details
- **Asset Names**: Custom asset names
- **Corporation Assets**: Corporation assets (if roles permit)
- **Blueprints**: Blueprint information

### Fleet Operations
- **Fleet Info**: Current fleet information
- **Fleet Members**: Fleet member list and roles
- **Fleet Management**: Fleet invitation and management
- **Wing Operations**: Wing-level operations
- **Squad Operations**: Squad-level operations

### Universe Data
- **Systems**: Solar system information
- **Stations**: Station data and services
- **Structures**: Player-owned structures
- **Regions**: Region information
- **Types**: Item type information

### Combat & PvP
- **Killmails**: Character and corporation killmails
- **Wars**: Active wars and war history
- **Sovereignty**: Sovereignty information

### Communication
- **Mail**: Character mail and mailing lists
- **Notifications**: Game notifications
- **Calendar Events**: Calendar events and invitations
- **Contacts**: Contact management

## Security Considerations

### Token Storage
- Tokens are stored locally in `~/.eve_portfolio/tokens.json`
- Files are created with restricted permissions (600)
- Tokens are automatically refreshed when needed

### API Credentials
- Never commit API credentials to version control
- Use environment variables or secure configuration files
- Regularly rotate API credentials for security

### Network Security
- All API calls use HTTPS
- No sensitive data is transmitted to third parties
- Local-only processing of all API responses

## Error Handling

The plugin provides comprehensive error handling for:
- **Authentication Errors**: Invalid tokens, expired authentication
- **Rate Limiting**: ESI API rate limit management
- **Network Errors**: Connection timeouts, server errors
- **Data Validation**: Invalid parameters, malformed responses
- **Permission Errors**: Insufficient scopes, access denied

## Troubleshooting

### Common Issues

1. **"EVE API library not available"**
   - Install the EVE Online API Utility library: `pip install eveonline-api-util`

2. **"Authentication not initialized"**
   - Configure your API credentials through the configuration interface

3. **"Authentication failed"**
   - Check your Client ID and Client Secret
   - Ensure the callback URL matches your EVE application settings
   - Verify the scopes are properly configured

4. **"Token expired"**
   - Re-authenticate the character
   - Check your internet connection for automatic token refresh

5. **"Permission denied"**
   - Ensure the character has the required scopes
   - Re-authenticate with the correct permissions

### Debug Mode
Enable debug logging by setting the environment variable:
```bash
export LOG_LEVEL=DEBUG
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This plugin is part of the Modular Portfolio project and follows the same license terms.

## Support

- **Issues**: Use the GitHub Issues system
- **EVE Online API**: [ESI Documentation](https://esi.evetech.net/ui/)
- **EVE Developers**: [EVE Online Third-Party Development](https://developers.eveonline.com/)

## Changelog

### Version 1.0.0
- Initial release
- Complete EVE Online ESI API integration
- Multi-interface support (CLI, Web, GUI)
- Secure OAuth2 authentication
- Comprehensive endpoint coverage
- Token management and automatic refresh
- Categorized API access
- Error handling and logging

---

**Fly safe, capsuleer!** o7
