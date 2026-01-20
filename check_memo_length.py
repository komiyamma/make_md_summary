import sys
import os

def custom_char_length(text):
    length = 0
    for char in text:
        if ord(char) < 128:  # ASCII characters
            length += 0.5
        else:  # Non-ASCII characters (including full-width Japanese characters)
            length += 1
    return length

def check_memo_length(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return

    calculated_length = custom_char_length(content)

    if 65 <= calculated_length <= 80:
        print(f"PASS: {file_path} - Length: {calculated_length} (within 65-80 characters)")
    else:
        print(f"FAIL: {file_path} - Length: {calculated_length} (NOT within 65-80 characters)")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_memo_length.py <path_to_memo_file>")
    else:
        check_memo_length(sys.argv[1])
