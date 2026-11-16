import sys
import Core  # Aapki Lexer/Parser wali file

def main():
    # Check karo ki user ne command mein file ka naam diya hai ya nahi
    if len(sys.argv) < 2:
        print("Usage: python rockstarlang.py <filename.rsl>")
        return

    filename = sys.argv[1]

    # Extension check (.rsl hona zaroori hai)
    if not filename.endswith('.rsl'):
        print("WASTED! File must have a .rsl extension.")
        return

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"WASTED! File '{filename}' not found.")
        return

    # Apne Lexer/Parser ko file ka poora text bhejo
    result, error = Core.run(source_code)

    if error:
        print(error)
    else:
        print(result)

if __name__ == '__main__':
    main()
