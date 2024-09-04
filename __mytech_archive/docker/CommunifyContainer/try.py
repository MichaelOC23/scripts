
var = [
  {
    "Name": "Tickers",
     "Value": [
          {
            "Id": "Cash & Cash Equivalents",
            "ValuePercent": 51.333138674064436
          },
          {
            "Id": "Technology",
            "ValuePercent": 20.839459013760823
          },
          {
            "Id": "Consumer Cyclical",
            "ValuePercent": 6.510178932591872
          },
          {
            "Id": "Healthcare",
            "ValuePercent": 5.754618421555965
          },
          {
            "Id": "Financial Services",
            "ValuePercent": 5.332312129118715
          },
          {
            "Id": "Communication Services",
            "ValuePercent": 2.973912348044332
          },
          {
            "Id": "Industrials",
            "ValuePercent": 2.6416831046331213
          },
          {
            "Id": "Utilities",
            "ValuePercent": 1.3493545453582694
          },
          {
            "Id": "Consumer Defensive",
            "ValuePercent": 1.3463756144509487
          },
          {
            "Id": "Energy",
            "ValuePercent": 0.8847631234860585
          },
          {
            "Id": "Real Estate",
            "ValuePercent": 0.5936133992188347
          },
          {
            "Id": "Basic Materials",
            "ValuePercent": 0.44059069371662546
          }
        ]
  }
]

Tickers = var[0].get('Value')
indus_list = []
for tick in Tickers:
    indus = tick.get('Id', '')  +  "  Portfolio Percent " + tick.get('ValuePercent', '')
    indus_list.append(indus)
    

message_content = "My porfolio contains the following percentage breakdown of industry sectors: " + ", ".join(indus_list) + "  Please provide your commentary"



print(message_content)