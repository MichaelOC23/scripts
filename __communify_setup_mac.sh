#!/bin/bash
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
install_homebrew() {
    # Check if Homebrew is installed, if not, install it
    if ! command -v brew &>/dev/null; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >>/Users/$(whoami)/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        echo "Homebrew is already installed. Updating Homebrew..."
        brew update
    fi
}
# Function to install or upgrade Homebrew taps
install_or_upgrade_tap() {
    tap_name=$1

    if brew tap | grep -q "^$tap_name\$"; then
        echo "Tap $tap_name is already installed. Upgrading all formulae from $tap_name..."
        brew upgrade $(brew search --casks --formulae --taps $tap_name | grep -v "==> Formulae")
    else
        echo "Tapping $tap_name..."
        brew tap $tap_name
    fi
}

main() {

    export NG_CODE_DIR="${HOME}/code"
    export NG_PLATFORM_DIR="${NG_CODE_DIR}/platform"
    export NG_API_DIR="${NG_PLATFORM_DIR}/Src/Api"
    export NG_SETUP_DIR="${HOME}/.setup"
    mkdir -p ${NG_SETUP_DIR}

    # Export environment variables
    # export QUART_APP=AudioBackground

    C1="1) Mac Dev Libraries: Install Xcode, Rosetta, Homebrew, Git"
    C2="2) Dev Tools: Install Docker, Github, Node, Visual Studio Code, jq, pgAdmin4, DBeaver, Sublime Text, Zed, Postman"
    C3="3) Obtain Platform: Clone Platform Repository"
    C4="4) Nats: Install Nats and Nats Tools"
    C5="5) Configure Nats"
    C6="6) Install .NET"
    C7="7) Configure Nats"

    CHOICE1=${C1}
    CHOICE2=${C2}
    CHOICE3=${C3}
    CHOICE4=${C4}
    CHOICE5=${C5}
    CHOICE6=${C6}
    CHOICE7=${C7}

    echo -e "\033[1;32mPlatform Installation Script for Mac\033[0m"
    echo -e "${CHOICE1}\n${CHOICE2}\n${CHOICE3}\n${CHOICE4}\n${CHOICE5}\n${CHOICE6}\n${CHOICE7}\n"

    local choice
    read -p "Enter choice number (1, 2, 3, etc.): " choice
    case $choice in
    1)

        echo "Installing Xcode and Rosetta... this could take a while... please be patient."
        # Xcode Command Line Tools
        xcode-select --install
        softwareupdate --install-rosetta

        # Install or upgrade homebrew
        install_homebrew

        #Install or upgrade git
        install_or_upgrade git

        #Install Python 3.11
        install_or_upgrade python@3.11
        ;;

    2)

        echo -e "Installing Docker, Github, Node, Visual Studio Code, jq, pgAdmin4, DBeaver, Sublime Text, Zed, Postman, .NET, Portaudio, ffmpeg, Spacy, Postgres"

        # Install or upgrade packages and casks
        install_or_upgrade docker
        install_or_upgrade github
        brew install --cask dotnet-sdk

        #shell utils:
        install_or_upgrade install coreutils
        install_or_upgrade install jq

        # Install node and verify
        install_or_upgrade node
        node -v
        npm -v

        # Development Tools
        install_or_upgrade_cask visual-studio-code
        install_or_upgrade jq
        install_or_upgrade_cask pgadmin4
        install_or_upgrade_cask dbeaver-community
        install_or_upgrade_cask sublime-text
        install_or_upgrade_cask zed@preview
        install_or_upgrade_cask postman

        # Running Deepgram API
        install_or_upgrade portaudio
        install_or_upgrade ffmpeg

        # Language Processing
        pip install --upgrade spacy
        pip install --upgrade spacy-lookups-data
        python -m spacy download en_core_web_sm

        # Postgres
        install_or_upgrade postgresql
        brew services start postgresql
        brew services stop postgresql
        ;;

    3)
        cd ${HOME}
        #If the code directory does not exist, create it
        if [ ! -d "${NG_CODE_DIR}" ]; then
            mkdir -p ${NG_CODE_DIR}
        fi
        cd ${NG_CODE_DIR}
        git clone https://gitlab.com/jbitech/platform.git

        ;;

    4)

        # Install or upgrade Nats and Nats Tools
        brew tap nats-io/nats-tools # Tap the nats-io/nats-tools repository so that brew can connect
        install_or_upgrade nats-io/nats-tools/nats

        #Install NSC
        install_or_upgrade nats-io/nats-tools/nsc

        mkdir -p "${NG_API_DIR}/Repository"

        echo -e "\033[1;32m *FINISHED* \033[0m"
        ;;

    5)
        # Check if the stack 'platform' exists
        if docker stack ls | grep -q 'platform'; then
            echo "Stack 'platform' exists. Proceeding to remove services and the stack."

            # Remove all services in the stack
            docker stack services platform -q | xargs docker service rm

            # Remove the stack itself
            docker stack rm platform

            echo "All services and the stack 'platform' have been removed."
        else
            echo "Stack 'platform' does not exist. No action taken."
        fi

        sleep 3

        # IF nats-server is running, stop it with homebrew
        # brew services stop nats-server

        install_or_upgrade nats-server
        sleep 5

        # Run the nats-server command to start the server
        nats-server -c ${NG_PLATFORM_DIR}/Docker/Nats/nats.conf &

        # Navigate to the Platform directory
        cd ${NG_PLATFORM_DIR}

        # Run the following commands at the root level of the Platform
        nsc add operator --generate-signing-key --sys --name JBITech
        nsc edit operator --require-signing-keys
        nsc delete account Communify
        nsc add account --name Communify
        nsc edit account --name Communify --sk generate --js-mem-storage 10G --js-disk-storage 50G
        nsc generate config --nats-resolver --sys-account SYS >resolver.conf
        mv resolver.conf Docker/Nats/resolver.conf

        # Push the config into NATS
        cd ${NG_PLATFORM_DIR}/Docker/Nats

        # Push the config into NATS
        nsc push -A -u nats://127.0.0.1:4222

        # Add the platform account as a user in NATS
        nsc add user -a Communify platform

        # Generate the creds for the platform account
        nsc generate creds --account Communify -n platform >${NG_PLATFORM_DIR}/Docker/Nats/platform.creds

        nats context save local --creds "${NG_PLATFORM_DIR}/Docker/Nats/platform.creds" --server nats://127.0.0.1:4222 --select

        # Check if the output contains "nuget.org"
        # Run dotnet nuget list source and capture the output
        output=$(dotnet nuget list source)
        if [[ "$output" != *"nuget.org"* ]]; then
            echo "NuGet.org source not found. Adding NuGet.org source..."
            dotnet nuget add source https://api.nuget.org/v3/index.json --name NuGetOrg
        else
            echo "NuGet.org source already present."
        fi

        nsc list keys --show-seeds --all

        ;;
    6)

        # # Download the secrets.json file template
        # secret_path="${NG_API_DIR}/secrets.json"
        # echo -e "Downloading the secrets.json file template to ${secret_path} "
        # curl -o "${secret_path}" -L "https://jbiholdings-my.sharepoint.com/personal/michael_justbuildit_com/Documents/DONOTMOVE/secrets.json"

        #TEMP APPROACH - TAKE FROM LOCAL FILE
        secret_path="${NG_API_DIR}/secrets.json"
        echo -e "Copying the secrets.json file template to ${secret_path} "
        cp -f /Users/michasmi/Library/CloudStorage/OneDrive-JBIHoldingsLLC/DONOTMOVE/secrets.json "${NG_API_DIR}/secrets.json"
        sleep 2

        # Run the nsc list keys command and capture the output
        # nsc list keys --all
        # nsc list keys --show-seeds --all

        KEY_ID=$(nsc describe user platform --field nats.issuer_account)
        KEY_PUB=$(nsc describe user platform --field iss)
        KEY_PRI=$"SAACTJC3QQN6WZE3KNOJPNMJJWXQWR2KMJD53RJUPWJGCLTGIHMHS32OWY"

        KEY_ID=${KEY_ID//\"/}
        KEY_PUB=${KEY_PUB//\"/}
        KEY_PRI=${KEY_PRI//\"/}
        HOME_PLACEHOLDER="${HOME}"

        # Replace all instances of "KEY_PLACEHOLDER" with the value of "$KEY_PLACEHOLDER" in the file
        sed -i.bak "s/KEY_ID/${KEY_ID}/g" "${NG_API_DIR}/secrets.json"
        sed -i.bak "s/KEY_PUB/${KEY_PUB}/g" "${NG_API_DIR}/secrets.json"
        sed -i.bak "s/KEY_PRI/${KEY_PRI}/g" "${NG_API_DIR}/secrets.json"
        sed -i.bak "s/HOME_PLACEHOLDER/${HOME_PLACEHOLDER}/g" "${NG_API_DIR}/secrets.json"

        # Optional: Remove the backup file created by sed (secrets.json.bak)
        rm "${NG_API_DIR}/secrets.json.bak"

        echo -e "\033[1;96mFrom NATS, obtained the following 3 keys and updated the secrets.json file.\n   --->   KEY_ID: ${KEY_ID}\n   --->    KEY_PUBLIC: ${KEY_PUB}\n   --->   KEY_PRIVATE: ${KEY_PRIV}\033[0m"

        # Navigate to the API directory
        # Load the secrets.json file into the dotnet
        cd ${NG_API_DIR}
        cat secrets.json | dotnet user-secrets set

        # Trust the HTTPS certificate
        dotnet dev-certs https --trust

        # Start / Restart the Application
        # Launch Docker and remove the nats container (it is running locally)
        docker-compose up -d >/dev/null 2>&1

        # Wait for the application to start
        sleep 5

        # Remove the nats container (it is running locally)
        docker ps -a | grep 'nats:alpine' | awk '{print $1}' | xargs -I {} docker rm -f {}
        sleep 2

        # Install the dotnet ef tool
        dotnet tool install --global dotnet-ef
        sleep 3

        dotnet ef database update --project "${NG_API_DIR}/Api.csproj" --startup-project "${NG_API_DIR}/Api.csproj" --context Infrastructure.Repository.PlatformContext

        dotnet run --project "${NG_API_DIR}/Api.csproj"

        ;;
    7)
        cd ${NG_PLATFORM_DIR}
        echo -e "Navigating to directory: ${NG_PLATFORM_DIR}"
        echo -e "Running commands from: ${PWD}"

        nats-server -c ${NG_PLATFORM_DIR}/Docker/Nats/nats.conf
        docker-compose up -d >/dev/null 2>&1
        dotnet ef database update --project "${NG_API_DIR}/Api.csproj" --startup-project "${NG_API_DIR}/Api.csproj" --context Infrastructure.Repository.PlatformContext
        dotnet run --project "${NG_API_DIR}/Api.csproj"

        ;;
    *)
        echo "Exiting..."
        exit 0
        ;;

    esac
}

