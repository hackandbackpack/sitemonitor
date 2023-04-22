import hashlib
import threading
import time
from bs4 import BeautifulSoup
import requests
from twilio.rest import Client
from datetime import datetime
import pytz

def read_config():
    config = {}
    with open("config.txt", "r") as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key] = value
    return config

def read_websites(config):
    websites = {}
    for line in config["websites"].split(';'):
        url, notification = line.strip().split(',')
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            print(f"Error while accessing {url}: {e}")
            continue
        soup = BeautifulSoup(response.content, "html.parser")
        _hash = hashlib.md5(soup.prettify().encode()).hexdigest()
        websites[url] = {
            'hash': _hash,
            'notification': notification
        }
    return websites

def send_sms(config, message):
    account_sid = config["twilio_account_sid"]
    auth_token = config["twilio_auth_token"]
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=config["twilio_phone_number"],
        to=config["destination_phone_number"]
    )

def status_update(websites, stop_event):
    while not stop_event.is_set():
        eastern = pytz.timezone('US/Eastern')
        current_time = datetime.now(eastern).strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{current_time} - Current status of monitored websites:")
        for url, data in websites.items():
            print(f"{url}: {data['hash']}, Custom alert: {data['notification']}")
        time.sleep(60)

def monitor(websites, config, stop_event):
    while not stop_event.is_set():
        for url, data in websites.items():
            try:
                response = requests.get(url)
            except requests.exceptions.RequestException as e:
                print(f"Error while accessing {url}: {e}")
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            current_hash = hashlib.md5(soup.prettify().encode()).hexdigest()

            if current_hash != data['hash']:
                eastern = pytz.timezone('US/Eastern')
                current_time = datetime.now(eastern).strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n{current_time} - Change detected on {url}, sending SMS alert.")
                send_sms(config, data['notification'])
                data['hash'] = current_hash

        time.sleep(180)

def main():
    config = read_config()
    websites = read_websites(config)

    stop_event = threading.Event()
    monitor_thread = threading.Thread(target=monitor, args=(websites, config, stop_event))
    status_thread = threading.Thread(target=status_update, args=(websites, stop_event))

    monitor_thread.start()
    status_thread.start()

    while True:
        try:
            command = input("\nEnter a command (status/start/stop/add/remove/quit): ").strip().lower()

            if command == 'status':
                eastern = pytz.timezone('US/Eastern')
                current_time = datetime.now(eastern).strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n{current_time} - Current status of monitored websites:")
                for url, data in websites.items():
                    print(f"{url}: {data['hash']}, Custom alert: {data['notification']}")

            elif command == 'start':
                if monitor_thread.is_alive():
                    print("Monitoring is already running.")
                else:
                    stop_event.clear()
                    monitor_thread = threading.Thread(target=monitor, args=(websites, config, stop_event))
                    monitor_thread.start()

            elif command == 'stop':
                if not monitor_thread.is_alive():
                    print("Monitoring is not running.")
                else:
                    stop_event.set()
                    monitor_thread.join()

            elif command == 'add':
                url = input("Enter the URL to monitor: ").strip()
                notification = input("Enter the custom notification: ").strip()
                websites[url] = {'hash': '', 'notification': notification}
                print(f"{url} added with custom alert: {notification}")

            elif command == 'remove':
                url = input("Enter the URL to remove: ").strip()
                if url in websites:
                    del websites[url]
                    print(f"{url} removed.")
                else:
                    print(f"{url} not found in the list of monitored websites.")

            elif command == 'quit':
                stop_event.set()
                monitor_thread.join()
                status_thread.join()
                break

            else:
                print("Invalid command. Please try again.")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
