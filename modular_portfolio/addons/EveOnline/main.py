import os
import json
import logging
from typing import Dict, Any, Optional, List
import webbrowser
from urllib.parse import urlencode

from modular_portfolio.modular_core.interface import BasePlugin

# Try to import the EVE Online API utility library
try:
    from eveonline_api_util import EVEAuth, TokenManager, ESIClient, ESIEndpointManager
    from eveonline_api_util.endpoints import (
        CharacterEndpoint, WalletEndpoint, FleetEndpoint, MarketEndpoint,
        AssetsEndpoint, UniverseEndpoint, KillmailsEndpoint, LocationsEndpoint,
        CorporationEndpoint, AllianceEndpoint, ContractsEndpoint,
        IndustryEndpoint, MailEndpoint, SkillsEndpoint
    )
    EVE_API_AVAILABLE = True
except ImportError:
    print("WARNING: EveOnline API Util library not found. Please install it with: pip install eveonline-api-util")
    EVE_API_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EveOnlineManager:
    """
    Manager class for EVE Online API operations with secure authentication
    and categorized endpoint access.
    """
    
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.eve_portfolio")
        self.token_file = os.path.join(self.config_dir, "tokens.json")
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.auth = None
        self.client = None
        self.endpoint_manager = None
        self.token_manager = None
        
        # Initialize if EVE API is available
        if EVE_API_AVAILABLE:
            self._initialize_api()
    
    def _initialize_api(self):
        """Initialize the EVE API components, filtering scopes to only valid EVE SSO scopes."""
        try:
            config = self._load_config()
            # Load valid scopes from file
            valid_scopes_path = os.path.join(os.path.dirname(__file__), "valid_scopes.json")
            try:
                with open(valid_scopes_path, "r") as f:
                    valid_scopes = set(json.load(f))
            except Exception as e:
                logger.warning(f"Could not load valid_scopes.json: {e}")
                valid_scopes = set()
            # Filter config scopes to only valid ones
            config_scopes = config.get('scopes', [])
            filtered_scopes = [s for s in config_scopes if not valid_scopes or s in valid_scopes]
            if not filtered_scopes:
                logger.warning("No valid EVE SSO scopes found in config; using default minimal scope.")
                filtered_scopes = ["esi-characters.read_corporation_history.v1"]
            self.token_manager = TokenManager(self.token_file)
            self.auth = EVEAuth(
                client_id=config.get('client_id', ''),
                client_secret=config.get('client_secret', ''),
                redirect_uri=config.get('redirect_uri', 'http://127.0.0.1:5000/api/eve_online/auth_callback'),
                scopes=filtered_scopes,
                token_manager=self.token_manager
            )
            self.client = ESIClient(self.auth)
            self.endpoint_manager = ESIEndpointManager(
                client_id=config.get('client_id', ''),
                client_secret=config.get('client_secret', ''),
                redirect_uri=config.get('redirect_uri', 'http://127.0.0.1:5000/api/eve_online/auth_callback')
            )
        except Exception as e:
            logger.error(f"Failed to initialize EVE API: {e}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            'client_id': '',
            'client_secret': '',
            'redirect_uri': 'http://127.0.0.1:5000/api/eve_online/auth_callback',
            'scopes': [
                'esi-characters.read_characters.v1',
                'esi-characters.read_corporation_history.v1',
                'esi-wallet.read_character_wallet.v1',
                'esi-assets.read_assets.v1',
                'esi-location.read_location.v1',
                'esi-skills.read_skills.v1',
                'esi-fleets.read_fleet.v1',
                'esi-markets.read_character_orders.v1'
            ]
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
            return default_config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return default_config
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file and re-initialize API components"""
        try:
            # Ensure config directory exists
            os.makedirs(self.config_dir, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Re-initialize API components with new configuration
            if EVE_API_AVAILABLE:
                self._initialize_api()
                logger.info("API components re-initialized with new configuration")
                
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def reload_configuration(self):
        """Reload configuration and re-initialize API components"""
        if EVE_API_AVAILABLE:
            self._initialize_api()
            logger.info("Configuration reloaded and API components re-initialized")
    
    def get_categories(self) -> Dict[str, list]:
        """Get categorized list of available endpoints with docstrings and required args"""
        # This should be kept in sync with _route_endpoint_call
        return {
            'Character': [
                {'function_name': 'Basic Info', 'docstring': 'Get public character info (requires character ID).', 'required_args': ['character_id']},
                {'function_name': 'Portrait', 'docstring': 'Get character portrait (requires character ID).', 'required_args': ['character_id']},
                {'function_name': 'Corporation History', 'docstring': 'Get character corporation history.', 'required_args': ['character_id']},
                {'function_name': 'Attributes', 'docstring': 'Get character attributes and implants.', 'required_args': ['character_id']},
                {'function_name': 'Skills', 'docstring': 'Get character skills.', 'required_args': ['character_id']},
                {'function_name': 'Skill Queue', 'docstring': 'Get character skill queue.', 'required_args': ['character_id']},
                {'function_name': 'Location', 'docstring': 'Get current character location.', 'required_args': ['character_id']},
                {'function_name': 'Ship', 'docstring': 'Get current ship info.', 'required_args': ['character_id']},
                {'function_name': 'Contacts', 'docstring': 'Get character contacts and standings.', 'required_args': ['character_id']},
            ],
            'Corporation': [
                {'function_name': 'Corporation Info', 'docstring': 'Get public corporation info (requires corporation ID).', 'required_args': ['corporation_id']},
                {'function_name': 'Members', 'docstring': 'Get corporation members (requires character authentication).', 'required_args': ['character_id']},
                {'function_name': 'Roles', 'docstring': 'Get corporation roles.', 'required_args': ['character_id']},
                {'function_name': 'Structures', 'docstring': 'Get corporation structures.', 'required_args': ['character_id']},
                {'function_name': 'Wallet', 'docstring': 'Get corporation wallet info.', 'required_args': ['character_id']},
                {'function_name': 'Industry Jobs', 'docstring': 'Get corporation industry jobs.', 'required_args': ['character_id']},
                {'function_name': 'Contracts', 'docstring': 'Get corporation contracts.', 'required_args': ['character_id']},
            ],
            'Assets & Inventory': [
                {'function_name': 'Character Assets', 'docstring': 'Get all character assets.', 'required_args': ['character_id', 'page']},
                {'function_name': 'Asset Locations', 'docstring': 'Get asset location details.', 'required_args': ['character_id']},
                {'function_name': 'Asset Names', 'docstring': 'Get custom asset names.', 'required_args': ['character_id']},
                {'function_name': 'Corporation Assets', 'docstring': 'Get corporation assets.', 'required_args': ['character_id']},
                {'function_name': 'Blueprints', 'docstring': 'Get blueprint information.', 'required_args': ['character_id']},
            ],
            'Market & Trading': [
                {'function_name': 'Character Orders', 'docstring': 'Get active market orders for character.', 'required_args': ['character_id']},
                {'function_name': 'Order History', 'docstring': 'Get historical market orders.', 'required_args': ['character_id']},
                {'function_name': 'Market Prices', 'docstring': 'Get current market prices.', 'required_args': []},
                {'function_name': 'Market Groups', 'docstring': 'Get market group information.', 'required_args': []},
                {'function_name': 'Region Orders', 'docstring': 'Get regional market data (region_id required).', 'required_args': ['region_id']},
                {'function_name': 'Structure Markets', 'docstring': 'Get structure market data.', 'required_args': ['structure_id']},
            ],
            'Fleet Operations': [
                {'function_name': 'Fleet Info', 'docstring': 'Get current fleet information.', 'required_args': ['character_id']},
                {'function_name': 'Fleet Members', 'docstring': 'Get fleet member list.', 'required_args': ['fleet_id', 'character_id']},
                {'function_name': 'Fleet Management', 'docstring': 'Manage fleet invitations and settings.', 'required_args': ['fleet_id', 'character_id']},
                {'function_name': 'Wing Operations', 'docstring': 'Wing-level operations.', 'required_args': ['fleet_id', 'character_id']},
                {'function_name': 'Squad Operations', 'docstring': 'Squad-level operations.', 'required_args': ['fleet_id', 'character_id']},
            ],
            'Universe Data': [
                {'function_name': 'Systems', 'docstring': 'Get solar system information.', 'required_args': []},
                {'function_name': 'Stations', 'docstring': 'Get station data and services.', 'required_args': []},
                {'function_name': 'Structures', 'docstring': 'Get player-owned structures.', 'required_args': []},
                {'function_name': 'Types', 'docstring': 'Get item type information.', 'required_args': []},
                {'function_name': 'Regions', 'docstring': 'Get region information.', 'required_args': []},
                {'function_name': 'Constellations', 'docstring': 'Get constellation information.', 'required_args': []},
                {'function_name': 'Planets', 'docstring': 'Get planet information.', 'required_args': []},
            ],
            'Combat & PvP': [
                {'function_name': 'Killmails', 'docstring': 'Get character/corporation killmails (killmail_id, killmail_hash required).', 'required_args': ['killmail_id', 'killmail_hash']},
                {'function_name': 'Character Kills', 'docstring': 'Get recent character kills.', 'required_args': ['character_id']},
                {'function_name': 'Corporation Kills', 'docstring': 'Get recent corporation kills.', 'required_args': ['character_id']},
                {'function_name': 'Wars', 'docstring': 'Get active wars and war history.', 'required_args': []},
                {'function_name': 'Sovereignty', 'docstring': 'Get sovereignty information.', 'required_args': []},
            ],
            'Communication': [
                {'function_name': 'Mail', 'docstring': 'Get character mail and mailing lists.', 'required_args': ['character_id']},
                {'function_name': 'Mailing Lists', 'docstring': 'Get mailing lists.', 'required_args': ['character_id']},
                {'function_name': 'Notifications', 'docstring': 'Get game notifications.', 'required_args': ['character_id']},
                {'function_name': 'Calendar Events', 'docstring': 'Get calendar events and invitations.', 'required_args': ['character_id']},
                {'function_name': 'Contacts', 'docstring': 'Get contact management.', 'required_args': ['character_id']},
            ]
        }
    
    def authenticate(self, character_name: Optional[str] = None) -> Dict[str, Any]:
        """Simplified authentication flow: prompts for missing config, then authenticates."""
        if not EVE_API_AVAILABLE:
            return {'error': 'EVE API library not available'}

        config = self._load_config()
        # Prompt for missing config interactively
        if not config.get('client_id'):
            config['client_id'] = input("Enter EVE Online Client ID: ").strip()
        if not config.get('client_secret'):
            config['client_secret'] = input("Enter EVE Online Client Secret: ").strip()
        if not config.get('redirect_uri'):
            config['redirect_uri'] = input("Enter Redirect URI (default: http://127.0.0.1:5000/api/eve_online/auth_callback): ").strip() or "http://127.0.0.1:5000/api/eve_online/auth_callback"
        self.save_config(config)

        # Re-initialize auth with new config
        self._initialize_api()
        if not self.auth:
            return {'error': 'Authentication not initialized. Please check your credentials.'}

        try:
            # Check if any tokens exist
            if self.token_manager and self.token_manager.list_characters():
                print("You already have authenticated characters:")
                for char_id in self.token_manager.list_characters():
                    token = self.token_manager.get_token(char_id)
                    print(f"- {token.get('CharacterName', 'Unknown')} (ID: {char_id})")
                use_existing = input("Use existing authentication? (y/n): ").strip().lower()
                if use_existing == 'y':
                    return {'success': True, 'message': 'Using existing authentication.'}

            # Get authorization URL
            auth_url, state = self.auth.get_authorization_url()
            print(f"\nPlease authenticate in your browser.")
            print(f"If the browser didn't open, visit: {auth_url}")
            webbrowser.open(auth_url)
            callback_url = input("Enter the full callback URL after authentication: ")
            token = self.auth.handle_callback(callback_url, state)
            return {
                'success': True,
                'character_id': token.get('CharacterID'),
                'character_name': token.get('CharacterName'),
                'token': token
            }
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return {'error': str(e)}
    
    def get_authenticated_characters(self) -> List[Dict[str, Any]]:
        """Get list of authenticated characters"""
        if not self.token_manager:
            return []
        
        characters = []
        for char_id in self.token_manager.list_characters():
            token = self.token_manager.get_token(char_id)
            if token:
                characters.append({
                    'character_id': char_id,
                    'character_name': token.get('CharacterName', 'Unknown'),
                    'expires_at': token.get('ExpiresOn'),
                    'scopes': token.get('Scopes', [])
                })
        
        return characters
    
    def execute_endpoint(self, category: str, operation: str, character_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Execute a specific endpoint operation"""
        if not EVE_API_AVAILABLE:
            return {'error': 'EVE API library not available'}
        
        if not self.client:
            return {'error': 'API client not initialized'}
        
        try:
            # Route to appropriate endpoint based on category and operation
            return self._route_endpoint_call(category, operation, character_id, **kwargs)
            
        except Exception as e:
            logger.error(f"Endpoint execution failed: {e}")
            return {'error': str(e)}
    
    def _route_endpoint_call(self, category: str, operation: str, character_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Route endpoint calls to appropriate handlers"""
        
        # Determine if this is a public endpoint that doesn't require authentication
        private_categories = ['Assets & Inventory', 'Fleet Operations', 'Communication']
        character_private_ops = ['Corporation History', 'Skills', 'Skill Queue', 'Location', 'Ship', 'Contacts', 'Attributes']
        
        is_private = False
        if category in private_categories:
            is_private = True
        elif category == 'Character' and operation in character_private_ops:
            is_private = True
        elif category == 'Market & Trading' and operation in ['Character Orders', 'Order History']:
            is_private = True
        elif category == 'Corporation' and operation not in ['Corporation Info']:
            is_private = True
        elif category == 'Combat & PvP' and operation in ['Character Kills', 'Corporation Kills']:
            is_private = True
        
        # For private endpoints, check if we have authentication
        if is_private and not character_id:
            return {'error': f'{operation} requires character authentication. Please authenticate first.'}
        
        # For private endpoints, verify token exists
        if is_private and self.token_manager and not self.token_manager.get_token(character_id):
            return {'error': f'No valid token found for character {character_id}. Please re-authenticate.'}
        
        # Character endpoints (mostly private, but some public info)
        if category == 'Character':
            char_endpoint = CharacterEndpoint(self.client)
            
            if operation == 'Basic Info':
                # Public endpoint - works without auth, but needs character_id
                if not character_id:
                    return {'error': 'Character ID required for Basic Info. This is a public endpoint but requires a character ID to look up.'}
                return char_endpoint.get_character_public_info(int(character_id))
            elif operation == 'Portrait':
                # Public endpoint - works without auth, but needs character_id  
                if not character_id:
                    return {'error': 'Character ID required for Portrait. This is a public endpoint but requires a character ID to look up.'}
                return char_endpoint.get_character_portrait(int(character_id))
            elif operation == 'Corporation History':
                return char_endpoint.get_character_corporation_history(character_id)
            elif operation == 'Skills':
                return char_endpoint.get_character_skills(character_id)
            elif operation == 'Location':
                return char_endpoint.get_character_location(character_id)
            # Add more character operations...
        
        # Market endpoints (mostly public)
        elif category == 'Market & Trading':
            market_endpoint = MarketEndpoint(self.client)
            
            if operation == 'Character Orders':
                # Private endpoint
                if not character_id:
                    return {'error': 'Character Orders requires authentication'}
                return market_endpoint.get_character_orders(character_id)
            elif operation == 'Market Prices':
                # Public endpoint
                return market_endpoint.get_market_prices()
            elif operation == 'Market Groups':
                # Public endpoint
                return market_endpoint.get_market_groups()
            elif operation == 'Region Orders':
                # Public endpoint
                region_id = kwargs.get('region_id', 10000002)  # Default to The Forge
                return market_endpoint.get_market_orders(region_id)
            # Add more market operations...
        
        # Assets endpoints (all private)
        elif category == 'Assets & Inventory':
            assets_endpoint = AssetsEndpoint(self.client)
            
            if operation == 'Character Assets':
                return assets_endpoint.get_character_assets(character_id, kwargs.get('page', 1))
            # Add more asset operations...
        
        # Fleet endpoints (all private)
        elif category == 'Fleet Operations':
            fleet_endpoint = FleetEndpoint(self.client)
            
            if operation == 'Fleet Info':
                return fleet_endpoint.get_character_fleet_info(character_id)
            elif operation == 'Fleet Members':
                fleet_id = kwargs.get('fleet_id')
                if fleet_id:
                    return fleet_endpoint.get_fleet_members(fleet_id, character_id)
            # Add more fleet operations...
        
        # Universe endpoints (all public)
        elif category == 'Universe Data':
            universe_endpoint = UniverseEndpoint(self.client)
            
            if operation == 'Systems':
                return universe_endpoint.get_universe_systems()
            elif operation == 'Stations':
                return universe_endpoint.get_universe_stations()
            elif operation == 'Regions':
                return universe_endpoint.get_universe_regions()
            elif operation == 'Constellations':
                return universe_endpoint.get_universe_constellations()
            elif operation == 'Types':
                return universe_endpoint.get_universe_types()
            # Add more universe operations...
        
        # Corporation endpoints (mixed public/private)
        elif category == 'Corporation':
            corp_endpoint = CorporationEndpoint(self.client)
            
            if operation == 'Corporation Info':
                # Public endpoint
                corp_id = kwargs.get('corporation_id')
                if corp_id:
                    return corp_endpoint.get_corporation_info(corp_id)
                else:
                    return {'error': 'Corporation ID required'}
            elif operation == 'Members':
                # Private endpoint
                if not character_id:
                    return {'error': 'Corporation Members requires authentication'}
                return corp_endpoint.get_corporation_members(character_id)
            # Add more corporation operations...
        
        # Combat & PvP endpoints (mostly public)
        elif category == 'Combat & PvP':
            killmail_endpoint = KillmailsEndpoint(self.client)
            
            if operation == 'Killmails':
                # Public endpoint with killmail ID
                killmail_id = kwargs.get('killmail_id')
                killmail_hash = kwargs.get('killmail_hash')
                if killmail_id and killmail_hash:
                    return killmail_endpoint.get_killmail_details(killmail_id, killmail_hash)
                else:
                    return {'error': 'Killmail ID and hash required'}
            elif operation == 'Character Kills':
                # Private endpoint
                if not character_id:
                    return {'error': 'Character Kills requires authentication'}
                return killmail_endpoint.get_character_recent_kills(character_id)
            # Add more killmail operations...
        
        return {'error': f'Unknown operation: {category} -> {operation}'}

class EveOnline(BasePlugin):
    def __init__(self):
        self.manager = EveOnlineManager()
    
    def run(self, mode: str):
        """Run the EVE Online plugin in the specified mode"""
        if not EVE_API_AVAILABLE:
            print("\nERROR: EVE Online API Utility library is not installed.")
            print("Please install it with: pip install eveonline-api-util")
            print("Or from source: https://github.com/DrIncognito/EveOnline_API_Util")
            return None
        
        if mode == 'cli':
            return self._run_cli()
        elif mode == 'web':
            return self._run_web()
        elif mode == 'gui':
            return self._run_gui()
        else:
            print(f"Unknown mode: {mode}")
            return None
    
    def _run_cli(self):
        """Run the CLI interface"""
        print("\n" + "="*60)
        print("        EVE ONLINE API TOOL - CLI INTERFACE")
        print("="*60)
        
        while True:
            print("\nMain Menu:")
            print("1. Authentication")
            print("2. Character Operations")
            print("3. Market & Trading")
            print("4. Assets & Inventory")
            print("5. Fleet Operations")
            print("6. Universe Data")
            print("7. Configuration")
            print("8. Exit")
            
            choice = input("\nSelect option (1-8): ").strip()
            
            if choice == '1':
                self._cli_authentication()
            elif choice == '2':
                self._cli_character_operations()
            elif choice == '3':
                self._cli_market_operations()
            elif choice == '4':
                self._cli_assets_operations()
            elif choice == '5':
                self._cli_fleet_operations()
            elif choice == '6':
                self._cli_universe_operations()
            elif choice == '7':
                self._cli_configuration()
            elif choice == '8':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _cli_authentication(self):
        """Handle CLI authentication operations"""
        print("\n--- Authentication ---")
        print("1. Authenticate new character")
        print("2. List authenticated characters")
        print("3. Remove character authentication")
        
        choice = input("Select option (1-3): ").strip()
        
        if choice == '1':
            result = self.manager.authenticate()
            if 'error' in result:
                print(f"Authentication failed: {result['error']}")
            else:
                print(f"Successfully authenticated {result['character_name']} (ID: {result['character_id']})")
        
        elif choice == '2':
            characters = self.manager.get_authenticated_characters()
            if not characters:
                print("No authenticated characters found.")
            else:
                print("\nAuthenticated Characters:")
                for char in characters:
                    print(f"- {char['character_name']} (ID: {char['character_id']})")
                    print(f"  Expires: {char['expires_at']}")
                    print(f"  Scopes: {len(char['scopes'])} permissions")
        
        elif choice == '3':
            characters = self.manager.get_authenticated_characters()
            if not characters:
                print("No authenticated characters to remove.")
                return
            
            print("Select character to remove:")
            for i, char in enumerate(characters, 1):
                print(f"{i}. {char['character_name']}")
            
            try:
                idx = int(input("Enter number: ")) - 1
                char_id = characters[idx]['character_id']
                self.manager.token_manager.remove_token(char_id)
                print(f"Removed authentication for {characters[idx]['character_name']}")
            except (ValueError, IndexError):
                print("Invalid selection.")
    
    def _cli_character_operations(self):
        """Handle CLI character operations"""
        characters = self.manager.get_authenticated_characters()
        if not characters:
            print("No authenticated characters. Please authenticate first.")
            return
        
        print("\nSelect character:")
        for i, char in enumerate(characters, 1):
            print(f"{i}. {char['character_name']}")
        
        try:
            idx = int(input("Enter number: ")) - 1
            character_id = characters[idx]['character_id']
            char_name = characters[idx]['character_name']
        except (ValueError, IndexError):
            print("Invalid selection.")
            return
        
        print(f"\nCharacter operations for {char_name}:")
        print("1. Basic Info")
        print("2. Skills")
        print("3. Location")
        print("4. Corporation History")
        
        choice = input("Select operation (1-4): ").strip()
        
        operations = {
            '1': 'Basic Info',
            '2': 'Skills',
            '3': 'Location',
            '4': 'Corporation History'
        }
        
        if choice in operations:
            result = self.manager.execute_endpoint('Character', operations[choice], character_id)
            self._print_result(result)
        else:
            print("Invalid choice.")
    
    def _cli_market_operations(self):
        """Handle CLI market operations - public endpoints"""
        print("\nMarket Operations:")
        print("1. Market Prices")
        print("2. Market Groups")
        print("3. Character Orders (requires auth)")
        
        choice = input("Select operation (1-3): ").strip()
        
        if choice == '1':
            result = self.manager.execute_endpoint('Market & Trading', 'Market Prices')
            self._print_result(result)
        elif choice == '2':
            result = self.manager.execute_endpoint('Market & Trading', 'Market Groups')
            self._print_result(result)
        elif choice == '3':
            characters = self.manager.get_authenticated_characters()
            if not characters:
                print("Authentication required for character orders.")
                return
            
            print("Select character:")
            for i, char in enumerate(characters, 1):
                print(f"{i}. {char['character_name']}")
            
            try:
                idx = int(input("Enter number: ")) - 1
                character_id = characters[idx]['character_id']
                result = self.manager.execute_endpoint('Market & Trading', 'Character Orders', character_id)
                self._print_result(result)
            except (ValueError, IndexError):
                print("Invalid selection.")
    
    def _cli_assets_operations(self):
        """Handle CLI assets operations"""
        characters = self.manager.get_authenticated_characters()
        if not characters:
            print("Authentication required for asset operations.")
            return
        
        print("Select character:")
        for i, char in enumerate(characters, 1):
            print(f"{i}. {char['character_name']}")
        
        try:
            idx = int(input("Enter number: ")) - 1
            character_id = characters[idx]['character_id']
            char_name = characters[idx]['character_name']
        except (ValueError, IndexError):
            print("Invalid selection.")
            return
        
        result = self.manager.execute_endpoint('Assets & Inventory', 'Character Assets', character_id)
        self._print_result(result)
    
    def _cli_fleet_operations(self):
        """Handle CLI fleet operations"""
        characters = self.manager.get_authenticated_characters()
        if not characters:
            print("Authentication required for fleet operations.")
            return
        
        print("Select character:")
        for i, char in enumerate(characters, 1):
            print(f"{i}. {char['character_name']}")
        
        try:
            idx = int(input("Enter number: ")) - 1
            character_id = characters[idx]['character_id']
            char_name = characters[idx]['character_name']
        except (ValueError, IndexError):
            print("Invalid selection.")
            return
        
        result = self.manager.execute_endpoint('Fleet Operations', 'Fleet Info', character_id)
        self._print_result(result)
    
    def _cli_universe_operations(self):
        """Handle CLI universe operations - public endpoints"""
        print("\nUniverse Operations:")
        print("1. Systems")
        print("2. Stations")
        print("3. Regions")
        
        choice = input("Select operation (1-3): ").strip()
        
        operations = {
            '1': 'Systems',
            '2': 'Stations',
            '3': 'Regions'
        }
        
        if choice in operations:
            result = self.manager.execute_endpoint('Universe Data', operations[choice])
            # Limit output for large datasets
            if isinstance(result, list) and len(result) > 10:
                print(f"Found {len(result)} items. Showing first 10:")
                self._print_result(result[:10])
            else:
                self._print_result(result)
        else:
            print("Invalid choice.")
    
    def _cli_configuration(self):
        """Handle CLI configuration"""
        print("\n--- Configuration ---")
        print("1. View current configuration")
        print("2. Set API credentials")
        print("3. Set scopes")
        print("4. Test configuration")
        
        choice = input("Select option (1-4): ").strip()
        
        if choice == '1':
            config = self.manager._load_config()
            print("\nCurrent Configuration:")
            print(f"Client ID: {'*' * min(len(config.get('client_id', '')), 20) if config.get('client_id') else 'Not set'}")
            print(f"Client Secret: {'*' * min(len(config.get('client_secret', '')), 20) if config.get('client_secret') else 'Not set'}")
            print(f"Redirect URI: {config.get('redirect_uri', 'Not set')}")
            print(f"Scopes: {len(config.get('scopes', []))} configured")
            
            # Show configuration status
            if not config.get('client_id') or not config.get('client_secret'):
                print("\n⚠️ WARNING: API credentials are not configured!")
                print("  - Get your credentials from: https://developers.eveonline.com/applications")
                print("  - Create a new application with appropriate scopes")
                print("  - Use option 2 to set your credentials")
        
        elif choice == '2':
            print("\n" + "="*60)
            print("      EVE ONLINE API CREDENTIALS SETUP")
            print("="*60)
            print("\nTo use this tool, you need to create an EVE Online application:")
            print("1. Visit: https://developers.eveonline.com/applications")
            print("2. Click 'Create New Application'")
            print("3. Fill in the form:")
            print("   - Name: Your app name (e.g., 'My Portfolio Tool')")
            print("   - Description: Brief description")
            print("   - Connection Type: Authentication & API Access")
            print("   - Permissions: Select the scopes you need")
            print("   - Callback URL: http://127.0.0.1:5000/api/eve_online/auth_callback")
            print("4. Save and copy your Client ID and Client Secret")
            print("\n" + "-"*60)
            
            current_config = self.manager._load_config()
            
            # Client ID
            current_client_id = current_config.get('client_id', '')
            if current_client_id:
                print(f"\nCurrent Client ID: {current_client_id[:8]}{'*' * (len(current_client_id) - 8)}")
                use_current = input("Keep current Client ID? (y/n): ").strip().lower()
                if use_current == 'y':
                    client_id = current_client_id
                else:
                    client_id = input("Enter new Client ID: ").strip()
            else:
                print("\n📋 Client ID not configured")
                client_id = input("Enter Client ID (from your EVE application): ").strip()
                
            while not client_id:
                print("❌ Client ID is required!")
                client_id = input("Enter Client ID: ").strip()
            
            # Client Secret
            current_client_secret = current_config.get('client_secret', '')
            if current_client_secret:
                print(f"\nCurrent Client Secret: {'*' * 20}")
                use_current = input("Keep current Client Secret? (y/n): ").strip().lower()
                if use_current == 'y':
                    client_secret = current_client_secret
                else:
                    client_secret = input("Enter new Client Secret: ").strip()
            else:
                print("\n🔐 Client Secret not configured")
                client_secret = input("Enter Client Secret (from your EVE application): ").strip()
                
            while not client_secret:
                print("❌ Client Secret is required!")
                client_secret = input("Enter Client Secret: ").strip()
            
            # Redirect URI
            current_redirect = current_config.get('redirect_uri', 'http://127.0.0.1:5000/api/eve_online/auth_callback')
            print(f"\nCurrent Redirect URI: {current_redirect}")
            redirect_uri = input(f"Redirect URI (press Enter for default): ").strip()
            
            if not redirect_uri:
                redirect_uri = "http://127.0.0.1:5000/api/eve_online/auth_callback"
            
            # Prepare config
            config = current_config.copy()
            config.update({
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri
            })
            
            # Save and test
            print("\n💾 Saving configuration...")
            self.manager.save_config(config)
            
            print("✅ Configuration saved!")
            print("\n🔄 Testing configuration...")
            
            # Test the configuration
            try:
                if self.manager.auth:
                    print("✅ API components initialized successfully")
                    auth_url, state = self.manager.auth.get_authorization_url()
                    print("✅ Authorization URL generation works")
                    print("\nConfiguration test passed! You can now authenticate characters.")
                else:
                    print("❌ Failed to initialize API components")
            except Exception as e:
                print(f"❌ Configuration test failed: {e}")
                print("Please check your credentials and try again.")
        
        elif choice == '3':
            print("\nScope Configuration:")
            current_config = self.manager._load_config()
            current_scopes = current_config.get('scopes', [])
            
            print(f"Current scopes ({len(current_scopes)}):")
            for scope in current_scopes:
                print(f"  - {scope}")
            
            print("\nScope management feature coming soon.")
            print("Current scopes provide access to most common operations.")
            
        elif choice == '4':
            print("\n🧪 Testing Configuration...")
            config = self.manager._load_config()
            
            # Check if credentials are set
            if not config.get('client_id'):
                print("❌ Client ID not configured")
                return
            if not config.get('client_secret'):
                print("❌ Client Secret not configured") 
                return
                
            print("✅ Credentials configured")
            
            # Test API initialization
            try:
                if self.manager.auth:
                    print("✅ EVE API components initialized")
                    
                    # Test authorization URL generation
                    auth_url, state = self.manager.auth.get_authorization_url()
                    print("✅ Authorization URL generation works")
                    print(f"    URL length: {len(auth_url)} characters")
                    
                    # Test public endpoint
                    try:
                        result = self.manager.execute_endpoint('Universe Data', 'Systems')
                        if isinstance(result, list) and len(result) > 0:
                            print(f"✅ Public API access works (found {len(result)} systems)")
                        else:
                            print("⚠️ Public API returned unexpected result")
                    except Exception as e:
                        print(f"⚠️ Public API test failed: {e}")
                    
                    print("\n🎉 Configuration test passed!")
                    print("You can now authenticate characters and use the API.")
                    
                else:
                    print("❌ API components not initialized")
                    
            except Exception as e:
                print(f"❌ Configuration test failed: {e}")
        else:
            print("Invalid choice.")
    
    def _print_result(self, result):
        """Pretty print API results"""
        if isinstance(result, dict) and 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print("\nResult:")
            if isinstance(result, (dict, list)):
                import json
                print(json.dumps(result, indent=2, default=str))
            else:
                print(result)
    
    def _run_web(self):
        """Return web interface data"""
        return {
            'template': 'eve_online.html',
            'data': {
                'categories': self.manager.get_categories(),
                'authenticated_characters': self.manager.get_authenticated_characters(),
                'api_available': EVE_API_AVAILABLE
            }
        }
    
    def _run_gui(self):
        """Run the GUI interface"""
        try:
            from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                         QHBoxLayout, QTabWidget, QListWidget, QPushButton,
                                         QTextEdit, QLabel, QComboBox, QMessageBox, QInputDialog)
            from PyQt5.QtCore import Qt, QThread, pyqtSignal
            import json
            
            class EveOnlineGUI(QMainWindow):
                def __init__(self, manager):
                    super().__init__()
                    self.manager = manager
                    self.setWindowTitle("EVE Online API Tool")
                    self.setGeometry(100, 100, 1000, 700)
                    
                    self.init_ui()
                
                def init_ui(self):
                    central_widget = QWidget()
                    self.setCentralWidget(central_widget)
                    
                    layout = QVBoxLayout(central_widget)
                    
                    # Create tab widget
                    tabs = QTabWidget()
                    layout.addWidget(tabs)
                    
                    # Authentication tab
                    auth_tab = self.create_auth_tab()
                    tabs.addTab(auth_tab, "Authentication")
                    
                    # Categories tabs
                    categories = self.manager.get_categories()
                    for category, operations in categories.items():
                        tab = self.create_category_tab(category, operations)
                        tabs.addTab(tab, category)
                
                def create_auth_tab(self):
                    widget = QWidget()
                    layout = QVBoxLayout(widget)
                    
                    # Character selection
                    layout.addWidget(QLabel("Authenticated Characters:"))
                    self.char_combo = QComboBox()
                    layout.addWidget(self.char_combo)
                    
                    # Buttons
                    buttons_layout = QHBoxLayout()
                    
                    auth_btn = QPushButton("Authenticate New Character")
                    auth_btn.clicked.connect(self.authenticate_character)
                    buttons_layout.addWidget(auth_btn)
                    
                    refresh_btn = QPushButton("Refresh Characters")
                    refresh_btn.clicked.connect(self.refresh_characters)
                    buttons_layout.addWidget(refresh_btn)
                    
                    layout.addLayout(buttons_layout)
                    
                    # Results area
                    self.auth_results = QTextEdit()
                    self.auth_results.setReadOnly(True)
                    layout.addWidget(self.auth_results)
                    
                    # Initial load
                    self.refresh_characters()
                    
                    return widget
                
                def create_category_tab(self, category, operations):
                    widget = QWidget()
                    layout = QHBoxLayout(widget)
                    
                    # Operations list
                    ops_list = QListWidget()
                    ops_list.addItems(operations)
                    layout.addWidget(ops_list)
                    
                    # Right side
                    right_layout = QVBoxLayout()
                    
                    execute_btn = QPushButton("Execute Operation")
                    execute_btn.clicked.connect(lambda: self.execute_operation(category, ops_list.currentItem()))
                    right_layout.addWidget(execute_btn)
                    
                    results_area = QTextEdit()
                    results_area.setReadOnly(True)
                    right_layout.addWidget(results_area)
                    
                    layout.addLayout(right_layout)
                    
                    # Store reference to results area
                    setattr(self, f'results_{category.lower().replace(" ", "_").replace("&", "and")}', results_area)
                    
                    return widget
                
                def authenticate_character(self):
                    result = self.manager.authenticate()
                    if 'error' in result:
                        QMessageBox.critical(self, "Authentication Error", result['error'])
                    else:
                        QMessageBox.information(self, "Success", 
                                              f"Successfully authenticated {result['character_name']}")
                        self.refresh_characters()
                
                def refresh_characters(self):
                    self.char_combo.clear()
                    characters = self.manager.get_authenticated_characters()
                    for char in characters:
                        self.char_combo.addItem(f"{char['character_name']} ({char['character_id']})", 
                                              char['character_id'])
                    
                    # Update auth results
                    if characters:
                        result_text = "Authenticated Characters:\n"
                        for char in characters:
                            result_text += f"- {char['character_name']} (ID: {char['character_id']})\n"
                            result_text += f"  Expires: {char['expires_at']}\n"
                            result_text += f"  Scopes: {len(char['scopes'])} permissions\n\n"
                        self.auth_results.setText(result_text)
                    else:
                        self.auth_results.setText("No authenticated characters found.")
                
                def execute_operation(self, category, item):
                    if not item:
                        QMessageBox.warning(self, "Warning", "Please select an operation")
                        return
                    
                    operation = item.text()
                    character_id = self.char_combo.currentData()
                    
                    # Execute the operation
                    try:
                        result = self.manager.execute_endpoint(category, operation, character_id)
                        
                        # Display results
                        results_attr = f'results_{category.lower().replace(" ", "_").replace("&", "and")}'
                        results_area = getattr(self, results_attr, None)
                        
                        if results_area:
                            if isinstance(result, dict) and 'error' in result:
                                results_area.setText(f"Error: {result['error']}")
                            else:
                                results_area.setText(json.dumps(result, indent=2, default=str))
                    
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Operation failed: {str(e)}")
            
            app = QApplication.instance() or QApplication([])
            window = EveOnlineGUI(self.manager)
            window.show()
            
            if not QApplication.instance():
                app.exec_()
                
        except ImportError:
            print("PyQt5 not available. GUI mode requires PyQt5.")
            print("Install with: pip install PyQt5")
            return None
