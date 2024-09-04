import os
import sys

TEST_FOLDER= "/Users/michasmi/Library/CloudStorage/OneDrive-JBIHoldingsLLC/WorkingMAS/ProjectSpring"

def main():
    # Ge the path to the start folder from sys.argv
    start_folder = sys.argv[1] if len(sys.argv) == 2 else TEST_FOLDER
    add_title_to_txt_files(start_folder=start_folder)
    print("Adding titles to text files complete.")

def add_title_to_txt_files(start_folder):
    for root, _, files in os.walk(start_folder):
        folder_name = os.path.basename(root)
        for file_name in files:
            if file_name.endswith('.txt') or file_name.endswith('.md'):
                print(f"Adding title to {file_name} in {folder_name}")
                file_path = os.path.join(root, file_name)
                add_title_to_file(file_path, folder_name, file_name)

def add_title_to_file(file_path, folder_name, file_name):
    title_line = f"Document File Name-Title: {folder_name} {file_name}\n\n" 

    try:
        with open(file_path, 'r') as file:
            content = file.readlines()
        
        content.insert(0, title_line)
        print(f"Inserting title line {title_line}")

        with open(file_path, 'w') as file:
            file.writelines(content)
        
        print(f"Title added to {file_path}")
    except Exception as e:
        print(f"Failed to add title to {file_path}: {e}")

if __name__ == "__main__":
    main()
    