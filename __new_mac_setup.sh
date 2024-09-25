#!/bin/bash

clear
echo "This script is designed to be run on a new Mac to set up the environment for business and development use."
echo "Each step is laid out below:"

SCRIPTS_PATH="${HOME}/code/scripts"
NSCCLI_PATH="${HOME}/.nsccli/bin"
DOTNET_PATH="${HOME}/.dotnet/tools"

# Function to deinitialize a Git repository

show_menu() {
    echo -e "\nSelect an option from the menu:"
    echo -e "1) Install Homebrew, Python, and Git Export Environment Variables and Grant Terminal Access to iCloud Drive"
    echo -e "2) Install Rossetta 1Password Cli and Dashlane Cli"
    echo -e "3) "
    echo -e "4) Install environment variables using the code-admin scripts"
    echo -e "5) Install Business Applications"
    echo -e "6) Install Development Applications"
    echo -e "7) Exit"
}

# Function to read the user's choice
read_choice() {
    local choice
    read -p "Enter your choice: " choice
    case $choice in
    1)
        option1
        ;;
    2)
        option2
        ;;
    3)
        option3
        ;;
    4)
        option4
        ;;
    5)
        option5
        ;;
    6)
        option6
        ;;
    7)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option, please try again."
        ;;
    esac
}

