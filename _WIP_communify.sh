#!/bin/bash

clear

# Key folders
PLATFORM_PATH="${HOME}/code/platform"
PLATFORM_API_PATH="${HOME}/code/platform/Src/Api"
PLATFORM_PROJECT="${PLATFORM_PATH}/Src/Api/Api.csproj"
FRONTEND_PATH="${HOME}/code/frontend"

#MyTech Scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color Variables for text
BLACK='\033[0;30m'
RED='\033[0;31m'
RED_BLINK='\033[5;31m'
GREEN='\033[0;32m'
GREEN_BLINK='\033[5;32m'
YELLOW_BOLD='\033[1;33m'
PURPLE='\033[1;34m'
PINK='\033[0;35m'
LIGHTBLUE_BOLD='\033[1;36m'
ORANGE='\033[1;91m'
CYAN='\033[1;96m'
MAGENTA='\033[1;95m'
BOLD='\033[1m'
UNDERLINE='\033[4m'
BLINK='\033[5m'

NC='\033[0m' # No Color

# Function to display the menu
show_menu() {
    echo -e "\n\n${LIGHTBLUE_BOLD}Hello! What would you like to do?"
    echo -e "Please choose one of the following options (enter the number):\n"
    echo -e "|-------------------------------------------------------------|${NC}\n"

    echo -e "${PURPLE}1) Update Communify${NC}"
    echo -e "${PURPLE}2) Launch Communify${NC}"

}

# Function to read the user's choice
read_choice() {
    local choice
    read -p "Enter choice [0 - 10]: " choice
    case $choice in

    1)
        run_frontend &
        run_platform
        # cd "${PLATFORM_API_PATH}"
        # dotnet ef database update --project Api.csproj --startup-project Api.csproj --context Infrastructure.Repository.PlatformContext
        # c_start_backend.sh &
        # cd $FRONTEND_PATH && npm I && npm start
        ;;
    2) ;;
    3) ;;
    4) ;;
    5) ;;
    6) ;;
    7) ;;
    8) ;;
    9) ;;
    *)
        echo "Invalid choice. Exiting ..."
        exit 0
        ;;
    esac
}

# Function to ask for confirmation
confirm() {
    while true; do
        read -p "$1 ( ${PURPLE}Yy or ${PINK_U}Nn ${NC}): " yn
        case $yn in
        [Yy]*) return 0 ;;                                                     # User responded yes
        [Nn]*) return 1 ;;                                                     # User responded no
        *) echo "${RED_BLINK}Please answer Y for 'yes' or N for 'no'.${NC}" ;; # Invalid response
        esac
    done
}

# Main logic loop
while true; do
    show_menu
    read_choice
done



[3:09 PM] Ricardo Georgel
nats req mutableasset.query '{"Item": {"Name":"get1", "Tickers":["AAA"]}}' -H Project:CMS -H Token:eyJ0eXAiOiJKV1QiLCAiYWxnIjoiZWQyNTUxOS1ua2V5In0.eyJhdWQiOiJjb21tdW5pZnkubG9jYWxob3N0IiwianRpIjoiTkZNVjVWQ0VUMzJDUkw1UjdBQVkzUVo3UFJVVFRMR1VKV0tIMzY2VFlUSUdENUtERlpOUSIsImlhdCI6MTcxOTU0MTEyOCwiaXNzIjoiQUNXTzJTTTU2RFQ3VTJWSzNWR1c1RVVFRjNXVERYV0o1UFhST05CRElKMlVCSEU1MzJaRUhKNEYiLCJuYW1lIjoibWljaGFlbEBqdXN0YnVpbGRpdC5jb20iLCJzdWIiOiJVRE80NlZTR1JRNFBIQzNOT0JGUFlWUlFESzZVSTNRWUpRWjJDNTdBTDRENEo3UEdOQ0JCS0Y1TiIsImV4cCI6MTcxOTkwMTEyOCwibmF0cyI6eyJpc3N1ZXJfYWNjb3VudCI6IkFCRDNaV1FYNERaTzcyRk1ZT1IzUlFSSUhYSkhFTENWUlVJUkdMSkJYR0c3RlNTQ0tBTENCSTJNIiwidGFncyI6WyJ0ZW5hbnQ9Y29tbXVuaWZ5Il0sInR5cGUiOiJ1c2VyIiwidmVyc2lvbiI6Miwic3VicyI6LTEsImRhdGEiOi0xLCJwYXlsb2FkIjotMX19.N0_kR94zb30RRCBWDxWLfFLPoAMxAtiC7axU_6Uzt1K2azdD99ctL21w_-DlNxtAX0DRGuwWvroVZJAKyqQ9AQ


