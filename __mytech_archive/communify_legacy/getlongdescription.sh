#!/bin/bash

# # The stock ticker symbol
# TICKER="$1"

# # URL of the Yahoo Finance profile page for the ticker
# URL="https://finance.yahoo.com/quote/$TICKER/profile"

# HTML_CONTENT=$(curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36" "$URL")

# echo "$HTML_CONTENT" >>/Users/michasmi/Downloads/stock.txt

# # Extract the description using awk and sed
# DESCRIPTION=$(echo "$HTML_CONTENT" | awk '/<section data-testid="description"/,/<\/section>/' | sed -n '/<p>/,/<\/p>/p' | sed -e 's/<[^>]*>//g')

# echo "Description for $TICKER:"
# echo "$DESCRIPTION"

# Function to fetch and print the company description
fetch_description() {
    local ticker="$1"

    # URL of the Yahoo Finance profile page for the ticker
    local url="https://finance.yahoo.com/quote/${ticker}/profile"

    # Use curl with a User-Agent to fetch the HTML
    local html_content=$(curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36" "$url")

    # Save HTML to a file
    echo "$html_content" >>/Users/michasmi/Downloads/${ticker}.txt

}

# Array of stock ticker symbols
tickers=("AAPL" "GOOGL" "MSFT" "AMZN" "FB")

# Loop through each ticker in the array
for ticker in "${tickers[@]}"; do
    echo "Fetching description for $ticker..."
    fetch_description "$ticker"

    # Pause for a random time between 5 and 15 seconds
    sleep $((RANDOM % 11 + 5))
done
