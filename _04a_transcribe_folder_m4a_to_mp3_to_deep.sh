#!/bin/bash

# Key folders
CODE_PATH="${HOME}/code"

#!/bin/bash

# Function to get the creation date of the file in YYYY-MM-DD format
get_creation_date() {
    # Using stat to get the creation date in YYYY-MM-DD format
    creation_date=$(stat -f "%SB" -t "%Y-%m-%d" "$1")
    echo "$creation_date"
}

SOURCE_FOLDER="/Users/michasmi/Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings"
DESTINATION_FOLDER="/Users/michasmi/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes By Michael/Transcriptions/.audio"

# Scripts Paths
SCRIPT_PATH="${CODE_PATH}/scripts"
SCRIPT_VENV_PATH="${SCRIPT_PATH}/scripts_venv/bin/activate"
SCRIPT_PYTHON_PATH="${SCRIPT_PATH}/scripts_venv/bin/python"

#Folder path to process
FOLDER_PATH=""

if [ -z "$1" ]; then
    # If no argument is provided, set val to the current working directory
    FOLDER_PATH="${SOURCE_FOLDER}"
elif [ "$1" = "." ]; then
    # If the argument is ".", set val to the current working directory
    FOLDER_PATH="$(pwd)"
else
    # If the argument exists and is not ".", set val to the argument value
    FOLDER_PATH="$1"
fi

# Define the base directory
BASE_DIR="${TRANSCRIPTION_BASE_DIR}"

# Create the new directory
TRANS_DIR="$BASE_DIR/.trans_json"
mkdir -p "$TRANS_DIR"

# Create the new directory
CONVERTED_AUDIO_DIR="$BASE_DIR/.audio"
mkdir -p "$CONVERTED_AUDIO_DIR"

# echo all the variables
echo -e "FOLDER_PATH: ${FOLDER_PATH}"
echo -e "BASE_DIR: ${BASE_DIR}"
echo -e "CURRENT_DATE: ${CURRENT_DATE}"
echo -e "Converted Audio Directory: ${CONVERTED_AUDIO_DIR}"
echo -e "JSON Transcription Folder: ${TRANS_DIR}"

# Define the folder containing the files as the current working directory
AUTH_TOKEN=${DEEPGRAM_API_KEY}
BIT_RATE="64k"
DEEPGRAM_URL="https://api.deepgram.com/v1/listen?topics=true&smart_format=true&punctuate=true&paragraphs=true&keywords=Sales%3A3&keywords=Marketing%3A3&keywords=Product%3A3&keywords=Client%3A3&keywords=Prospect%3A3&diarize=true&sentiment=true&language=en&model=nova-2"

echo -e "Beginning m4a to mp3 conversion and transcription for files in folder: \033[1;95m${FOLDER_PATH}\033[0m"
echo -e "Transcriptions will be saved in: \033[1;95m${TRANS_DIR}\033[0m"
shopt -s nullglob


AUDIO_COPIES="${HOME}/.audio_copies"
mkdir -p "${AUDIO_COPIES}"

echo -e "Source folder: ${FOLDER_PATH}"
echo -e "Copies dest folder: ${AUDIO_COPIES}"

