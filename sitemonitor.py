import json
import threading
import time
import requests
from bs4 import BeautifulSoup

CONFIG_FILE = "config.json"

# Load configuration from a JSON file
def load_config():
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    return config

# Save configuration to a JSON file
def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# Monitor websites for changes
def monitor_websites():
    config = load_config()
    for website in config['websites']:
        try:
            response = requests.get(website['url'])
            soup = BeautifulSoup(response.text, 'html.parser')
            body_text = str(soup.body)

            if 'last_content' in website and website['last_content'] and website['last_content'] != body_text:
                print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {website['url']} - {website['message']} (Change detected)")

            website['last_content'] = body_text

        except Exception as e:
            print(f"Error while monitoring {website['url']}: {e}")

    save_config(config)

# Display the status of monitored websites
def display_status():
    config = load_config()
    print("\nCurrent Status -", time.strftime('%Y-%m-%d %H:%M:%S'))
    print("---------------------------------------------------")
    for website in config['websites']:
        print(f"{website['url']} - {website['message']}")
    print("---------------------------------------------------\n")

# Add a website to monitor
def add_website(url, message):
    config = load_config()
    config['websites'].append({"url": url, "message": message, "last_content": ""})
    save_config(config)

# Remove a website from monitoring
def remove_website(url):
    config = load_config()
    config['websites'] = [website for website in config['websites'] if website['url'] != url]
    save_config(config)

# Monitor websites in a separate thread
def monitor_websites_thread():
    while True:
        monitor_websites()
        display_status()
        time.sleep(60)

# User interface for managing monitored websites
def user_interface():
    print("Available commands: add, remove, status, quit")

    # Start monitoring websites in a separate thread
    monitor_thread = threading.Thread(target=monitor_websites_thread)
    monitor_thread.daemon = True
    monitor_thread.start()

    # Process user commands
    while True:
        command = input("Enter command: ").strip().lower()
        if command == "add":
            url = input("Enter the URL to monitor: ")
            message = input("Enter the custom alert message: ")
            add_website(url, message)
        elif command == "remove":
            url = input("Enter the URL to stop monitoring: ")
            remove_website(url)
        elif command == "status":
            display_status()
        elif command == "quit":
            break
        else:
            print("Invalid command. Available commands: add, remove, status, quit")

if __name__ == "__main__":
    user_interface()
