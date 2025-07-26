from flask import Flask, render_template
from modular_portfolio.modular_core.loader import PluginLoader
from modular_portfolio.flask_app.routes import plugin_routes

app = Flask(__name__)
loader = PluginLoader()
app.register_blueprint(plugin_routes)

@app.route('/')
def index():
    plugins = loader.get_plugins('web')
    return render_template('dashboard.html', plugins=plugins)

def launch_web():
    app.run(debug=True)

if __name__ == "__main__":
    launch_web()
