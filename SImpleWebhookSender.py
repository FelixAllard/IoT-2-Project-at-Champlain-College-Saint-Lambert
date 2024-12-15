import requests
import time

# Function to check internet connection
def is_connected():
    try:
        # Attempt to reach a reliable site like Google
        requests.get('https://www.google.com', timeout=5)
        return True
    except requests.ConnectionError:
        return False

# Function to get public IP
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        ip_data = response.json()
        return ip_data['ip']
    except Exception as e:
        return f"Error: {e}"

# Discord webhook URL
webhook_url = "https://discord.com/api/webhooks/1299164357275418624/e0xTQ69k6j93ZlhJz_LyWfqgB6WNAN0eqkU6wAVlV8-_Y5_X28LGSrgpm9sYPNvMBnwH"

# Wait for internet connection
print("Checking internet connection...")
while not is_connected():
    print("No internet connection. Retrying in 5 seconds...")
    time.sleep(5)

print("Internet connection found!")

# Get the public IP once the internet connection is established
public_ip = get_public_ip()

# Data to send to the Discord webhook
data = {
    "content": f"My public IP address is: {public_ip}"
}

# Sending the data to the Discord webhook
response = requests.post(webhook_url, json=data)

# Check the response
if response.status_code == 204:
    print("IP address sent successfully!")
else:
    print(f"Failed to send IP. Status code: {response.status_code}")
