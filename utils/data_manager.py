import json
import os
import threading
import time

_data = None  # In-memory cache for data.json
_data_lock = threading.Lock() # Lock for thread-safe data access
_last_saved = 0 #Timestamp of last save

DATA_SAVE_INTERVAL = 60  # Save interval in seconds

def load_data():
    global _data
    global _last_saved
    with _data_lock:
        if _data is None:
            try:
                if os.path.exists('data.json'):
                    with open('data.json', 'r') as f:
                        _data = json.load(f)
                        logging.info("Data loaded from data.json")
                else:
                    _data = {"admins": [], "users": {}, "banned_users": []}
                    logging.info("data.json not found. Starting with blank slate.")
                _last_saved = time.time()
            except Exception as e:
                logging.exception("Error loading data!")
                return {"admins": [], "users": {}, "banned_users": []}
        return _data

def save_data(data):
    global _last_saved
    with _data_lock:
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4)
        _last_saved = time.time()

def is_admin(user_id):
    data = load_data()
    #print(f"Checking admin status for user_id: {user_id}")
    #print(f"Admins in data: {data['admins']}")
    return str(user_id) in [str(admin_id) for admin_id in data['admins']]

def is_banned(user_id):
    data = load_data()
    return str(user_id) in data.get('banned_users', [])

import logging

def start_data_saver():
    def save_data_periodically():
        while True:
            time.sleep(DATA_SAVE_INTERVAL)
            if time.time() - _last_saved >= DATA_SAVE_INTERVAL:
                try:
                    data = load_data()
                    save_data(data)
                    logging.info("Saving data...")
                except Exception as e:
                    logging.exception(f"Error saving data: {e}")

    logging.info("Starting data saver thread...")
    thread = threading.Thread(target=save_data_periodically)
    thread.daemon = True  # Allow the main program to exit even if this thread is running
    thread.start()
