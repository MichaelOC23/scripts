#Standard Imports
import json
import os
import shutil
from datetime import datetime



def WriteOut(LogTitle, TextToWrite, FilePath):
  try:
    with open(FilePath, 'a') as f:
      current_time = datetime.now()
      milliseconds = current_time.microsecond // 1000
      end_time = current_time.strftime("%Y-%m-%d %H:%M:%S") + f":{milliseconds}ms"
      
      if TextToWrite:
        if isinstance(TextToWrite, str):
          f.write(os.linesep+os.linesep + LogTitle + ": " + end_time + os.linesep + TextToWrite + os.linesep)
        elif isinstance(TextToWrite, dict):
          json_string = json.dumps(TextToWrite, indent=4)
          f.write(os.linesep+os.linesep + LogTitle + ": " + end_time + os.linesep + json_string + os.linesep)
        else:
          f.write(os.linesep + LogTitle + ": " + end_time + os.linesep + str(TextToWrite) + os.linesep)
      else:
          f.write(os.linesep + LogTitle + ": " + end_time + os.linesep)
    
      f.flush()
      f.close()

  except Exception as e:
    ErrMessage = 'Error writing to log with LogTitle: ' + LogTitle + "Error: " + os.linesep + str(e)
    print(ErrMessage)

def WriteOutJSON(JsonToWrite, FilePath, log_file):
  try:
    #Get the current date/time
    current_time = datetime.now()
    milliseconds = current_time.microsecond // 1000
    end_time = current_time.strftime("%Y-%m-%d %H:%M:%S") + f":{milliseconds}ms"
    
    # JsonToWrite is a list of dicts (have to transform it)
    json_data = json.dumps(JsonToWrite, indent=4)

    # Write out json_data string to file
    with open(FilePath, 'w') as f:  
      f.write(json_data)
      f.flush()
      f.close()
    LogMessage = 'Successfully exported JSON' + ' for ' + FilePath + ' at ' + end_time
    WriteOut(LogMessage, '', log_file)
    print(LogMessage)
    return  json_data
      
  except Exception as e:
    print("Error Exporting JSON: ", e)
    
def CreateFolderIfNotExist(folder):
  #get workling directory of this script
  current_dir = os.path.dirname(os.path.abspath(__file__))
  folder_path = os.path.join(current_dir, folder, '')
  
  # Create parent directories if they don't exist
  if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    print ('Created Directory (it did not exist)' + folder)

def CreateFileIfNotExist(file_path, log_file):

  # Create parent directories if needed
  directory = os.path.dirname(file_path)
  if not os.path.exists(directory):
    os.makedirs(directory)
    WriteOut('Created Directory (it did not exist)', directory, log_file)

  # Create file if it doesn't exist
  if not os.path.exists(file_path):
    open(file_path, 'w').close()
    #print(f'Created new file at {file_path}')
    WriteOut('Created File (it did not exist)', file_path, log_file)
  
  #Create a subfolder named Archive if it doesn't exist
  archive_path = os.path.join(directory, 'Archive')
  if not os.path.exists(archive_path):
      os.makedirs(archive_path)
      WriteOut('Created Directory (it did not exist)', archive_path, log_file)
      
  #Copy the file at file_path to the Archive folder and append the current date and time to the file
  archive_file = file_path.replace('.txt', f'_archive_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
  archive_file = file_path.replace('.json', f'_archive_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
  archive_file = archive_file.replace('Files/', 'Files/Archive/')
  shutil.copy2(file_path, archive_file)
  WriteOut('Created copy of the file at:' + os.linesep + file_path, 'at: ' + archive_path, log_file)
    
  #Create an empty file at file_path
  open(file_path, 'w').close()
  WriteOut('Created an empty file at:', file_path, log_file)

