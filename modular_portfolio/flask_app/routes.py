

from flask import Blueprint, request, redirect, url_for, render_template_string
from modular_portfolio.modular_core.loader import PluginLoader

plugin_routes = Blueprint('plugin_routes', __name__)
loader = PluginLoader()


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