nats req watchlists.query '{"Name":"g"}' -H Project:CMS -H Token:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJhM2E1ZWJjYi00NGYyLTQ5ZjMtYjIyNS0yNDQzYzYzZGNhZGMiLCJ1bmlxdWVfbmFtZSI6Im1pY2hhZWxAanVzdGJ1aWxkaXQuY29tIiwiZW1haWwiOiJtaWNoYWVsQGp1c3RidWlsZGl0LmNvbSIsImdpdmVuX25hbWUiOiJNaWNoYWVsIFNtaXRoIiwidGVuYW50X2lkIjoiODMyZTM1MjAtYzM0OS00ZWQ2LWJmMjktNTNhNTUxOTc4MmM2IiwidGVuYW50IjoiY29tbXVuaWZ5IiwibmJmIjoxNzE1MjA5OTc5LCJleHAiOjE3MTU1Njk5NzgsImlhdCI6MTcxNTIwOTk3OCwiaXNzIjoiQUJEM1pXUVg0RFpPNzJGTVlPUjNSUVJJSFhKSEVMQ1ZSVUlSR0xKQlhHRzdGU1NDS0FMQ0JJMk0iLCJhdWQiOiJjb21tdW5pZnkubG9jYWxob3N0In0.kUlIvIUtNEEHyYa6FMShSyy8ZCjTD8dSHrNCSV3_KnM

nats req watchlists.get '{"Id":"d9801a93-d50d-4a1d-ac19-294816dede7b"}' -H Project:CMS -H Token:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJhM2E1ZWJjYi00NGYyLTQ5ZjMtYjIyNS0yNDQzYzYzZGNhZGMiLCJ1bmlxdWVfbmFtZSI6Im1pY2hhZWxAanVzdGJ1aWxkaXQuY29tIiwiZW1haWwiOiJtaWNoYWVsQGp1c3RidWlsZGl0LmNvbSIsImdpdmVuX25hbWUiOiJNaWNoYWVsIFNtaXRoIiwidGVuYW50X2lkIjoiODMyZTM1MjAtYzM0OS00ZWQ2LWJmMjktNTNhNTUxOTc4MmM2IiwidGVuYW50IjoiY29tbXVuaWZ5IiwibmJmIjoxNzE1MjA5OTc5LCJleHAiOjE3MTU1Njk5NzgsImlhdCI6MTcxNTIwOTk3OCwiaXNzIjoiQUJEM1pXUVg0RFpPNzJGTVlPUjNSUVJJSFhKSEVMQ1ZSVUlSR0xKQlhHRzdGU1NDS0FMQ0JJMk0iLCJhdWQiOiJjb21tdW5pZnkubG9jYWxob3N0In0.kUlIvIUtNEEHyYa6FMShSyy8ZCjTD8dSHrNCSV3_KnM

