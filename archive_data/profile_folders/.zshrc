# eval "$(/opt/homebrew/bin/brew shellenv)"

source /Users/michasmi/code/scripts/env_variables.sh

NSCCLI_PATH="${HOME}/.nsccli/bin"
DOTNET_PATH="${HOME}/.dotnet/tools"

export PATH="$PATH:/Users/michasmi/.nsccli/bin"
export PATH="$PATH:/Users/michasmi/.dotnet/tools"

export PATH=$PATH:/Users/michasmi/code/platform
export PATH="$PATH:/Users/michasmi/code/nats"

export NVM_DIR="$HOME/.nvm"
[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && \. "/opt/homebrew/opt/nvm/nvm.sh"

# This loads nvm
[ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && \. "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" # This loads nvm bash_completion
