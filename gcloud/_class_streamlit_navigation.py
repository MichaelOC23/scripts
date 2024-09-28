import streamlit as st
import os
import pathlib  


class navigation_streamlit:
    def __init__(self):
        self.folder_name = "pages_nav"
        self.start_folder = f"{os.getcwd()}/gcloud/{self.folder_name}"
        self.folder_structure = self.get_folder_structure(self.start_folder)
        self.menu = None
    
    def get_folder_structure(self, start_folder):
        folder_structure = {}
        num_seed = 1001
        used_numbers = []
        
        #from the start folder, get all name of the last folder with pathlib
        
        
        # Check if the start_folder exists
        if not os.path.isdir(start_folder):
            print(f"The folder {start_folder} does not exist.")
            return folder_structure
        
        start_folder_name = os.path.basename(start_folder)
        
        # Iterate through all items in the start_folder
        for sub_folder in os.listdir(start_folder):
            sub_folder_path = f"{start_folder}/{sub_folder}"
            if not os.path.isdir(sub_folder_path): 
                continue
            
            
            folder_structure[sub_folder] = {}
                
            # Iterate through all files in this subfolder
            for file in os.listdir(sub_folder_path):
                file_path = f"{sub_folder_path}/{file}"
                
                # Check if it's a file (not a directory)
                if not file.endswith(".py"):
                    continue
                #get the file number
                num = num_seed
                if file[:1].isdigit(): num = int(file[:1])
                if file[:2].isdigit(): num = int(file[:2])
                if file[:3].isdigit(): num = int(file[:3])
                
                if num == num_seed:
                    num_seed += 1
                
                
                while num in used_numbers:
                    num += 1
                
                used_numbers.append(num)
                    
                folder_structure[sub_folder][num] = {'name': self.format_menu_name(file).strip(), "num": num, "path": file_path}

            #Sort the subfolder dictionary by the number key
            folder_structure[sub_folder] = dict(sorted(folder_structure[sub_folder].items()))

        return folder_structure

    def format_menu_name(self, name):
        
        #get the left 3 characters of the name, if they are numbers then tun the number string into an integer
        if name[:3].isdigit():
            name = name.replace(name[:3], "")
        if name[:2].isdigit():
            name = name.replace(name[:2], "")
        if name[:1].isdigit():
            name = name.replace(name[:1], "")
        
        name = name.replace(".py", "")
        name = name.replace("_", " ")
        name = name.replace("-", " ")
        
        return name.title()
    
    def create_menu(self):
        def create_page(file_dict):
            path_obj = pathlib.Path(file_dict.get('path', 'NO-PATH'))
            page = st.Page(path_obj, title=file_dict.get('name', 'NO-NAME').strip())
            return page
            
        nav_dict = {}
        for folder in self.folder_structure.keys():
            nav_dict[folder] = []
            sorted_dict = self.folder_structure[folder]
            for key in sorted_dict.keys():
                nav_dict[folder].append(create_page(sorted_dict[key]))
        return nav_dict
       
    def check_if_authenticated(self):
        isAuthenticated = False
        if 'IS_AUTHENTICATED_TO_GOOGLE' not in st.session_state:
            st.session_state['IS_AUTHENTICATED_TO_GOOGLE'] = False
            return isAuthenticated
        
        if st.session_state['IS_AUTHENTICATED_TO_GOOGLE']:
            isAuthenticated = True
        
        if isAuthenticated:
            self.menu = self.create_menu() 

        return isAuthenticated
        
    
        



