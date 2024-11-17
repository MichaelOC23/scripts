#!/bin/bash

# Print the first argument
echo "First argument: ${1}"

ENDPOINT="https://api.openai.com/v1/chat/completions"
HEADERS="Content-Type: application/json"
PROMPT="${1}"

# Build the JSON request payload
REQUEST=$(
      cat <<EOF
{
  "model": "gpt-40-mini",
  "messages": [{"role": "user", "content": "${PROMPT}"}],
  "temperature": 0.1
}
EOF
)

# Print the request for debugging purposes
echo "Request payload: ${REQUEST}"

# Send the request to the OpenAI API
RESPONSE=$(curl -X POST -H "${HEADERS}" -H "Authorization: Bearer ${OPENAI_API_KEY}" -d "${REQUEST}" "${ENDPOINT}")

# Print the raw response for debugging purposes
echo "Raw response: ${RESPONSE}"

# Extract the message content from the response, or an error message
CONTENT=$(echo "${RESPONSE}" | jq -r '.choices[0].message.content // .error.message')

# Print the relevant content
echo "Extracted content: ${CONTENT}"
