from pathlib import Path

from declutter.functions import create, organize, remove


def main() -> None:
    src_path = Path.cwd()
    dest_path = src_path / "Declutter"

    print("Welcome to DeClutter")
    print("Source:      ", src_path)
    print("Destination: ", dest_path)

    if not dest_path.exists():
        print("Running...")
        if not create(dest_path):
            print("Failed to create declutter directories. Check logs.")
            return
        if organize(src_path, dest_path):
            print("Successful!")
        else:
            print("Organize failed. See logs for details.")
    else:
        print("Removing files...")
        if remove(src_path, dest_path):
            print("Files removed successfully")
        else:
            print("Failed to remove files. See logs.")


if __name__ == "__main__":
    main()
