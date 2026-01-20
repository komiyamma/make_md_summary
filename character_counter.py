import sys

def count_characters(text):
    count = 0
    for char in text:
        # Check if the character is ASCII (0-127)
        if ord(char) < 128:
            count += 0.5
        else:
            count += 1
    return count

if __name__ == "__main__":
    if len(sys.argv) > 1:
        memo_content = sys.argv[1]
        length = count_characters(memo_content)
        print(length)
    else:
        print("Usage: python character_counter.py <memo_content>")