nats req watchlists.delete '{"Id":"2483a249-9ebe-48f0-bb30-27390a6679e9"}' -H Project:CMS -H Token:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJhM2E1ZWJjYi00NGYyLTQ5ZjMtYjIyNS0yNDQzYzYzZGNhZGMiLCJ1bmlxdWVfbmFtZSI6Im1pY2hhZWxAanVzdGJ1aWxkaXQuY29tIiwiZW1haWwiOiJtaWNoYWVsQGp1c3RidWlsZGl0LmNvbSIsImdpdmVuX25hbWUiOiJNaWNoYWVsIFNtaXRoIiwidGVuYW50X2lkIjoiODMyZTM1MjAtYzM0OS00ZWQ2LWJmMjktNTNhNTUxOTc4MmM2IiwidGVuYW50IjoiY29tbXVuaWZ5IiwibmJmIjoxNzE1MjA5OTc5LCJleHAiOjE3MTU1Njk5NzgsImlhdCI6MTcxNTIwOTk3OCwiaXNzIjoiQUJEM1pXUVg0RFpPNzJGTVlPUjNSUVJJSFhKSEVMQ1ZSVUlSR0xKQlhHRzdGU1NDS0FMQ0JJMk0iLCJhdWQiOiJjb21tdW5pZnkubG9jYWxob3N0In0.kUlIvIUtNEEHyYa6FMShSyy8ZCjTD8dSHrNCSV3_KnM

nats req watchlists.update '{"Item": {"Name":"not-get-boo", "Tickers":["AAPL"], "Id":"d9801a93-d50d-4a1d-ac19-294816dede7b"}}' -H Project:CMS -H Token:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJhM2E1ZWJjYi00NGYyLTQ5ZjMtYjIyNS0yNDQzYzYzZGNhZGMiLCJ1bmlxdWVfbmFtZSI6Im1pY2hhZWxAanVzdGJ1aWxkaXQuY29tIiwiZW1haWwiOiJtaWNoYWVsQGp1c3RidWlsZGl0LmNvbSIsImdpdmVuX25hbWUiOiJNaWNoYWVsIFNtaXRoIiwidGVuYW50X2lkIjoiODMyZTM1MjAtYzM0OS00ZWQ2LWJmMjktNTNhNTUxOTc4MmM2IiwidGVuYW50IjoiY29tbXVuaWZ5IiwibmJmIjoxNzE1MjA5OTc5LCJleHAiOjE3MTU1Njk5NzgsImlhdCI6MTcxNTIwOTk3OCwiaXNzIjoiQUJEM1pXUVg0RFpPNzJGTVlPUjNSUVJJSFhKSEVMQ1ZSVUlSR0xKQlhHRzdGU1NDS0FMQ0JJMk0iLCJhdWQiOiJjb21tdW5pZnkubG9jYWxob3N0In0.kUlIvIUtNEEHyYa6FMShSyy8ZCjTD8dSHrNCSV3_KnM

nats req watchlists.update '{"Item": {"Name":"not-get-boo", "Tickers":["AAPL"], "AddTicker": "CSCO", "Id":"d9801a93-d50d-4a1d-ac19-294816dede7b"}}' -H Project:CMS -H Token:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJhM2E1ZWJjYi00NGYyLTQ5ZjMtYjIyNS0yNDQzYzYzZGNhZGMiLCJ1bmlxdWVfbmFtZSI6Im1pY2hhZWxAanVzdGJ1aWxkaXQuY29tIiwiZW1haWwiOiJtaWNoYWVsQGp1c3RidWlsZGl0LmNvbSIsImdpdmVuX25hbWUiOiJNaWNoYWVsIFNtaXRoIiwidGVuYW50X2lkIjoiODMyZTM1MjAtYzM0OS00ZWQ2LWJmMjktNTNhNTUxOTc4MmM2IiwidGVuYW50IjoiY29tbXVuaWZ5IiwibmJmIjoxNzE1MjA5OTc5LCJleHAiOjE3MTU1Njk5NzgsImlhdCI6MTcxNTIwOTk3OCwiaXNzIjoiQUJEM1pXUVg0RFpPNzJGTVlPUjNSUVJJSFhKSEVMQ1ZSVUlSR0xKQlhHRzdGU1NDS0FMQ0JJMk0iLCJhdWQiOiJjb21tdW5pZnkubG9jYWxob3N0In0.kUlIvIUtNEEHyYa6FMShSyy8ZCjTD8dSHrNCSV3_KnM