cp -R "$FOLDER_PATH"/* "$AUDIO_COPIES"

# Loop through all files in the folder
for file in "${AUDIO_COPIES}"/*; do
    echo -e "\033[1;95mProcessing file: $file\033[0m"
    if [[ "$file" == *.m4a || "$file" == *.mp3 || "$file" == *.wav ||
        "$file" == *.aac || "$file" == *.flac || "$file" == *.ogg ||
        "$file" == *.wma || "$file" == *.aiff || "$file" == *.opus ||
        "$file" == *.amr || "$file" == *.mp2 ||
        "$file" == *.mp4 || "$file" == *.avi || "$file" == *.mkv ||
        "$file" == *.mov || "$file" == *.flv || "$file" == *.wmv ||
        "$file" == *.webm ]]; then
        # echo -e "\033[1;95mProcessing file: $file\033[0m"

        # Get the base name of the file without extension
        FILE_NAME_ONLY=$(basename "$file")
        BASE_NAME="${FILE_NAME_ONLY%.*}"

        echo "Base name: $BASE_NAME"

        MP3_FILE_NAME="${FILE_NAME_ONLY}.mp3"
        MP3_FILE_PATH="${CONVERTED_AUDIO_DIR}/${MP3_FILE_NAME}"

        TRANS_FILE_NAME="${FILE_NAME_ONLY}.json"
        TRANS_FILE_PATH="${TRANS_DIR}/${TRANS_FILE_NAME}"

        # echoe out all path variables
        echo -e "MP3_FILE_NAME: ${MP3_FILE_NAME}"
        echo -e "MP3_FILE_PATH: ${MP3_FILE_PATH}"

        echo -e "TRANS_FILE_NAME: ${TRANS_FILE_NAME}"
        echo -e "TRANS_FILE_PATH: ${TRANS_FILE_PATH}"

        # If a transcription exists, move to the next file
        if [[ -f "${TRANS_FILE_PATH}" ]]; then
            echo -e "${ORANGE}Skipping conversion for ${TRANS_FILE_PATH}, transcription already exists.\033[0m"
            continue
        fi

        # If an mp3 file does not exist, create an mp3 version of the file.
        if [[ ! -f "${MP3_FILE_PATH}" ]]; then
            echo -e "${GREEN}Beginning conversion of ${file} to mp3.\033[0m"
            ffmpeg -i "$file" -b:a $BIT_RATE "${MP3_FILE_PATH}" && echo -e "\033[0;32mConversion COMPLETE to ${MP3_FILE_NAME}.\033[0m"
        fi

        # Extract metadata using ffprobe
        metadata=$(ffprobe -v quiet -show_format -show_entries format_tags=creation_time,title,voice-memo-uuid,duration -of json "$file")
        echo -e "Metadata: $metadata"

        # Extract the creation time, title, UUID, and duration
        creation_time=$(echo "$metadata" | jq -r '.format.tags.creation_time // empty')
        title=$(echo "$metadata" | jq -r '.format.tags.title // empty')
        uuid=$(echo "$metadata" | jq -r '.format.tags["voice-memo-uuid"] // empty')
        duration=$(echo "$metadata" | jq -r '.format.duration')

        echo -e "Creation Time 1: $creation_time"

        # If creation_time is empty, use the file modification date
        if [ -z "$creation_time" ]; then
            creation_time=$(date -r "$m4a_file" +"%Y-%m-%dT%H:%M:%S")
        fi
        echo -e "Creation Time 2: $creation_time"

        # Format creation time as YY.MM.DD
        cleaned_time="${creation_time%%.*}Z"
        creation_date=$(date -jf "%Y-%m-%dT%H:%M:%S%z" "${cleaned_time//Z/+0000}" +"%y.%m.%d")
        echo -e "Creation Date: $creation_date"
        # Use the title or UUID, prioritize title
        file_name_part="${title:-$uuid}"

        # # Get the current year and month in YYYY-MM format
        # CURRENT_DATE=$(date +"%Y-%m")

        # Create the new directory
        TEXT_TRANS_DIR="$BASE_DIR/$creation_date"
        mkdir -p "$TEXT_TRANS_DIR"

        # Calculate duration in minutes and seconds
        duration_min=$(printf "%.0f" "$(echo "$duration / 60" | bc -l)")
        duration_sec=$(printf "%.0f" "$(echo "$duration % 60" | bc -l)")
        duration_formatted="${duration_min}min.${duration_sec}sec"

        # Construct the final file name
        TEXT_TRAN_FILE_NAME="${creation_date}.${file_name_part}.${duration_formatted}.md"
        DIARIZED_TEXT_TRAN_FILE_NAME="${creation_date}.${file_name_part}.diarized.${duration_formatted}.md"
        TEXT_TRAN_FILE_PATH="${TEXT_TRANS_DIR}/${TEXT_TRAN_FILE_NAME}"
        cd "${SCRIPTS_PATH}" && source "${SCRIPT_VENV_PATH}"
        if [[ ! -f "${TRANS_FILE_PATH}" ]]; then
            rm -rf "${TEXT_TRAN_FILE_PATH}"
            echo -e "\033[1;95m Connecting to Deepgram to transcribe ${MP3_FILE_NAME}\033[0m"
            # Run the curl command to process the mp3 file with Deepgram API
            curl -X POST \
                -H "Authorization: Token $AUTH_TOKEN" \
                --header 'Content-Type: audio/wav' \
                --data-binary @"${MP3_FILE_PATH}" \
                "$DEEPGRAM_URL" >"${TRANS_FILE_PATH}"
            sleep 2

            # jq -r '.results.channels[0].alternatives[0].transcript' "$TRANS_FILE_PATH" >"${TEXT_TRANS_DIR}/${TEXT_TRAN_FILE_NAME}" && \
            jq -r '.results.utterances[] | "Speaker \(.speaker): \(.transcript)"' "${TRANS_FILE_PATH}" >"${TEXT_TRANS_DIR}/${DIARIZED_TEXT_TRAN_FILE_NAME}"

            echo -e "\033[0;32mBeginning transcription and summarization of ${TEXT_TRAN_FILE_NAME}\033[0m"
        fi
        if [[ ! -f "${TEXT_TRAN_FILE_PATH}" ]]; then
            eval "${SCRIPT_PYTHON_PATH} \"${SCRIPTS_PATH}/_04b_summarize_transcript_gemini.py\" \"${TRANS_FILE_PATH}\" \"${TEXT_TRAN_FILE_PATH}\""
        fi
    fi
done
wait
