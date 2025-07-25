import argparse
import os
import shutil

def create_plugin(name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, 'templates', 'plugin_template')
    target_dir = os.path.join(base_dir, 'addons', name)
    if os.path.exists(target_dir):
        print(f"Plugin '{name}' already exists.")
        return
    shutil.copytree(template_dir, target_dir)
    print(f"Plugin '{name}' created at {target_dir}")

def main():
    parser = argparse.ArgumentParser(description="Create a new plugin from template.")
    parser.add_argument('--name', required=True, help='Plugin name')
    args = parser.parse_args()
    create_plugin(args.name)

if __name__ == "__main__":
    main()
