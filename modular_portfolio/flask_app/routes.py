import sys
import os
# Add calc_module to the path for core imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'calc_module')))

from flask import Blueprint, request, redirect, url_for, render_template_string, jsonify
from modular_portfolio.modular_core.loader import PluginLoader

plugin_routes = Blueprint('plugin_routes', __name__)
loader = PluginLoader()


# --- EVE Online Search Endpoint ---
@plugin_routes.route('/api/eve_online/search', methods=['POST'])
def eve_online_search():
    """Search EVE Online API operations by category and query string"""
    try:
        data = request.get_json()
        category = data.get('category', '').strip()
        query = data.get('query', '').strip().lower()
        # Get the EVE Online plugin
        plugins = loader.get_plugins('web')
        eve_plugin = None
        for plugin in plugins:
            if plugin['name'].lower() == 'eveonline':
                eve_plugin = plugin['class']()
                break
        if not eve_plugin:
            return jsonify({'error': 'EVE Online plugin not found'}), 404
        # Get all categories/operations
        categories = eve_plugin.manager.get_categories() if hasattr(eve_plugin.manager, 'get_categories') else {}
        results = []
        if category and category in categories:
            ops = categories[category]
        else:
            # Flatten all operations
            ops = [op for ops in categories.values() for op in ops]
        for op in ops:
            name = op.get('function_name', op) if isinstance(op, dict) else op
            doc = op.get('docstring', '') if isinstance(op, dict) else ''
            if query in name.lower() or query in doc.lower():
                results.append(op)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@plugin_routes.route('/tool/<plugin_name>')
