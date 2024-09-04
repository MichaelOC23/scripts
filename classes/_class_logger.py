import os
import uuid
import json
import time
from datetime import datetime

class Logger:
    def __init__(self, output_folder="logs", only_print_errors=False, working_dir=None):
        
        if not working_dir: 
            return
        
        # Set Log Data and Metadata
        self.uid = f"{uuid.uuid4()}"
        self.start_time = datetime.now()
        self.last_log_time = self.start_time
        self.log_entries = []
        self.only_print_errors = only_print_errors
        
        try:
            self.working_dir = working_dir
            if not self.working_dir or not os.path.exists(self.working_dir):
                self.working_dir = os.getcwd()
            if not os.path.isdir(self.working_dir):
                self.working_dir = os.path.dirname(os.path.realpath(__file__))
        except:
            self.working_dir = os.getcwd()  
            
        self.output_folder = os.path.join(self.working_dir, output_folder)
        if not os.path.exists(self.output_folder): os.makedirs(self.output_folder)
        
        # Safe value of datetime for log name
        self.log_time = datetime.now().strftime('%Y.%m.%d-%H.%M.%S')
        
        #Complete log paths
        self.log_file_path = f"{self.output_folder}/log_{self.log_time}_{self.uid}.txt"
        self.large_log_file_path = f"{self.output_folder}/log_LARGE_{self.log_time}_{self.uid}.txt"
        
        print (f"Logger file: {self.log_file_path}")
        
        self.shell_color_dict = {
            "BLACK": "\033[1;30m",
            "RED": "\033[1;31m",
            "GREEN": "\033[1;32m",
            "YELLOW": "\033[1;33m",
            "BLUE": "\033[1;34m",
            "PURPLE": "\033[1;35m",
            "CYAN": "\033[1;36m",
            "WHITE": "\033[1;37m",
            "GRAY": "\033[1;90m",
            "LIGHT_RED": "\033[1;91m",
            "LIGHT_GREEN": "\033[1;92m",
            "LIGHT_YELLOW": "\033[1;93m",
            "LIGHT_BLUE": "\033[1;94m",
            "LIGHT_PURPLE": "\033[1;95m",
            "LIGHT_CYAN": "\033[1;96m",
            "LIGHT_WHITE": "\033[1;97m",
            "ORANGE": "\033[1;38;5;208m",
            "PINK": "\033[1;95m",
            "LIGHTBLUE": "\033[1;94m",
            "MAGENTA": "\033[1;95m",
            "NC":"\033[0m" # No Color
            }
            # "BOLD":"\033[1m",
            # "UNDERLINE":"\033[4m",
            # "BLINK":"\033[5m",
    
    def log(self, message, force_print=False, color="NC", save_it=True, save_to_large_log=False, reprint=True):
        # Add the message to the log entries
        log_prefix = self.get_log_prefix()
        
        
        printable_message = f"{self.shell_color_dict.get(color, "\033[0m")}\n{log_prefix}\n{message}{self.shell_color_dict.get("NC", "")}"
        
        # Shorten the log if it is too long
        if len(printable_message) > 1000:
            printable_message = f"{self.shell_color_dict.get(color, "\033[0m")}\n{log_prefix} -> \n\033[1;31m[TRUNCATED LOG]\033[0m\n{message[:1000]}{self.shell_color_dict.get("NC", "")} -> \033[1;31m[truncated due to length] ...\033[0m"

        # Add the log entry to the log_entries list
        self.log_entries.append([log_prefix, message, color, printable_message])
        
        print_it = False
        if color == "RED" or force_print or "Error".upper() in printable_message.upper():
            print_it = True
        
        # Print the message if it is an error or if force_print is True
        if not self.only_print_errors or print_it:
            print(printable_message)
        
        if save_to_large_log:
            with open(f"{self.large_log_file_path}", 'a') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: \n{message}\n\n\n\n")
                save_it = False
        
        if save_it:
            with open(self.log_file_path, 'w') as f:
                try: 
                    msgs = [f"{entry[2]}: {entry[0]} \n{entry[1]}\n" for entry in self.log_entries if entry]
                    all_logs = "\n".join(msgs)
                    f.write(all_logs)
                except Exception as e:
                    f.write(json.dumps(self.log_entries))
                    
    
    def error(self, message="", color="NC", print_it=True, save_it=True, save_to_large_log=False):
        self.log(message, color=color, print_it=print_it, save_it=save_it, save_to_large_log=save_to_large_log)
    
    def get_log_prefix(self):
        current_time = datetime.now()
        cumulative_time = current_time - self.start_time
        
        # Calculate the incremental time since the last log
        incremental_time = current_time - self.last_log_time
        
        
        # format the times as 00:00:00
        current_time_str = current_time.strftime("%H:%M:%S")
        cumulative_time_str = str(cumulative_time).split('.')[0]
        incremental_time_str = str(incremental_time).split('.')[0]
        
        # Note the current time as the last log time
        self.last_log_time = current_time
        
        log_prefix = f"[ N:{current_time_str}, C:{cumulative_time_str}, I:{incremental_time_str} ]"
        
        return log_prefix
    
    def reprint_log(self):
        print ("\n\n\n|--------------   REPRINTING LOG   --------------|")
        for entry in self.log_entries:
            print(entry[3])
    
    def reinit_log(self, output_folder="logs", only_print_errors=False, working_dir=None):
        # Set the working directory (default to the current directory)
        self.working_dir = working_dir
        if not self.working_dir:
            self.working_dir = os.getcwd()
        self.output_folder = output_folder
        
        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder): os.makedirs(output_folder)
        
        # Set Log Data and Metadata
        self.uid = f"{uuid.uuid4()}"
        self.start_time = datetime.now()
        self.last_log_time = self.start_time
        self.log_entries = []
        self.only_print_errors = only_print_errors
        
        #Complete log paths
        self.log_file_path = f"{self.working_dir}/{self.output_folder}/log_{self.start_time}_{self.uid}.txt"
        self.large_log_file_path = f"{self.working_dir}/{self.output_folder}/log_LARGE_{self.start_time}_{self.uid}.txt"
        
        
logger = Logger()