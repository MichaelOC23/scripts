GREEN='\033[0;32m'
RED='\033[0;31m'

commit_current_folder() {
    cd "${HOME}/code/scripts"
    echo -e "Committing changes to current repository at: $PWD"
    git pull origin main
    git add .
    git commit -m "default commit message"
    git push origin main

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Commit Successful for ${PWD} ${NC}"
    else
        echo -e "${RED}!! ERROR !! Commit was not successful${NC}"
    fi
}
mkdir -p "${HOME}/code/scripts/automator" && cp ~/Library/Services/*.workflow "${HOME}/code/scripts/automator/"
commit_current_folder