def tool_page(plugin_name):
    plugins = loader.get_plugins('web')
    # InfoTool always first, pass plugins to template for sidebar
    plugins = sorted(plugins, key=lambda p: 0 if p['name'].lower() == 'infotool' else 1)
    for plugin in plugins:
        if plugin['name'] == plugin_name:
            from flask import render_template
            if plugin_name.lower() == 'infotool':
                import os
                import markdown
                # Always use the main README.md in the project root
                root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
                readme_path = os.path.join(root_dir, 'README.md')
                readme_html = None
                if os.path.exists(readme_path):
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        readme_html = markdown.markdown(f.read(), extensions=['fenced_code', 'tables'])
                return render_template('info_tool.html', plugin=plugin, plugins=plugins, readme_html=readme_html)
            # Special case for Gamenight: render games template
            if plugin_name.lower() == 'gamenight':
                return render_template('gamenight.html', plugin=plugin, plugins=plugins)
            # Special case for AdvancedLifeCounter: render life counter template
            if plugin_name.lower() == 'advlifecounter':
                return render_template('advanced_life_counter.html', plugin=plugin, plugins=plugins)
            # Special case for TestTool: render template with plugins list
            if plugin_name.lower() == 'testtool':
                result = None
                action = request.args.get('action')
                if action == 'ping':
                    host = request.args.get('host', '8.8.8.8')
                    result = plugin['class']().ping_test(host, 4, return_output=True)
                elif action == 'speed':
                    result = plugin['class']().speed_test(return_output=True)
                elif action == 'sysinfo':
                    result = plugin['class']().system_info(return_output=True)
                elif action == 'netinfo':
                    result = plugin['class']().network_info(return_output=True)
                return render_template('test_tool.html', plugins=plugins, result=result)
            # Special case for CalcTool: render template with plugins list and calculation
            if plugin_name.lower() == 'calctool':
                from core import calculate, list_operations, Operation
                import re
                # Categorize operations
                ops = list_operations()
                categories = {
                    'Arithmetic': [],
                    'Geometry': [],
                    'Trigonometry': [],
                    'Logarithms': [],
                    'Statistics': [],
                    'Other': []
                }
                for op in ops:
                    fname = op['function_name']
                    if 'area' in fname or 'perimeter' in fname or 'volume' in fname or 'distance' in fname or 'midpoint' in fname or 'slope' in fname or 'angle' in fname:
                        categories['Geometry'].append(op)
                    elif 'sin' in fname or 'cos' in fname or 'tan' in fname or 'deg' in fname or 'radian' in fname or 'cot' in fname or 'sec' in fname or 'csc' in fname:
                        categories['Trigonometry'].append(op)
                    elif 'log' in fname or 'exp' in fname:
                        categories['Logarithms'].append(op)
                    elif 'mean' in fname or 'median' in fname or 'mode' in fname or 'variance' in fname or 'std' in fname or 'quartile' in fname or 'correlation' in fname or 'z_score' in fname or 'percentile' in fname:
                        categories['Statistics'].append(op)
                    elif fname in ['add', 'subtract', 'multiply', 'divide', 'modulo', 'floor_divide', 'power', 'square_root', 'cube_root', 'nth_root', 'square', 'cube', 'absolute_value', 'sign', 'ceiling', 'floor', 'round_to_decimals', 'factorial', 'combination', 'permutation', 'greatest_common_divisor', 'least_common_multiple', 'is_prime', 'fibonacci', 'arithmetic_mean', 'geometric_mean', 'harmonic_mean', 'percentage', 'percentage_change']:
                        categories['Arithmetic'].append(op)
                    else:
                        categories['Other'].append(op)
                # Handle form submission
                result = None
                error = None
                selected_op = request.args.get('operation')
                arg_values = {}
                if selected_op:
                    opinfo = next((o for cat in categories.values() for o in cat if o['function_name'] == selected_op), None)
                    if opinfo:
                        for arg in opinfo['required_args']:
                            arg_values[arg] = request.args.get(arg, '')
                        # Operations that require integer arguments
                        int_ops = {
                            'fibonacci', 'factorial', 'combination', 'permutation', 'greatest_common_divisor',
                            'least_common_multiple', 'is_prime', 'floor_divide', 'modulo',
                            'quartile_1', 'quartile_3', 'percentile',
                        }
                        list_ops = {'range_values', 'mean', 'median', 'mode', 'variance_population', 'variance_sample', 'standard_deviation_population', 'standard_deviation_sample', 'percentile'}
                        try:
                            call_args = {}
                            for k, v in arg_values.items():
                                if selected_op in list_ops:
                                    # Accept comma or space separated list, convert to list of floats
                                    if v:
                                        items = [s for s in re.split(r'[ ,]+', v) if s]
                                        call_args[k] = [float(x) for x in items]
                                    else:
                                        call_args[k] = []
                                elif selected_op in int_ops:
                                    call_args[k] = int(float(v)) if v else v
                                else:
                                    call_args[k] = float(v) if v and v.replace('.','',1).replace('-','',1).isdigit() else v
                            result = calculate(operation=opinfo['operation'], **call_args)
                        except Exception as e:
                            error = f"Calculation error: {e}"
                return render_template('calc_tool.html', plugins=plugins, categories=categories, selected_op=selected_op, arg_values=arg_values, result=result, error=error)
            
            # Special case for EveOnline: render EVE Online API tool template
            if plugin_name.lower() == 'eveonline':
                web_data = plugin['class']().run('web')
                if isinstance(web_data, dict) and 'template' in web_data and 'data' in web_data:
                    return render_template(web_data['template'], plugins=plugins, **web_data['data'])
                else:
                    # Fallback if plugin doesn't return expected format
                    return render_template('eve_online.html', plugins=plugins, 
                                         categories={}, authenticated_characters=[], api_available=False)
            
            html = plugin['class']().run('web')
            if isinstance(html, str):
                from flask import render_template_string
                return render_template_string(html)
            # If plugin returns None or not a string, show a default info page
            return render_template('base.html', plugins=plugins, content=f"<div class='container'><div class='alert alert-info mt-4'>No web page implemented for this tool.</div></div>")
    return redirect(url_for('index'))

@plugin_routes.route('/run/<plugin_name>', methods=['POST'])
def run_plugin(plugin_name):
    # For future: handle POST actions for plugins
    return redirect(url_for('tool_page', plugin_name=plugin_name))

