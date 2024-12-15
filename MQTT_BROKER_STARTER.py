import subprocess
import sys
import platform


def install_mosquitto():
    """Install Mosquitto on Linux or Windows."""
    if platform.system() == "Linux":
        # For Linux-based systems
        try:
            print("Checking if Mosquitto is installed...")
            subprocess.check_call(['which', 'mosquitto'])
        except subprocess.CalledProcessError:
            print("Mosquitto is not installed. Installing...")
            subprocess.check_call(['sudo', 'apt-get', 'update'])
            subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'mosquitto'])
        finally:
            print("Starting Mosquitto service...")
            subprocess.check_call(['sudo', 'systemctl', 'start', 'mosquitto'])
            subprocess.check_call(['sudo', 'systemctl', 'enable', 'mosquitto'])

    elif platform.system() == "Windows":
        # For Windows systems
        print("Windows is detected. Please ensure Mosquitto is installed and run manually.")
        print("Start Mosquitto manually from the command prompt (CMD):")
        print("mosquitto")
    else:
        print("Unsupported OS")


def start_mqtt_server():
    """Start the Mosquitto MQTT server."""
    if platform.system() == "Linux":
        print("Starting Mosquitto service...")
        subprocess.run(["sudo", "systemctl", "start", "mosquitto"])
    else:
        print("Mosquitto server should be started manually on Windows.")


if __name__ == "__main__":
    install_mosquitto()
    start_mqtt_server()
