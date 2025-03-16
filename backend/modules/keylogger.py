keystroke_data = []

def log_keystroke(user_id, key_text):
    keystroke_data.append(f"{user_id} typed: {key_text}\n")
    return True
