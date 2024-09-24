import subprocess
import os
import platform
import json
import sys

# Function to check and lock Pipfile if it has been modified
def check_and_lock_pipfile():
    try:
        result = subprocess.run(['git', 'diff', '--name-only', 'HEAD'], capture_output=True, text=True)
        if 'Pipfile' in result.stdout:
            print("Pipfile has changed. Running pipenv lock...")
            subprocess.run(['pipenv', 'lock'], check=True)
        else:
            print("Pipfile has not changed. Skipping pipenv lock.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during pipenv lock: {e}")
        sys.exit(1)

# Function to install dependencies with development packages
def install_dependencies():
    try:
        subprocess.run(['pipenv', 'install', '--dev'], check=True)
        print("Dependencies installed.")
        subprocess.run(['pipenv', 'shell'], check=True)  # Activate the virtual environment
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during pipenv install: {e}")
        sys.exit(1)

# Function to create VS Code settings for real-time linting and formatting
def create_vscode_settings():
    try:
        settings = {
            "python.pythonPath": "${workspaceFolder}/.venv/bin/python",
            "python.linting.enabled": True,
            "python.linting.flake8Enabled": True,
            "python.formatting.blackPath": "${workspaceFolder}/.venv/bin/black",
            "python.formatting.provider": "black",
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": "explicit",
                "source.fixAll": "explicit"
            }
        }

        # Check for platform-specific paths
        if platform.system() == "Windows":
            settings["python.pythonPath"] = "${workspaceFolder}\\.venv\\Scripts\\python.exe"

        # Create .vscode directory if it doesn't exist
        vscode_dir = ".vscode"
        if not os.path.exists(vscode_dir):
            os.makedirs(vscode_dir)

        # Write the settings to the settings.json file
        with open(os.path.join(vscode_dir, "settings.json"), "w") as f:
            json.dump(settings, f, indent=4)

    except Exception as e:
        print(f"Error occurred during VS Code settings creation: {e}")
        sys.exit(1)

# Main function to run the setup
def main():
    # check_and_lock_pipfile()
    install_dependencies()
    create_vscode_settings()
    print("Setup complete. Please reload VS Code to apply the new settings for linting and formatting.")

if __name__ == "__main__":
    main()