# --- EVE Online OAuth2 Start (GET) ---
@plugin_routes.route('/api/eve_online/auth', methods=['GET'])
def eve_online_auth():
    """Start EVE Online OAuth2 flow using client_id and redirect_uri from query params"""
    from flask import request, redirect
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    if not client_id or not redirect_uri:
        return "Missing client_id or redirect_uri", 400
    # Get the EVE Online plugin
    plugins = loader.get_plugins('web')
    eve_plugin = None
    for plugin in plugins:
        if plugin['name'].lower() == 'eveonline':
            eve_plugin = plugin['class']()
            break
    if not eve_plugin:
        return "EVE Online plugin not found", 404
    # Save config to plugin (in-memory, not persisted)
    if hasattr(eve_plugin.manager, 'save_config'):
        eve_plugin.manager.save_config({
            'client_id': client_id,
            'redirect_uri': redirect_uri
        })
    # Get the SSO authorization URL
    if hasattr(eve_plugin.manager.auth, 'get_authorization_url'):
        try:
            auth_url, state = eve_plugin.manager.auth.get_authorization_url()
            return redirect(auth_url)
        except Exception as e:
            return f"Failed to get authorization URL: {str(e)}", 500
    return "Authorization handler not available", 500
    
# EVE Online API endpoints
@plugin_routes.route('/api/eve_online/authenticate', methods=['POST'])
def eve_online_authenticate():
    """Initiate EVE Online authentication flow"""
    from flask import jsonify
    
    try:
        plugins = loader.get_plugins('web')
        eve_plugin = None
        for plugin in plugins:
            if plugin['name'].lower() == 'eveonline':
                eve_plugin = plugin['class']()
                break
        
        if not eve_plugin:
            return jsonify({'error': 'EVE Online plugin not found'}), 404
        
        # Get authorization URL
        result = eve_plugin.manager.authenticate()
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@plugin_routes.route('/api/eve_online/auth_callback')
def eve_online_auth_callback():
    """Handle EVE Online OAuth2 callback and redirect to frontend with tokens and character info as query params"""
    from flask import request, redirect, url_for
    import traceback, logging
    logger = logging.getLogger("eve_online_auth_callback")
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        logger.info(f"OAuth2 callback received: code={code}, state={state}")
        if not code:
            logger.error("Authorization code not received in callback.")
            return "Authorization code not received", 400
        plugins = loader.get_plugins('web')
        eve_plugin = None
        for plugin in plugins:
            if plugin['name'].lower() == 'eveonline':
                eve_plugin = plugin['class']()
                break
        if not eve_plugin:
            logger.error("EVE Online plugin not found in callback handler.")
            return "EVE Online plugin not found", 404
        callback_url = request.url.replace('localhost', '127.0.0.1')
        logger.info(f"Callback URL: {callback_url}")
        if hasattr(eve_plugin.manager.auth, 'handle_callback'):
            try:
                token = eve_plugin.manager.auth.handle_callback(callback_url, state)
                logger.info(f"Token received: {token}")
                # Extract info for frontend
                char_id = token.get('CharacterID') or token.get('character_id')
                char_name = token.get('CharacterName') or token.get('character_name')
                access_token = token.get('access_token')
                refresh_token = token.get('refresh_token')
                logger.info(f"Redirecting to frontend with character_id={char_id}, character_name={char_name}")
                # Redirect to frontend with info as query params
                frontend_url = url_for('tool_page', plugin_name='EveOnline', _external=True)
                redirect_url = f"{frontend_url}?character_id={char_id}&character_name={char_name}&access_token={access_token}&refresh_token={refresh_token}"
                logger.info(f"Redirect URL: {redirect_url}")
                return redirect(redirect_url)
            except Exception as e:
                logger.error(f"Authentication failed: {str(e)}\n{traceback.format_exc()}")
                return f"Authentication failed: {str(e)}", 400
        else:
            logger.error("Authentication handler not available on eve_plugin.manager.auth.")
            return "Authentication handler not available", 500
    except Exception as e:
        logger.error(f"Exception in auth_callback: {str(e)}\n{traceback.format_exc()}")
        return str(e), 500

@plugin_routes.route('/api/eve_online/characters', methods=['GET'])
def eve_online_characters():
    """Get list of authenticated characters"""
    from flask import jsonify
    
    try:
        plugins = loader.get_plugins('web')
        eve_plugin = None
        for plugin in plugins:
            if plugin['name'].lower() == 'eveonline':
                eve_plugin = plugin['class']()
                break
        
        if not eve_plugin:
            return jsonify({'error': 'EVE Online plugin not found'}), 404
        
        characters = eve_plugin.manager.get_authenticated_characters()
        return jsonify(characters)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@plugin_routes.route('/api/eve_online/auth_url', methods=['GET'])
