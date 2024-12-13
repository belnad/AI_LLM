import os
import subprocess

def setup_virtual_environment(env_name="env", requirements_file="requirements.txt"):
    """
    Sets up a virtual environment and installs dependencies.

    Args:
        env_name (str): Name of the virtual environment folder.
        requirements_file (str): Path to the requirements.txt file.
    """
    try:
        # Create virtual environment if it does not exist
        if not os.path.exists(env_name):
            print(f"Creating virtual environment '{env_name}'...")
            subprocess.check_call(["python", "-m", "pip", "install", "virtualenv"])
            subprocess.check_call(["python", "-m", "virtualenv", env_name])

        # Activate the virtual environment
        activate_script = os.path.join(env_name, "Scripts", "activate") if os.name == "nt" else os.path.join(env_name, "bin", "activate")

        if os.name == "nt":
            activation_cmd = f"{activate_script} &"
        else:
            activation_cmd = f"source {activate_script} &&"

        # Install dependencies
        if os.path.exists(requirements_file):
            print(f"Installing dependencies from '{requirements_file}'...")
            subprocess.check_call(f"{activation_cmd} pip install -r {requirements_file}", shell=True, executable="/bin/bash" if os.name != "nt" else None)
            print("Dependencies installed successfully!")
        else:
            print(f"Requirements file '{requirements_file}' not found. Skipping dependency installation.")

    except subprocess.CalledProcessError as error:
        print(f"Error during setup: {error}")

if __name__ == "__main__":
    setup_virtual_environment()

    # processing
    #os.system('python3 fetch.py')
    os.system('python3 storing.py')
