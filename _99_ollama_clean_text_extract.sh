#!/bin/bash

# PROMPT="${1}"
# ORIG_FILE_PATH="${2}"
# OPENAI_API_KEY="${3}"
ENDPOINT="https://api.openai.com/v1/chat/completions"

# #Test Variables
PROMPT=" \n hell my \n nam   e is Jo   hn   laramie  \n"
ORIG_FILE_PATH="${HOME}/Downloads/test/testpdf.pdf"
OPENAI_API_KEY="${OPENAI_API_KEY}"

INSTRUCTIONS="Please transform the following OCR-extracted text into a clean, readable version that closely matches the original document.  1). Accuracy and Readability: Strive to correct any OCR errors, ensuring the text is readable and as accurate as possible.  2). Structure: Reconstruct sentence structures, headers, and footnotes appropriately.  3). Legal Context: This is a legal document, so maintain the integrity of the legal language.  4). Common Names: Preserve the names of organizations: Fincentric, Markit On Demand, Markit, S&P, and Wall Street On Demand. Do not alter these names.  5). Uncertain Words: If a word is unclear and is critical to the meaning of the sentence indicate uncertainty with a question mark in brackets [?].  Note I understand there may be some inaccuracies due to the quality of the OCR, but please make your best effort to ensure the text is as close to the original as possible. \n\n\n"

# Combine INSTRUCTIONS and PROMPT into REQUEST_FINAL
REQUEST_FINAL="${INSTRUCTIONS} ${PROMPT}"

# # Build the JSON request payload using jq to ensure proper escaping
# REQUEST_JSON=$(jq -n --arg content "$REQUEST_FINAL" '{
#   model: "llama3",
#   messages: [{"role": "user", "content": $content}],
#   temperature: 0.1
# }')

REQUEST_JSON=$(jq -n --arg content "$REQUEST_FINAL" '{
  "model": "llama3-gradient",
  "prompt": $content,
  "options": {
    "num_ctx": 64000
  }
}')

# Send the request to the OpenAI API
RESPONSE=$(curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer ${OPENAI_API_KEY}" -d "${REQUEST_JSON}" "${ENDPOINT}")

# Print the raw response for debugging purposes
echo "Raw response: ${RESPONSE}"

# Extract the message content from the response, or an error message
CONTENT=$(echo "${RESPONSE}" | jq -r '.choices[0].message.content // .error.message')

# Get the directory and filename without extension
DIR=$(dirname "${ORIG_FILE_PATH}")
FILENAME=$(basename "${ORIG_FILE_PATH}" .txt)

# Define the new file path with _clean.txt
NEW_FILE_PATH="${DIR}/${FILENAME}_clean.txt"

# Print the relevant content into the new file
echo "${CONTENT}" >"${NEW_FILE_PATH}"

# Print a message to confirm the file creation
echo "Extracted content has been saved to: ${NEW_FILE_PATH}"
