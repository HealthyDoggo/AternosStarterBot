import json

def save_pending_responses(pending_responses):
    with open("pending_responses.json", "w") as f:
        json.dump(pending_responses, f)

def save_linked_accounts(linked_accounts):
    with open("linked_accounts.json", "w") as f:
        json.dump(linked_accounts, f)

def save_correct_ip_addresses(correct_ip_addresses):
    with open("correct_ip_addresses.json", "w") as f:
        json.dump(correct_ip_addresses, f)
    
def save_last_checked_log(last_checked_log):
    with open("last_checked_log.txt", "w") as f:
        try:
            f.write(last_checked_log)
        except TypeError:
            f.write('')

def load_pending_responses():
    try:
        with open("pending_responses.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Return empty list if no file exists

def load_linked_accounts():
    try:
        with open("linked_accounts.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}  # Return empty dict if no file exists

def load_correct_ip_addresses():
    try:
        with open("correct_ip_addresses.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}  # Return empty dict if no file exists
def load_last_checked_log():
    try:
        with open("last_checked_log.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return None