def eve_online_auth_url():
    """Get EVE Online authentication URL"""
    from flask import jsonify, request
    try:
        client_id = request.args.get('client_id')
        redirect_uri = request.args.get('redirect_uri', 'http://127.0.0.1:5000/api/eve_online/auth_callback')
        # ...existing code...
        plugins = loader.get_plugins('web')
        eve_plugin = None
        for plugin in plugins:
            if plugin['name'].lower() == 'eveonline':
                eve_plugin = plugin['class']()
                break
        
        if not eve_plugin:
            return jsonify({'error': 'EVE Online plugin not found'}), 404
        
        if not eve_plugin.manager.auth:
            return jsonify({'error': 'Authentication not initialized. Please configure API credentials.'}), 400
        
        try:
            auth_url, state = eve_plugin.manager.auth.get_authorization_url()
            return jsonify({
                'auth_url': auth_url,
                'state': state
            })
        except Exception as e:
            return jsonify({'error': f'Failed to get authorization URL: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@plugin_routes.route('/api/eve_online/execute', methods=['POST'])
def eve_online_execute():
    """Execute EVE Online API operations"""
    from flask import jsonify
    
    try:
        data = request.get_json()
        category = data.get('category')
        operation = data.get('operation')
        character_id = data.get('character_id')
        
        # Get the EVE Online plugin
        plugins = loader.get_plugins('web')
        eve_plugin = None
        for plugin in plugins:
            if plugin['name'].lower() == 'eveonline':
                eve_plugin = plugin['class']()
                break
        
        if not eve_plugin:
            return jsonify({'error': 'EVE Online plugin not found'}), 404
        
        # Execute the operation
        result = eve_plugin.manager.execute_endpoint(category, operation, character_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@plugin_routes.route('/api/eve_online/remove_character', methods=['POST'])
def eve_online_remove_character():
    """Remove character authentication"""
    from flask import jsonify
    
    try:
        data = request.get_json()
        character_id = data.get('character_id')
        
        # Get the EVE Online plugin
        plugins = loader.get_plugins('web')
        eve_plugin = None
        for plugin in plugins:
            if plugin['name'].lower() == 'eveonline':
                eve_plugin = plugin['class']()
                break
        
        if not eve_plugin:
            return jsonify({'error': 'EVE Online plugin not found'}), 404
        
        # Remove the character token
        if eve_plugin.manager.token_manager:
            eve_plugin.manager.token_manager.remove_token(character_id)
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Token manager not initialized'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@plugin_routes.route('/api/eve_online/configure', methods=['GET'])
def eve_online_get_config():
    """Get EVE Online API configuration"""
    from flask import jsonify
    
    try:
        # Get the EVE Online plugin
        plugins = loader.get_plugins('web')
        eve_plugin = None
        for plugin in plugins:
            if plugin['name'].lower() == 'eveonline':
                eve_plugin = plugin['class']()
                break
        
        if not eve_plugin:
            return jsonify({'error': 'EVE Online plugin not found'}), 404
        
        # Get current configuration (don't expose client_secret)
        config = eve_plugin.manager._load_config()
        safe_config = {
            'client_id': config.get('client_id', ''),
            'redirect_uri': config.get('redirect_uri', 'http://127.0.0.1:5000/api/eve_online/auth_callback')
        }
        
        return jsonify(safe_config)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@plugin_routes.route('/api/eve_online/configure', methods=['POST'])
def eve_online_configure():
    """Save EVE Online API configuration"""
    from flask import jsonify
    
    try:
        data = request.get_json()
        
        # Get the EVE Online plugin
        plugins = loader.get_plugins('web')
        eve_plugin = None
        for plugin in plugins:
            if plugin['name'].lower() == 'eveonline':
                eve_plugin = plugin['class']()
                break
        
        if not eve_plugin:
            return jsonify({'error': 'EVE Online plugin not found'}), 404
        
        # Save configuration
        config = {
            'client_id': data.get('client_id', ''),
            'client_secret': data.get('client_secret', ''),
            'redirect_uri': data.get('redirect_uri', 'http://127.0.0.1' \
            ':5000/api/eve_online/auth_callback')
        }
        
        eve_plugin.manager.save_config(config)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
