import os
import sys

skip_files = [".DS_Store", "appveyor.yml"]

def find_duplicate_files(start_folder):
    files_dict = {}
    duplicates = []

    for dirpath, _, filenames in os.walk(start_folder):
        if ".git" in dirpath:
            continue
        if ".vscode" in dirpath:
            continue
        if "_OtherFiles" in dirpath:
            continue
        
        for filename in filenames:
            if filename in skip_files:
                continue
            file_path = os.path.join(dirpath, filename)
            if filename in files_dict:
                files_dict[filename].append(file_path)
            else:
                files_dict[filename] = [file_path]

    for filename, paths in files_dict.items():
        if len(paths) > 1:
            duplicates.append((filename, paths))

    return duplicates

def write_duplicates_to_file(duplicates, output_file):
    with open(output_file, 'w') as file:
        for filename, paths in duplicates:
            file.write(f"Duplicate File: {filename}\n")
            for path in paths:
                file.write(f"  Path: {path}\n")
            file.write("\n")

def main():
    
    if len(sys.argv) == 2:
        folder_path = sys.argv[1]
    else:
        #working directory the script is run from
        folder_path = os.getcwd()

    if not os.path.isdir(folder_path):
        print("Usage: python >find_duplicate_files2.py <folder_path>")
        sys.exit(1)

    print(f"Finding duplicates in folder: {folder_path}")

    external_drive_path = folder_path
    output_file = os.path.join(external_drive_path, "duplicate_files.txt")

    duplicates = find_duplicate_files(external_drive_path)
    write_duplicates_to_file(duplicates, output_file)
    print(f"Duplicate files list written to: {output_file}")

if __name__ == "__main__":
    main()