nats req watchlists.update '{"Item": { "Name":"not-get-boo", "Tickers":["AAPL"], "Id":"d9801a93-d50d-4a1d-ac19-294816dede7b"}}' -H Project:CMS -H Token:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJhM2E1ZWJjYi00NGYyLTQ5ZjMtYjIyNS0yNDQzYzYzZGNhZGMiLCJ1bmlxdWVfbmFtZSI6Im1pY2hhZWxAanVzdGJ1aWxkaXQuY29tIiwiZW1haWwiOiJtaWNoYWVsQGp1c3RidWlsZGl0LmNvbSIsImdpdmVuX25hbWUiOiJNaWNoYWVsIFNtaXRoIiwidGVuYW50X2lkIjoiODMyZTM1MjAtYzM0OS00ZWQ2LWJmMjktNTNhNTUxOTc4MmM2IiwidGVuYW50IjoiY29tbXVuaWZ5IiwibmJmIjoxNzE1MjA5OTc5LCJleHAiOjE3MTU1Njk5NzgsImlhdCI6MTcxNTIwOTk3OCwiaXNzIjoiQUJEM1pXUVg0RFpPNzJGTVlPUjNSUVJJSFhKSEVMQ1ZSVUlSR0xKQlhHRzdGU1NDS0FMQ0JJMk0iLCJhdWQiOiJjb21tdW5pZnkubG9jYWxob3N0In0.kUlIvIUtNEEHyYa6FMShSyy8ZCjTD8dSHrNCSV3_KnM

nats req watchlists.update '{"Item": { "AddTicker":"LLL", "Id":"d9801a93-d50d-4a1d-ac19-294816dede7b"}}' -H Project:CMS -H Token:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJhM2E1ZWJjYi00NGYyLTQ5ZjMtYjIyNS0yNDQzYzYzZGNhZGMiLCJ1bmlxdWVfbmFtZSI6Im1pY2hhZWxAanVzdGJ1aWxkaXQuY29tIiwiZW1haWwiOiJtaWNoYWVsQGp1c3RidWlsZGl0LmNvbSIsImdpdmVuX25hbWUiOiJNaWNoYWVsIFNtaXRoIiwidGVuYW50X2lkIjoiODMyZTM1MjAtYzM0OS00ZWQ2LWJmMjktNTNhNTUxOTc4MmM2IiwidGVuYW50IjoiY29tbXVuaWZ5IiwibmJmIjoxNzE1MjA5OTc5LCJleHAiOjE3MTU1Njk5NzgsImlhdCI6MTcxNTIwOTk3OCwiaXNzIjoiQUJEM1pXUVg0RFpPNzJGTVlPUjNSUVJJSFhKSEVMQ1ZSVUlSR0xKQlhHRzdGU1NDS0FMQ0JJMk0iLCJhdWQiOiJjb21tdW5pZnkubG9jYWxob3N0In0.kUlIvIUtNEEHyYa6FMShSyy8ZCjTD8dSHrNCSV3_KnM

