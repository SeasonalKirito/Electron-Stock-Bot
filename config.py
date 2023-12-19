import json
from colorama import init, Fore, Style
init()

class config():
    def read():
        CONFIG_FILE = "config.json"
        try:
            with open(CONFIG_FILE, "r") as file:
                config_data = json.load(file)
                return config_data
        except FileNotFoundError:
            print(f"{Fore.RED}[-] {CONFIG_FILE} not found.")
            return None
        except json.JSONDecodeError:
            print(f"{Fore.RED}[-] Unable to decode {CONFIG_FILE}. Check if it's a valid JSON file.")
            return None