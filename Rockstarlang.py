import sys
import os
import Core

BASE_DIR = "/storage/emulated/0/Coding/rockstarlang"


def main():
    # Terminal se file di ho toh woh chalaao, warna Play button dabane par Test.rsl chalaao
    filename = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE_DIR, "Test.rsl")

    if not os.path.exists(filename):
        print(f"WASTED! FileNotFoundError: Mission file '{filename}' not found.")
        return

    with open(filename, "r", encoding="utf-8") as file:
        source_code = file.read()

    _, error = Core.run(source_code)
    if error:
        print(error)


if __name__ == "__main__":
    main()
