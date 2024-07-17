import subprocess
import sys
import json
import os
import time

CONFIG_FILE = "settings.json"

def load_settings():
    """Load settings from a JSON file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_settings(settings):
    """Save settings to a JSON file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(settings, f)

    print("Saved settings to setting.json")

def list_drives():
    """List all drives with their sizes in GB."""
    drives = {}
    output = subprocess.check_output("wmic logicaldisk get name,size", shell=True).decode().strip().split('\n')[1:]
    
    for line in output:
        parts = line.split()
        if len(parts) == 2:
            drive = parts[0].strip()
            size = int(parts[1].strip())
            drives[drive] = size / (1024 * 1024 * 1024)  # Convert to GB
    
    return drives

def clear_console():
    os.system('cls')

def format_drive(drive, filesystem, label):
    """Format the specified drive with the given filesystem and label."""
    print(f"Formatting {drive} as {filesystem} with label '{label}'...")
    
    cmd = f"format {drive} /FS:{filesystem} /Q /Y /V:{label}"
    
    process = subprocess.run(cmd, shell=True)
    
    if process.returncode == 0:
        print(f"{drive} formatted successfully!\n")
        return True
    else:
        print(f"Failed to format {drive}.")
        return False

def check_drive_size(drive, expected_size):
    """Check if the drive is within 10% of the expected size."""
    size = list_drives().get(drive, 0)
    if size < expected_size * 0.9 or size > expected_size * 1.1:
        print(f"Warning: The size of {drive} ({size:.2f} GB) is not within 10% of the expected size ({expected_size} GB).")
        return False
    return True

def format_with_saved_settings(drive):
    clear_console()
    """Format a drive using saved settings."""
    settings = load_settings()
    if not settings:
        print("No settings found. Please provide settings for formatting.")
        return

    filesystem = settings.get("filesystem")
    label = settings.get("label")
    expected_size = settings.get("size")

    if not all([filesystem, label, expected_size]):
        print("Incomplete settings found. Please provide all settings.")
        return

    expected_size = float(expected_size)  # Ensure expected_size is a float

    # Prevent formatting of system drives
    if drive == "C:":
        print("Aborting operation: Cannot format the system drive C:.")
        return

    if not check_drive_size(drive, expected_size):
        print("Drive size check failed. Aborting operation.")
        return
    confirmation = input(f"Filesystem: {filesystem}\n"
                         f"Label: {label}\n"
                         f"Expected Size: {expected_size} GB\n\n"
                         f"Press Enter to format {drive}\n"
                         f"Press (q) to Quit\n")
    if confirmation == "":
        formatOK = format_drive(drive, filesystem, label)
        if formatOK != True:
            return
        format_with_saved_settings(drive)


def format_single_sd_card():
    clear_console()
    """Format a single SD card with user-provided settings."""
    print("Formatting a single SD card with user settings.")
    
    drives = list_drives()
    print("Available drives:")
    for drive, size in drives.items():
        print(f"{drive}: {size:.2f} GB")

    drive = input("Enter the drive to format (e.g., E:): ").strip()
    filesystem = input("Choose filesystem type (FAT32/exFAT/NTFS): ").strip()
    label = input("Enter a name for the card (label): ").strip()
    expected_size = float(input("Enter expected size of the card in GB (e.g., 64, 128): ").strip())

    if not check_drive_size(drive, expected_size):
        print("Drive size check failed. Aborting operation.")
        return
    clear_console()
    confirmation = input(f"Filesystem: {filesystem}\n"
                         f"Label: {label}\n"
                         f"Expected Size: {expected_size} GB\n\n"
                         f"Press Enter to format {drive}\n")
    if confirmation == "":
        format_drive(drive, filesystem, label)
            # Save the settings
        settings = {
            "drive": drive,
            "filesystem": filesystem,
            "label": label,
            "size": expected_size
        }
        save_settings(settings)
    time.sleep(2)
    clear_console()


def main():
    """Main menu for the script."""
    settings = load_settings()
    drive = settings.get("drive")
    clear_console()
    while True:
        print("\n[SD Card Formatter]")
        choice = input("    (1) Format one SD card\n    (2) Enter loop to format as settings.json\n    (q) Quit program\n").strip()

        if choice == "1":
            format_single_sd_card()
        elif choice == "2":
            if drive:
                print(f"\nPreparing to format the saved drive: {drive} using saved settings...")
                format_with_saved_settings(drive)
            else:
                print("No drive saved in settings. Please format a drive first.")
        elif choice.lower() == "q":
            print("Exiting the script.")
            clear_console()
            break
        else:
            print("Invalid choice. Please enter 1, 2, or q.")

if __name__ == "__main__":
    if not sys.platform.startswith('win'):
        print("This script is for Windows only.")
    else:
        main()
