#!/bin/bash
#Install Command
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/MichaelOC23/setup/main/jbi-init.sh)"

#Archvie the current .mytech folder if there is one

#Custom hidden root folder for JBI machines to install software
HOME_DIR="${HOME}"
cd "${HOME}"
echo "Current directory is ${PWD} after cd to ${HOME_DIR}"

JBI_FOLDER=".setup"
ARCHIVE_SUFFIX="-archive"
JBI_FOLDER_PATH="${HOME}/${JBI_FOLDER}"
ARCHIVE_FOLDER_DATE_NAME="$(date '+%Y-%m-%d_%H-%M-%S')"
ARCHIVE_FOLDER_DATE_PATH="${HOME}/${JBI_FOLDER}-${ARCHIVE_SUFFIX}/${ARCHIVE_FOLDER_DATE_NAME}"
echo "ARCHIVE_FOLDER_DATE_NAME is ${ARCHIVE_FOLDER_DATE_NAME}"
echo "JBI_FOLDER is ${JBI_FOLDER} and ARCHIVE_FOLDER_DATE_NAME is ${ARCHIVE_FOLDER_DATE_NAME} and JBI_FOLDER_PATH is ${JBI_FOLDER_PATH}"

# Check if the folder already exists, if so run some code
if [ -d "${JBI_FOLDER_PATH}" ]; then
    echo "JBI folder already exists."

    # Create the archive directory
    mkdir -p ${JBI_FOLDER}-${ARCHIVE_SUFFIX}
    cd ${JBI_FOLDER}-${ARCHIVE_SUFFIX}
    mkdir -p $ARCHIVE_FOLDER_DATE_NAME

    cd "${HOME}"

    # Now move the folder
    echo "Since the JBI_FOLDER exists we are going to move ${JBI_FOLDER_PATH} to ${ARCHIVE_FOLDER_DATE_PATH}"
    mv "${JBI_FOLDER_PATH}" "${ARCHIVE_FOLDER_DATE_PATH}"

else
    echo "JBI folder does not exist."
    # Add your code here to run when the folder does not exist
fi

git clone https://github.com/MichaelOC23/setup.git "${JBI_FOLDER_PATH}"

# Use 'move' to rename the folder (. folders are hidden)
# echo -p "about to mvoe setup to .jbi       "
# mv "${HOME}/setup" "${JBI_FOLDER_PATH}"

# Loop through each .sh file in the .jbi folder
for file in "${JBI_FOLDER_PATH}"/*.sh; do
    # Check if the file exists to avoid errors with non-existent files
    if [ -f "$file" ]; then
        # Make the file executable
        chmod u+x "$file"
        echo "Made executable: $file"
    fi
done

# Define the line to add
line_to_add='source "${HOME}/.jbi/env_variables.sh"'

# Define the path to your .zshrc
zshrc="$HOME/.zshrc"

# Check if the line already exists in .zshrc
if ! grep -Fxq "$line_to_add" "$zshrc"; then
    # If the line does not exist, append it
    echo "$line_to_add" >>"$zshrc"
    echo "Line added to .zshrc"
else
    echo "Line already in .zshrc"
fi

source "${HOME}/.zshrc"
echo "The jbi-init.sh script has been run successfully."