option1() {
    echo "You chose Option 1:"
    echo "This will install: Homebrew (a package manager), Python (a package), and Git (version control)"

    # Check if Homebrew is installed, if not, install it
    if ! check_homebrew_installed; then
        install_homebrew
        if ! check_homebrew_installed; then
            echo "Failed to install Homebrew. Cannot proceed with Git installation."
            exit 1
        fi
    fi

    # Check if Git is installed, if not, install it
    if ! check_git_installed; then
        install_git
        # Confirm the installation
        if check_git_installed; then
            echo "Git installation was successful."
        else
            echo "Git installation failed."
            exit 1
        fi
    fi

    # Add Homebrew to your PATH in /Users/yourname/.zprofile:
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >>$HOME/.zprofile
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >>$HOME/.zshrc
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >>$HOME/.bashrc

    # Install Python 3
    install_or_upgrade python3

    # Install MyTech
    cd ~
    mkdir -p code
    cd code
    git clone https://github.com/MichaelOC23/scripts.git

    # Setup the paths
    # UTIL_SLINK=".utils"
    # ln -s ${HOME}/code/mytech/docker/Utils ~/${UTIL_SLINK}

    # Define the content to be added
    CONTENT=$(
        cat <<'EOF'
# Your multi-line content here




eval "$(/opt/homebrew/bin/brew shellenv)"
source "${SCRIPTS_PATH}/env_variables.sh"

export NVM_DIR="$HOME/.nvm"
[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && \. "/opt/homebrew/opt/nvm/nvm.sh"

# This loads nvm add bash_completion
[ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && \. "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm"

export PATH="$PATH:$SCRIPTS_PATH:$NSCCLI_PATH:$DOTNET_PATH"
EOF
    )

    # List of paths to check
    paths_to_check=(
        "/opt/homebrew/bin/brew"
        "${HOME}/${UTIL_SLINK}/scripts/env_variables.sh"
        "/opt/homebrew/opt/nvm/nvm.sh"
        "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm"
    )

    # Check for the existence of each path/file
    for path in "${paths_to_check[@]}"; do
        if [ ! -e "$path" ]; then
            echo "Error: Path or file '$path' does not exist."
            echo "Please manually review the paths and files that are referenced in this script."
            echo "in Option 1 and adjust the imports needed in ~zshrc, ~zprofile, etc."
            echo "Then re-run Option 1 to complete the setup."
            exit 1
        fi
    done

    # Append the content to .zshrc and .zprofile
    echo "$CONTENT" >>~/.zshrc
    # echo "$CONTENT" >>~/.zprofile

    # Append the content to .bashrc and .bash_profile
    echo "$CONTENT" >>~/.bashrc
    # echo "$CONTENT" >>~/.bash_profile

    # Granting Terminal access to iCloud Drive
    echo -e "${LIGHTBLUE}Granting Terminal access to iCloud Drive${NC}"
    echo -e "import os\nprint(os.path.expanduser('~/Library/Mobile Documents/com~apple~CloudDocs'))" >${HOME}/Library/Mobile\ Documents/com~apple~CloudDocs/terminal_access.py
    cd ${HOME}/Library/Mobile\ Documents/com~apple~CloudDocs
    python3 ${HOME}/Library/Mobile\ Documents/com~apple~CloudDocs/terminal_access.py
    echo -e "${GREEN}You should now have access to iCloud Drive in the terminal${NC}"
}

option2() {
    echo "You chose Option 2:"
    echo "This will install Rosetta, the Dashlane CLI"

    # Install Rosetta
    echo "Installing Rosetta... this could take a while... please be patient."
    softwareupdate --install-rosetta

    # Dashlane CLI
    install_or_upgrade install dashlane/tap/dashlane-cli
    install_or_upgrade 1password-cli

    # Sync Dashlane
    echo -e "Please login with your Dashlane email address and password."
    echo -e "You CANNOT continue to step 3 until you have completed this step."
    echo -e "The command is: dcli sync, which will be executed now."
    dcli sync

    # echo "You chose Option 3:"
    # echo "This will create a DMG folder and disk image in ~/dmg"

    # # Create the dmg folder
    # mkdir -p ~/dmg
    # # Ask the user how big to make the data dmg, but suggest 200GB.
    # hdiutil create -size 300g -fs APFS -volname "data" -encryption AES-256 -stdinpass -attach ~/dmg/code.dmg

}

# option3() {

# }

option4() {
    echo "You chose Option 4:"
    echo "This will install environment variables using the code-admin scripts."
    echo "This will also add the code-admin scripts to your PATH"
    VSCODE_FOLDER_PATH="${HOME}/code/vscode/"
    echo -e "source ${SCRIPT_FOLDER}/env_variables.sh" >>~/.zshrc
    echo -e "source ${SCRIPT_FOLDER}/env_variables.sh" >>~/.zshrc
    echo -e "source ${SCRIPT_FOLDER}/env_variables.sh" >>~/.bashrc
}

option5() {
    echo "You chose Option 5:"
    echo "This will install Business Applications"

    # Business Apps
    install_or_upgrade_cask microsoft-office
    install_or_upgrade_cask microsoft-teams
    install_or_upgrade_cask dropbox
    install_or_upgrade_cask chatgpt

    # Browsers
    install_or_upgrade_cask microsoft-edge
    install_or_upgrade_cask google-chrome
    install_or_upgrade_cask firefox
    install_or_upgrade_cask arc
    install_or_upgrade_cask vivaldi
    install_or_upgrade_cask orion

    # Design
    install_or_upgrade_cask figma
    install_or_upgrade_cask adobe-creative-cloud

    # Communication Apps
    install_or_upgrade_cask zoom

    # Music
    install_or_upgrade_cask spotify

    # Security

    install_or_upgrade_cask private-internet-access

    # Recommended Installs from the Mac App Store: (print text out in CYAN)
    echo -e "${CYAN}Recommended Installs from the Mac App Store:${NC}"
    echo -e "${CYAN}---> Jump Desktop\n---> Daisy Disk\n---> Goodnotes\n---> Enchanted LLM\n{NC}"
    echo -e "${CYAN}---> Parallels\n---> HTML Editor\n---> Actions\n---> UTM LLM\n{NC}"
    echo -e "${CYAN}---> Power JSON Editor\n---> Microsoft To Do\n{NC}"
}

option6() {
    # Xcode Command Line Tools
    xcode-select --install

    # Install or upgrade packages and casks
    install_or_upgrade docker
    install_or_upgrade github

    # Install node and verify
    install_or_upgrade node
    node -v
    npm -v

    install_or_upgrade_cask visual-studio-code

    install_or_upgrade jq
    install_or_upgrade poppler
    install_or_upgrade_cask ollama
    install_or_upgrade_cask lm-studio
    install_or_upgrade openai-whisper

    install_or_upgrade_cask pgadmin4
    install_or_upgrade_cask google-cloud-sdk
    install_or_upgrade_cask chromedriver
    install_or_upgrade_cask dbeaver-community
    install_or_upgrade_cask sublime-text
    install_or_upgrade_cask postman
    install_or_upgrade_cask zed@preview
    install_or_upgrade_cask blackhole-2ch
    install_or_upgrade tesseract
    install_or_upgrade portaudio
    install_or_upgrade ffmpeg

    install_or_upgrade_cask google-cloud-sdk
    gcloud auth login
    gcloud config set project toolsexplorationfirebase

    # Language Processing
    pip install --upgrade spacy
    pip install --upgrade spacy-lookups-data
    python -m spacy download en_core_web_sm

    # Postgres
    install_or_upgrade postgresql
    brew services start postgresql
    brew services stop postgresql
}

clear

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if Homebrew is installed
check_homebrew_installed() {
    if brew --version &>/dev/null; then
        echo "Homebrew is already installed."
        return 0
    else
        echo "Homebrew is not installed."
        return 1
    fi
}

# Function to install Homebrew
install_homebrew() {
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add Homebrew to your PATH in /Users/yourname/.zprofile:
    eval "$(/opt/homebrew/bin/brew shellenv)"
}

# Function to check if Git is installed
check_git_installed() {
    if git --version &>/dev/null; then
        echo "Git is already installed."
        return 0
    else
        echo "Git is not installed."
        return 1
    fi
}

# Function to install Git
install_git() {
    echo "Installing Git..."
    brew install git
    echo "Installing GitHub CLI..."
    brew install gh
}

# Function to install or upgrade Homebrew packages
install_or_upgrade() {
    if brew list --formula | grep -q "^$1\$"; then
        echo "Upgrading $1..."
        brew upgrade $1
    else
        echo "Installing $1..."
        brew install $1
    fi
}

# Function to install or upgrade Homebrew casks
install_or_upgrade_cask() {
    if brew list --cask | grep -q "^$1\$"; then
        echo "Upgrading $1..."
        brew upgrade --cask $1
    else
        echo "Installing $1..."
        brew install --cask $1
    fi
}

# Main logic loop
while true; do
    show_menu
    read_choice
done
