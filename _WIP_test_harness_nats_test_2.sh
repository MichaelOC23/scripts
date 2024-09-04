#!/bin/bash

# Clear the screen

ENCODED_CREDENTIALS=$(echo -n 'platform:local' | base64)

user_registration=$(curl -k -X 'POST' 'https://localhost:5001/api/auth/register' -H 'accept: */*' -H 'Content-Type: application/json' -H 'Authorization: Basic ${ENCODED_CREDENTIALS}' -d '{"Email": "123@456.com", "Name": "123 string", "Password": "123abcDEF!!!"}')

nats_login_json=$(curl -k -X 'POST' 'https://localhost:5001/api/auth/login' -H 'accept: application/json' -H 'Content-Type: application/json' -H 'Authorization: Basic ${ENCODED_CREDENTIALS}' -d '{"Email": "123@456.com", "Password": "123abcDEF!!!"}')

# Extract Token and NatsJwt using jq
NATS_TOKEN_STR=$(echo "$nats_login_json" | jq -r '.Token')

# Export the values as environment variables
export NATS_TOKEN="${NATS_TOKEN_STR}"

# # Optional: Print the values to verify

REQUES2='{"SymTicker": "MSFT", "AcquisitionCost": 10000.01, "AcquisitionDate": "2024-06-18", "UnitsHeld": 100, "RecordContext": "WATCHLIST"}'
# Send the request via nats (adjust the command as needed)
echo -e "\033[1;97mKey: ${REQUES2}\033[0m Token: ${NATS_TOKEN_STR}"
cd '/Users/michasmi/code/platform/Src/Api' &&
    nats req privateasset.create "${REQUES2}" -H Project:CMS -H Token:"${NATS_TOKEN}" # Use double quotes to preserve spaces in REQUEST


# cd '/Users/michasmi/code/platform/Src/Api' && nats req $1.$2 "${REQUEST}" -H Project:CMS -H Token:"${NATS_TOKEN}" # Use double quotes to preserve spaces in REQUEST

# nats req account.query '{}' -H Project:CMS -H Token:eyJ0eXAiOiJKV1QiLCAiYWxnIjoiZWQyNTUxOS1ua2V5In0.eyJhdWQiOiJjb21tdW5pZnkubG9jYWxob3N0IiwianRpIjoiTkZNVjVWQ0VUMzJDUkw1UjdBQVkzUVo3UFJVVFRMR1VKV0tIMzY2VFlUSUdENUtERlpOUSIsImlhdCI6MTcxOTU0MTEyOCwiaXNzIjoiQUNXTzJTTTU2RFQ3VTJWSzNWR1c1RVVFRjNXVERYV0o1UFhST05CRElKMlVCSEU1MzJaRUhKNEYiLCJuYW1lIjoibWljaGFlbEBqdXN0YnVpbGRpdC5jb20iLCJzdWIiOiJVRE80NlZTR1JRNFBIQzNOT0JGUFlWUlFESzZVSTNRWUpRWjJDNTdBTDRENEo3UEdOQ0JCS0Y1TiIsImV4cCI6MTcxOTkwMTEyOCwibmF0cyI6eyJpc3N1ZXJfYWNjb3VudCI6IkFCRDNaV1FYNERaTzcyRk1ZT1IzUlFSSUhYSkhFTENWUlVJUkdMSkJYR0c3RlNTQ0tBTENCSTJNIiwidGFncyI6WyJ0ZW5hbnQ9Y29tbXVuaWZ5Il0sInR5cGUiOiJ1c2VyIiwidmVyc2lvbiI6Miwic3VicyI6LTEsImRhdGEiOi0xLCJwYXlsb2FkIjotMX19.N0_kR94zb30RRCBWDxWLfFLPoAMxAtiC7axU_6Uzt1K2azdD99ctL21w_-DlNxtAX0DRGuwWvroVZJAKyqQ9AQ
# nats req privateasset.create '{"SymTicker": "NVDA", "AcquisitionCost":10000.01, "UnitsHeld": 100}' -H Project:CMS -H Token:$
# {"SymTicker": "NVDA"}
