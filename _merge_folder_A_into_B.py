import os
import shutil

def relative_path(root_folder, full_path):
    return os.path.relpath(full_path, root_folder)

def get_all_files(folder):
    file_paths = {}
    for dirpath, _, filenames in os.walk(folder):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            rel_path = relative_path(folder, full_path)
            file_paths[rel_path] = full_path
    return file_paths

def merge_folders(folder_a, folder_b):
    files_in_a = get_all_files(folder_a)
    files_in_b = get_all_files(folder_b)

    for rel_path, full_path_b in files_in_b.items():
        full_path_a = os.path.join(folder_a, rel_path)
        
        if rel_path not in files_in_a:
            os.makedirs(os.path.dirname(full_path_a), exist_ok=True)
            # shutil. copy2(full_path_b, full_path_a)
            print(f"Copied: {full_path_b} to {full_path_a}")
        else:
            print(f"Skipped (already exists): {full_path_a}")

def main(folder_a, folder_b):
    if not os.path.exists(folder_a):
        print(f"Error: Folder A '{folder_a}' does not exist.")
        return
    
    if not os.path.exists(folder_b):
        print(f"Error: Folder B '{folder_b}' does not exist.")
        return

    merge_folders(folder_a, folder_b)
    print("Merge complete.")

if __name__ == "__main__":
    folder_a = "/Volumes/4TBSandisk/T2 T3 Accounts #WORKING#"  # Replace with your actual folder A path
    folder_b = "/Volumes/4TBSandisk/Clients/T2 T3 Accounts #WORKING#"  # Replace with your actual folder B path

    main(folder_a, folder_b)