nats req watchlists.update '{"Item": { "AddTicker":"AA", "Id":"d9801a93-d50d-4a1d-ac19-294816dede7b"}}' -H Project:CMS -H Token:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJhM2E1ZWJjYi00NGYyLTQ5ZjMtYjIyNS0yNDQzYzYzZGNhZGMiLCJ1bmlxdWVfbmFtZSI6Im1pY2hhZWxAanVzdGJ1aWxkaXQuY29tIiwiZW1haWwiOiJtaWNoYWVsQGp1c3RidWlsZGl0LmNvbSIsImdpdmVuX25hbWUiOiJNaWNoYWVsIFNtaXRoIiwidGVuYW50X2lkIjoiODMyZTM1MjAtYzM0OS00ZWQ2LWJmMjktNTNhNTUxOTc4MmM2IiwidGVuYW50IjoiY29tbXVuaWZ5IiwibmJmIjoxNzE1MjA5OTc5LCJleHAiOjE3MTU1Njk5NzgsImlhdCI6MTcxNTIwOTk3OCwiaXNzIjoiQUJEM1pXUVg0RFpPNzJGTVlPUjNSUVJJSFhKSEVMQ1ZSVUlSR0xKQlhHRzdGU1NDS0FMQ0JJMk0iLCJhdWQiOiJjb21tdW5pZnkubG9jYWxob3N0In0.kUlIvIUtNEEHyYa6FMShSyy8ZCjTD8dSHrNCSV3_KnM

nats req watchlists.update '{"Item": { "RemoveTicker":"LLL", "Id":"d9801a93-d50d-4a1d-ac19-294816dede7b"}}' -H Project:CMS -H Token:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJhM2E1ZWJjYi00NGYyLTQ5ZjMtYjIyNS0yNDQzYzYzZGNhZGMiLCJ1bmlxdWVfbmFtZSI6Im1pY2hhZWxAanVzdGJ1aWxkaXQuY29tIiwiZW1haWwiOiJtaWNoYWVsQGp1c3RidWlsZGl0LmNvbSIsImdpdmVuX25hbWUiOiJNaWNoYWVsIFNtaXRoIiwidGVuYW50X2lkIjoiODMyZTM1MjAtYzM0OS00ZWQ2LWJmMjktNTNhNTUxOTc4MmM2IiwidGVuYW50IjoiY29tbXVuaWZ5IiwibmJmIjoxNzE1MjA5OTc5LCJleHAiOjE3MTU1Njk5NzgsImlhdCI6MTcxNTIwOTk3OCwiaXNzIjoiQUJEM1pXUVg0RFpPNzJGTVlPUjNSUVJJSFhKSEVMQ1ZSVUlSR0xKQlhHRzdGU1NDS0FMQ0JJMk0iLCJhdWQiOiJjb21tdW5pZnkubG9jYWxob3N0In0.kUlIvIUtNEEHyYa6FMShSyy8ZCjTD8dSHrNCSV3_KnM

nats req watchlists.update '{"Item": { "Name":"not-get-booaskdjf", "Id":"d9801a93-d50d-4a1d-ac19-294816dede7b"}}' -H Project:CMS -H Token:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJhM2E1ZWJjYi00NGYyLTQ5ZjMtYjIyNS0yNDQzYzYzZGNhZGMiLCJ1bmlxdWVfbmFtZSI6Im1pY2hhZWxAanVzdGJ1aWxkaXQuY29tIiwiZW1haWwiOiJtaWNoYWVsQGp1c3RidWlsZGl0LmNvbSIsImdpdmVuX25hbWUiOiJNaWNoYWVsIFNtaXRoIiwidGVuYW50X2lkIjoiODMyZTM1MjAtYzM0OS00ZWQ2LWJmMjktNTNhNTUxOTc4MmM2IiwidGVuYW50IjoiY29tbXVuaWZ5IiwibmJmIjoxNzE1MjA5OTc5LCJleHAiOjE3MTU1Njk5NzgsImlhdCI6MTcxNTIwOTk3OCwiaXNzIjoiQUJEM1pXUVg0RFpPNzJGTVlPUjNSUVJJSFhKSEVMQ1ZSVUlSR0xKQlhHRzdGU1NDS0FMQ0JJMk0iLCJhdWQiOiJjb21tdW5pZnkubG9jYWxob3N0In0.kUlIvIUtNEEHyYa6FMShSyy8ZCjTD8dSHrNCSV3_KnM
