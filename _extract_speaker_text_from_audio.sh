#!/bin/bash

# Run the curl command and store the JSON response in a variable
response=$(curl \
    --request POST \
    --header 'Authorization: Token a036e3a46669ca63fb31ef412ba47848e76efd03' \
    --header 'Content-Type: audio/m4a' \
    --data-binary '@/Users/michasmi/Library/Mobile Documents/iCloud~md~obsidian/Documents/_AudioRecordings/20200514 075846-CA2CFA57.m4a' \
    --url 'https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&diarize=true&punctuate=true')

# Extract the words array from the response using jq
words=$(echo "$response" | jq -c '.results.channels[0].alternatives[0].words')

# Initialize variables
# prior_speaker=-1
statement=""
statements=()

# Loop through each word in the response
echo "$words" | jq -c '.[]' | while read -r word; do
    speaker=$(echo "$word" | jq -r '.speaker')
    punctuated_word=$(echo "$word" | jq -r '.punctuated_word')

    echo -e "${response}"

    if [ "$prior_speaker" == "-1" ]; then
        prior_speaker="$speaker"
        statement="$punctuated_word"
        continue
    fi

    if [ "$speaker" == "$prior_speaker" ]; then
        statement="$statement $punctuated_word"
        continue
    fi

    if [ "$speaker" != "$prior_speaker" ]; then
        # Append the current statement to the list of statements
        statements+=("Speaker $prior_speaker: $statement")
        prior_speaker="$speaker"
        statement="$punctuated_word"
    fi
done

# Append the final statement
statements+=("Speaker $prior_speaker: $statement")

# Output the statements
for stmt in "${statements[@]}"; do
    echo "$stmt"
done
