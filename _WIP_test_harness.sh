#!/bin/bash

# Clear the screen

ENCODED_CREDENTIALS=$(echo -n 'platform:local' | base64)

# echo -e "${ENCODED_CREDENTIALS}"

# user_registration=$(curl -k -X 'POST' 'https://localhost:5001/api/auth/register' -H 'accept: */*' -H 'Content-Type: application/json' -H 'Authorization: Basic ${ENCODED_CREDENTIALS}' -d '{"Email": "123@456.com", "Name": "123 string", "Password": "123abcDEF!!!"}')
# echo -e "${user_registration}"

# nats_login_json=$(curl -k -X 'POST' 'https://localhost:5001/api/auth/login' -H 'accept: application/json' -H 'Content-Type: application/json' -H 'Authorization: Basic ${ENCODED_CREDENTIALS}' -d '{"Email": "123@456.com", "Password": "123abcDEF!!!"}')
# echo -e "${nats_login_json}"

# # Extract Token and NatsJwt using jq
# NATS_TOKEN=$(echo "$nats_login_json" | jq -r '.Token')
# NATS_JWT=$(echo "$nats_login_json" | jq -r '.NatsJwt')

# # Export the values as environment variables
# export NATS_TOKEN
# export NATS_JWT

# # # Optional: Print the values to verify
# echo "NATS_TOKEN: $NATS_TOKEN"
# echo "NATS_JWT: $NATS_JWT"

# # Get the service key from the first argument
# KEY="$1$2$3"

# # Display the key being used
# echo -e "\033[1;97mKey: ${KEY}\033[0m"

# Define the absolute path to the JSON file
JSON_FILE_PATH="/Users/michasmi/code/mytech/docker/Utils/scripts/test_harness_queries.json"

# Extract the request string using jq, checking for errors
REQUEST=$(jq -r ".${KEY}" "$JSON_FILE_PATH" 2>/dev/null) # Redirect jq errors to /dev/null

if [ $? -ne 0 ] || [ -z "$REQUEST" ]; then # Check for both jq failure and empty result
    echo -e "\033[4;31mERROR: Key '$KEY' not found or empty in '$JSON_FILE_PATH'\033[0m"
    exit 1 # Exit the script if there's an error
fi

# Display service name and JSON payload
echo -e "> > KEY : \033[1;97m ${KEY}\033[0m"
echo -e "> > Service Called: \033[4;34m${1}\033[0m || from file: \033[4;34m${JSON_FILE_PATH}\033[0m"
echo -e "> > REQUEST JSON : \033[1;97m ${REQUEST}\033[0m"
# echo -e "> > Token: \033[1;97m ${COMMKEY}\033[0m"

# Send the request via nats (adjust the command as needed)
cd '/Users/michasmi/code/platform/Src/Api' &&
    nats req $1.$2 "${REQUEST}" -H Project:CMS -H Token:"${NATS_TOKEN}" # Use double quotes to preserve spaces in REQUEST

# nats req account.query '{}' -H Project:CMS -H Token:eyJ0eXAiOiJKV1QiLCAiYWxnIjoiZWQyNTUxOS1ua2V5In0.eyJhdWQiOiJjb21tdW5pZnkubG9jYWxob3N0IiwianRpIjoiTkZNVjVWQ0VUMzJDUkw1UjdBQVkzUVo3UFJVVFRMR1VKV0tIMzY2VFlUSUdENUtERlpOUSIsImlhdCI6MTcxOTU0MTEyOCwiaXNzIjoiQUNXTzJTTTU2RFQ3VTJWSzNWR1c1RVVFRjNXVERYV0o1UFhST05CRElKMlVCSEU1MzJaRUhKNEYiLCJuYW1lIjoibWljaGFlbEBqdXN0YnVpbGRpdC5jb20iLCJzdWIiOiJVRE80NlZTR1JRNFBIQzNOT0JGUFlWUlFESzZVSTNRWUpRWjJDNTdBTDRENEo3UEdOQ0JCS0Y1TiIsImV4cCI6MTcxOTkwMTEyOCwibmF0cyI6eyJpc3N1ZXJfYWNjb3VudCI6IkFCRDNaV1FYNERaTzcyRk1ZT1IzUlFSSUhYSkhFTENWUlVJUkdMSkJYR0c3RlNTQ0tBTENCSTJNIiwidGFncyI6WyJ0ZW5hbnQ9Y29tbXVuaWZ5Il0sInR5cGUiOiJ1c2VyIiwidmVyc2lvbiI6Miwic3VicyI6LTEsImRhdGEiOi0xLCJwYXlsb2FkIjotMX19.N0_kR94zb30RRCBWDxWLfFLPoAMxAtiC7axU_6Uzt1K2azdD99ctL21w_-DlNxtAX0DRGuwWvroVZJAKyqQ9AQ
# nats req privateasset.create '{"SymTicker": "NVDA", "AcquisitionCost":10000.01, "UnitsHeld": 100}' -H Project:CMS -H Token:$
# {"SymTicker": "NVDA"}