main

dotnet ef dbcontext list --project "${NG_API_DIR}/Api.csproj" --startup-project "${NG_API_DIR}/Api.csproj"

# NSC: Useful Commands

# Note: Operator/Account/User are: JBITech/Communify/platform
# mkdir -p ${HOME}/.setup
# mkdir -p ${HOME}/.setup/keys
# nsc export keys --operator --dir "${HOME}/.setup/keys/operator" --force
# nsc export keys --accounts --dir "${HOME}/.setup/keys/accounts" --force
# nsc export keys --users --dir "${HOME}/.setup/keys/users" --force
# nsc export keys --account Communify --dir "${HOME}/.setup/keys/account-communify" --force
# nsc export keys --user platform --dir "${HOME}/.setup/keys/user-platform" --force

# nsc list keys --all
# nsc list keys --show-seeds --all

#Create a new context
# nats context save local --creds platform.creds --server nats://127.0.0.1:4222 --select

# Select an existing context
# nats context select local

# Run the project explicitly
# dotnet run --project ${HOME}/code/platform/Src/Api/Api.csproj

# dotnet build --project

# Update the database
# dotnet ef database update --project Api.csproj --startup-project Api.csproj --context Infrastructure.Repository.PlatformContext

# nats-server -c ${NG_PLATFORM_DIR}/Docker/Nats/nats.conf
# nsc push -A -u nats://localhost:4222

# # Start the Backend
# cd ./Src/api
# dotnet run

# export API_DIR="${HOME}code/platform/Src/Api" && dotnet ef dbcontext list --project ${API_DIR}/Api.csproj --startup-project ${API_DIR}/Api.csproj

# dotnet ef database update --project "${NG_API_DIR}/Api.csproj" --startup-project "${NG_API_DIR}/Api.csproj" --context Infrastructure.Repository.ViewContext
# dotnet ef database update --project "${NG_API_DIR}/Api.csproj" --startup-project "${NG_API_DIR}/Api.csproj" --context Api.BasicCrudDbContext

Infrastructure.Repository.PlatformContext
Infrastructure.Repository.ViewContext
Api.BasicCrudDbContext
