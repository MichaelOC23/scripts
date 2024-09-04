import os
import sys
import hashlib
import filecmp

def get_folder_hash(folder_path):
    """Generate a hash for the contents of a folder."""
    hash_md5 = hashlib.md5()
    for root, _, files in os.walk(folder_path):
        for file in sorted(files):  # Sort to ensure consistent order
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'rb') as f:
                    while chunk := f.read(8192):
                        hash_md5.update(chunk)
            except (OSError, IOError):
                # Skip files that can't be read
                continue
    return hash_md5.hexdigest()

def find_duplicate_folders(root_dir):
    """Find and list duplicate folders based on their contents."""
    folder_hashes = {}
    duplicates = []

    for dirpath, dirnames, _ in os.walk(root_dir):
        for dirname in dirnames:
            folder_path = os.path.join(dirpath, dirname)
            folder_hash = get_folder_hash(folder_path)
            print(f"Evaluating: {folder_path}")
            if folder_hash in folder_hashes:
                duplicates.append((folder_hashes[folder_hash], folder_path))
            else:
                folder_hashes[folder_hash] = folder_path

    return duplicates


if len(sys.argv) == 2:
    folder_path = sys.argv[1]
else:
    #working directory the script is run from
    folder_path = os.getcwd()

if not os.path.isdir(folder_path):
    print("Usage: python _find_duplicate_files.py <folder_path>")
    sys.exit(1)

print(f"Finding duplicates in folder: {folder_path}")

root_dir = folder_path
duplicate_folders = find_duplicate_folders(root_dir)

if duplicate_folders:
    with open(f"{folder_path}/duplicate_folders.txt", "w") as f:
        f.write("Duplicate folders found:\n")
        for original, duplicate in duplicate_folders:
            f.write(f"Original: {original}\nDuplicate: {duplicate}\n\n")
    print(f"{len(duplicate_folders)} duplicate folders found")
else:
    print("No duplicate folders found.")
