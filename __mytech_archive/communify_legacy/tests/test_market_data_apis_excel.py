#################################
#?## PRICING API EVALUATIONS ####
#################################

#################################
#?##### PYTHON ENV. SETUP #######
#################################

#! Create a virtual environment
# python -m venv pricing_venv

#! Activate the virtual environment
# source pricing_venv/bin/activate

#! From the activated virtual environment, install required packages

#################################
#?###### NASDAQ DATA LINK #######
#################################


# Websites:  https://pypi.org/project/nasdaq-data-link/
#            https://docs.data.nasdaq.com/docs/python

#API Key:   6X82a45M1zJPu2ci4TJP for user michaelasmith@caa.columbia.edu

#################################
#?#######  Yahoo Finance  #######
#################################

# Docuemntation: https://github.com/ranaroussi/yfinance

#################################
#?#######  FINHUB  #######
#################################
#API Key = "clbs0qpr01qp535t44mgclbs0qpr01qp535t44n0"

# Use this for the price quote
# Quote
#   result = finnhub_client.quote('AAPL')
#   export_api_response_to_excel(result, excel_file_full_path, 'Quote')

# Website       https://finnhub.io/



# pip install pandas openpyxl # Standard packages
# pip install yfinance nasdaq-data-link quandl finnhub-python # Third-party packages
# Imports for pacakges
import os
from datetime import date, datetime, timedelta
import pandas as pd

#YAHOO
import yfinance as yf

#NASDAQ
import nasdaqdatalink 
import quandl

# FINNHUB
import finnhub
import json
from openpyxl import load_workbook  # This is the missing import


# Global variables
# Get dates for one year 
current_date = datetime.now()
# Set end_date to 12/31/2022
end_date = datetime(2022, 12, 31)
start_date = datetime(2022, 1, 1)


# Establish string versions for the dates
current_date_str = current_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')
start_date_str = start_date.strftime('%Y-%m-%d')

# This is the list of stocks used in the portfolio for the user in the Communify Finance Designs.
#stock_list = {'IVV', 'AAPL', 'NVDA', 'MSFT', 'ITOT', 'IEFA', 'RMBS', 'QUAL', 'ESGU', 'DAL', 'GOOGL', 'MTSI', 'AMZN', 'HSCZ', 'TMUS', 'IXN', 'AER', 'DVN', 'KBR', 'USMV', 'LLY', 'IGT', 'VST', 'ACHC', 'CRTO', 'GOOG', 'NOW', 'JPM', 'UNH', 'V', 'CAR', 'MOH', 'VECO', 'CLF', 'ETN', 'ESGE', 'FTI', 'LUV', 'PG', 'VRNS', 'DUK', 'AVY', 'SIZE', 'CLH', 'KD', 'THS', 'KAR', 'PNC', 'BKU', 'APO', 'ENTG', 'WIX', 'HAE', 'ORA', 'TPX', 'CIEN', 'LNG', 'MAR', 'IEMG', 'UBER', 'CCK', 'PLD', 'MCK', 'TSLA', 'CB', 'SSYS', 'ITRI', 'TJX', 'OSIS', 'ORCL', 'MDLZ', 'BANC', 'TDG', 'OIS', 'JBLU', 'VRTX', 'WCN', 'ABBV', 'CI', 'MET', 'MDT', 'CAL', 'APH', 'PXD', 'HBAN', 'LGF', 'T', 'KO', 'MCD', 'XPO', 'CRNC', 'ULTA', 'SPGI', 'ADI', 'VREX', 'MSI', 'BKNG', 'WFC', 'CRL', 'TT', 'TW', 'BOX', 'ATRC', 'DTM', 'TEX', 'TMO', 'GXO', 'HD', 'XOM', 'DXCM', 'PDCO', 'STZ', 'BMY', 'SMAR', 'PKG', 'AME', 'LIN', 'EQH', 'TOL', 'REGN', 'LVS', 'ELV', 'RLJ', 'PLCE', 'CNNE', 'BSX', 'CHS', 'NKE', 'SHW', 'BLK', 'VMI', 'HON', 'ADEA', 'JNJ', 'BA', 'PTEN', 'WRBY', 'AON', 'FCX', 'ZIMV', 'CMA', 'CSCO', 'ODP', 'JCI', 'EPAC', 'VIAV', 'CGNT', 'TCBI', 'COHR', 'UIS', 'TKO', 'DLTR', 'DRQ', 'REZI', 'FI', 'ICE', 'VRNT', 'CNDT', 'PSX', 'ADSK', 'IART', 'BX', 'CNP', 'INTU', 'ECL', 'OSPN', 'ZTS', 'STWD', 'COO', 'ACA', 'RDWR', 'FCPT', 'BFH', 'ALL', 'LAB', 'LW', 'TRU', 'UA', 'COP', 'TRGP', 'BYON', 'MRCY', 'GS', 'NVT', 'INVZ', 'CEVA', 'BW', 'VSAT', 'BMRN', 'FTCH', 'CWBHF', 'CEG', 'EXC', 'SMTC', 'CVSI', 'ESGU', 'IVV', 'IVW', 'EFG', 'EFV', 'EMXC', 'IEMG', 'GOVT', 'HYDB', 'ICVT', 'IUSB', 'TLT', 'OEF', 'QUAL', 'USMV', 'IFRA', 'IXC', 'IYW', 'LQD', 'MBB', 'TFLO', 'TIP', 'EMB'}

# Shorter stock list for testing
stock_list = {'AAPL', 'NVDA', 'MSFT', 'ITOT', 'IEFA', 'RMBS', 'IVV'} 

# File name for saving the data
history_file_name = f'{start_date_str}_{end_date_str}'
current_date_file_name = f'{current_date_str}'

def main():

    
    #! Execute the function for Yahoo Finance
    yahoo_main()

    #! Execute the function for NASDAQ
    nasdaq_main()

    #! Execute the function for FINNHUB
    finnhub_main()




###############################################
#!##### YAHOOFINANCE PRICE / PRICE HISTORY #####
###############################################


def yahoo_main():
   
    # Iterate through each stock in the list
    for stock_name in stock_list:
        # Download the stock data and store it in the dictionary
        try:
            # Download stock data history
            current_price_data = yf.download(stock_name, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
            # Add a new column with the stock name
            current_price_data['Stock'] = stock_name



            # Download current price
            history_data = yf.download(stock_name, start=current_date.strftime('%Y-%m-%d'))
            # Add a new column with the stock name
            history_data['Stock'] = stock_name

            # Save to CSV file
            append_to_text_file(current_price_data, current_date_file_name, "YAHOO_EOD", "csv")
            append_to_text_file(history_data, history_file_name, "YAHOO_EOD", "csv")
            
            print(f'Current and historical data successfully saved for {stock_name}')
            
            
            # Create a Ticker object for the company
            stock = yf.Ticker(stock_name)

            # Access information about the company
            info = stock.info

            # Get the company's description
            description = info.get('longBusinessSummary')
            
            
            
            
        except Exception as e:
            print(f'Error downloading {stock_name} from Yahoo Finance: {e}')
    return history_data




###############################################
#!############ NASDAQ FREE API #############
###############################################
def nasdaq_main():

    #set an environment variable for the API key
    quandl.ApiConfig.api_key = "6X82a45M1zJPu2ci4TJP"

    #End of Day prices for ticker list
    data = nasdaqdatalink.get_table('WIKI/PRICES', qopts = { 'columns': ['ticker', 'date', 'close'] }, ticker = stock_list, date = { 'gte': current_date_str, 'lte': current_date_str })
    append_to_text_file(data, current_date_file_name, "NASDAQ_EOD", "csv")
    

    #Closing price history for ticker list
    data = nasdaqdatalink.get_table('WIKI/PRICES', qopts = { 'columns': ['ticker', 'date', 'close'] }, ticker = stock_list, date = { 'gte': start_date_str, 'lte': end_date_str })
    append_to_text_file(data, history_file_name, "NASDAQ_HISTORY", "csv")
        


###############################################
#!############ FINHUB.COM FREE API ############
###############################################


def export_api_response_to_excel(res, excel_file_full_path, sheet_name):
   # Check if res is a single dictionary
    if isinstance(res, dict):
        with open(f'{sheet_name}.json', 'w') as file:
        # Dump the dictionary to the file in JSON format.
            json.dump(res, file, indent=4)

  
    else:
    # Convert the API call result to a Pandas DataFrame.
        df = pd.DataFrame(res)

        # Check if the Excel file already exists.
        if not os.path.isfile(excel_file_full_path):
            # If the file does not exist, create a new Excel writer and write the DataFrame.
            with pd.ExcelWriter(excel_file_full_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # If the file exists, append to it (this will load the existing workbook).
            with pd.ExcelWriter(excel_file_full_path, engine='openpyxl', mode='a') as writer:
                # Write the dataframe data to a new sheet.
                # If the sheet already exists, ExcelWriter will replace it.
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            



    ##########################################
    #!## FINNHUB API - OTHER FREE API CALLS ###
    ##########################################
def finnhub_main():
    
    excel_file_full_path = f'finhub-api-test{current_date}.xlsx'

    # Setup client
    finnhub_client = finnhub.Client(api_key="clbs0qpr01qp535t44mgclbs0qpr01qp535t44n0")

    # Stock candles
    res = finnhub_client.stock_candles('AAPL', 'D', 1590988249, 1591852249)
    export_api_response_to_excel(res, excel_file_full_path, 'Stock candles')   

    # Basic financials
    result = finnhub_client.company_basic_financials('AAPL', 'all')
    export_api_response_to_excel(result, excel_file_full_path, 'Basic financials')

    # Earnings surprises
    result = finnhub_client.company_earnings('TSLA', limit=5)
    export_api_response_to_excel(result, excel_file_full_path, 'Earnings surprises')

    # Company News
    # Need to use _from instead of from to avoid conflict
    result = finnhub_client.company_news('AAPL', _from="2023-06-01", to="2024-06-10")
    export_api_response_to_excel(result, excel_file_full_path, 'Company News')

    # Company Peers
    result = finnhub_client.company_peers('AAPL')
    export_api_response_to_excel(result, excel_file_full_path, 'Company Peers')

    # Company Profile 2
    result = finnhub_client.company_profile2(symbol='AAPL')
    export_api_response_to_excel(result, excel_file_full_path, 'Company Profile 2')

    # Crypto symbols
    result = finnhub_client.crypto_symbols('BINANCE')
    export_api_response_to_excel(result, excel_file_full_path, 'Crypto symbols')

    # Filings
    result = finnhub_client.filings(symbol='AAPL', _from="2022-01-01", to="2023-06-11")
    export_api_response_to_excel(result, excel_file_full_path, 'Filings')

    # Financials as reported
    result = finnhub_client.financials_reported(symbol='AAPL', freq='annual')
    export_api_response_to_excel(result, excel_file_full_path, 'Financials as reported')

    # Forex exchanges
    result = finnhub_client.forex_exchanges()
    export_api_response_to_excel(result, excel_file_full_path, 'Forex exchanges')  

    # Forex symbols
    result = finnhub_client.forex_symbols('OANDA')
    export_api_response_to_excel(result, excel_file_full_path, 'Forex symbols')

    # General news
    result = finnhub_client.general_news('forex', min_id=0)
    export_api_response_to_excel(result, excel_file_full_path, 'General news')

    # IPO calendar
    result = finnhub_client.ipo_calendar(_from="2023-05-01", to="2024-06-01")
    export_api_response_to_excel(result, excel_file_full_path, 'IPO calendar')

    # Quote
    result = finnhub_client.quote('AAPL')
    export_api_response_to_excel(result, excel_file_full_path, 'Quote')

    # Recommendation trends
    result = finnhub_client.recommendation_trends('AAPL')
    export_api_response_to_excel(result, excel_file_full_path, 'Recommendation trends')

    # Stock symbols
    result = finnhub_client.stock_symbols('US')[0:500]
    export_api_response_to_excel(result, excel_file_full_path, 'Stock symbols')

    # Earnings Calendar
    result = finnhub_client.earnings_calendar(_from="2023-06-10", to="2024-06-30", symbol="", international=False)
    export_api_response_to_excel(result, excel_file_full_path, 'Earnings Calendar')

    # Covid-19
    result = finnhub_client.covid19()
    export_api_response_to_excel(result, excel_file_full_path, 'Covid-19')

    # Technical Indicator
    result = finnhub_client.technical_indicator(symbol="AAPL", resolution='D', _from=1583098857, to=1584308457, indicator='rsi', indicator_fields={"timeperiod": 3})
    export_api_response_to_excel(result, excel_file_full_path, 'Technical Indicator')

    # Crypto Candles
    result = finnhub_client.crypto_candles('BINANCE:BTCUSDT', 'D', 1590988249, 1591852249)
    export_api_response_to_excel(result, excel_file_full_path, 'Crypto Candles')

    # FDA Calendar
    result = finnhub_client.fda_calendar()
    export_api_response_to_excel(result, excel_file_full_path, 'FDA Calendar')

    # Symbol lookup
    result = finnhub_client.symbol_lookup('apple')
    export_api_response_to_excel(result, excel_file_full_path, 'Symbol lookup')

    # Insider transactions
    result = finnhub_client.stock_insider_transactions('AAPL', '2021-01-01', '2023-11-01')
    export_api_response_to_excel(result, excel_file_full_path, 'Insider transactions')

    # Visa application
    result = finnhub_client.stock_visa_application("AAPL", "2022-01-01", "2023-06-15")
    export_api_response_to_excel(result, excel_file_full_path, 'Visa application')

    # Insider sentiment
    result = finnhub_client.stock_insider_sentiment('AAPL', '2022-01-01', '2023-11-01')
    export_api_response_to_excel(result, excel_file_full_path, 'Insider sentiment')
    
    # Lobbying
    result = finnhub_client.stock_lobbying("AAPL", "2022-01-01", "2023-06-15")
    export_api_response_to_excel(result, excel_file_full_path, 'Lobbying')
    #
    #  USA Spending
    result = finnhub_client.stock_usa_spending("LMT", "2022-01-01", "2023-06-15")
    export_api_response_to_excel(result, excel_file_full_path, 'USA Spending')

    ## Market Holiday
    result = finnhub_client.market_holiday(exchange='US')
    export_api_response_to_excel(result, excel_file_full_path, 'Market Holiday')

    ## Market Status
    result = finnhub_client.market_status(exchange='US')
    export_api_response_to_excel(result, excel_file_full_path, 'Market Status')






def append_to_text_file(data, file_name, prefix = '', suffix = ''):  
    #Save to text file
    if suffix == '': suffix = 'txt'

    with open(f'{prefix}_{file_name}.{suffix}', 'a') as f:
        if suffix == 'csv':
            data.to_csv(f, header=f.tell()==0)
        else:
            f.write(data)
if __name__ == '__main__':
    print ('hello')
    yahoo_main()


#main()

###################################################
#!############ OTHER FREE DATA: NASDAQ  ############
###################################################

# IMF Cross Country Macroeconomic Statistics
# Open global data of key economic indicators from the World Economic Outlook database sourced directly from the IMF website.

# Commodity Futures Trading Commission Reports
# Weekly Commitment of Traders and Concentration Ratios sourced directly from the official CFTC website. Reports for futures positions as well as futures plus options positions in and legacy formats.

# Organization of the Petroleum Exporting Countries
# A comprehensive collection of crude oil prices declared by oil-producing countries over time.

# JODI Oil World Database
# Extensive global data on energy products and flows from 120+ countries, encompassing over 90% of the world's supply and demand.

# Bitfinex Crypto Coins Exchange Rate
# Essential cryptocurrency exchange rates featuring high, low, mid, last, bid, ask, and volume metrics as presented by the Bitfinex website.

# Bitcoin Data Insights
# Daily, one day-delayed data showing essential insights of various Bitcoin metrics, as presented by the Blockchain website.

# Metal Stocks Breakdown Report
# Daily, two day-delayed reports showing opening stocks, open and cancelled tonnage, delivered in and out tonnage by metal, location and country as presented by the London Metal Exchange

# Zillow Real Estate Data
# Zillow is the leading real estate and rental marketplace dedicated to empowering consumers with data, inspiration and knowledge around the place they call home, and connecting them with the best local professionals who can help.

# Federal Reserve Economic Data
# Growth, employment, inflation, labor, manufacturing and other US economic statistics from the research department of the Federal Reserve Bank of St. Louis.

# London Bullion Market Association
# An international trade association in the London gold and silver market, consisting of central banks, private investors, producers, refiners, and other agents.

# U.S. Energy Information Administration Data
# US national and state data on production, consumption and other indicators on all major energy products, such as electricity, coal, natural gas and petroleum.

# Energy Production and Consumption
# BP is a large energy producer and distributor. It provides data on energy production and consumption in individual countries and larger subregions.

# Federal Reserve Economic Data
# Growth, employment, inflation, labor, manufacturing and other US economic statistics from the research department of the Federal Reserve Bank of St. Louis.

# London Bullion Market Association
# An international trade association in the London gold and silver market, consisting of central banks, private investors, producers, refiners, and other agents.

# U.S. Energy Information Administration Data
# US national and state data on production, consumption and other indicators on all major energy products, such as electricity, coal, natural gas and petroleum.

# Energy Production and Consumption
# BP is a large energy producer and distributor. It provides data on energy production and consumption in individual countries and larger subregions.

# Consumer Sentiment
# The University of Michigan’s consumer survey - data points for the most recent 6 months are unofficial; they are sourced from articles in the Wall Street Journal.

# World Agricultural Supply and Demand Estimates
# The WASDE report comes from the World Agricultural Outlook Board (WAOB). The report is released monthly, and provides annual forecasts for U.S. and various world regions pertaining to wheat, rice, coarse grains, oilseeds, and cotton. The report also covers U.S. production of sugar, meat, poultry, eggs, and milk.

# World Bank Data
# World Bank provides data from hundreds of countries and regions around the world, from multiple categories such as finance, economy, energy, education, health, poverty, agriculture, employment, population, land use, foreign aid, climate change, government expenditures, literacy, mortality, and patents.

# Hong Kong Exchange
# Hong Kong Exchange stock prices, historical divided futures, etc. updated daily.

# S&P 500 Ratios
# No description for this database yet.

# US Federal Reserve Data Releases
# Official US figures on money supply, interest rates, mortgages, government finances, bank assets and debt, exchange rates, industrial production.

# Financial Industry Regulatory Authority
# Financial Industry Regulatory Authority provides short interest data on securities firms and exchange markets.

# Central Bank of Brazil Statistical Database
# Brazilian macroeconomic data, covering public finances, national accounts, payment systems, inflation, exchange rates, trade, and international reserves.

# Bank of England Official Statistics
# Current and historical exchange rates, interest rates on secured loans and time deposits, Euro-commercial paper rates, and yields on government securities.

# US Treasury
# The U.S. Treasury ensures the nation's financial security, manages the nation's debt, collects tax revenues, and issues currency, provides data on yield rates.

# Corporate Bond Yield Rates
# Merrill Lynch, a major U.S. bank, publishes data on yield rates for corporate bonds in different regions.

# The Economist - Big Mac Index
# The Big Mac index was invented by The Economist in 1986 as a lighthearted guide to whether currencies are at their “correct” level. It is based on the theory of purchasing-power parity (PPP).

# Organisation for Economic Co-operation and Development
# International organization of developed countries that promotes economic welfare. Collects data from members and others to make policy recommendations.

# BATS U.S. Stock Exchanges
# Bats is an equities market operator in the U.S., operating four equities exchanges — BZX Exchange, BYX Exchange, EDGA Exchange, and EDGX Exchange

# Bombay Stock Exchange
# End of day prices, indices, and additional information for companies trading on the Bombay Stock Exchange in India.

# Inflation Rates
# Inflation Rates and the Consumer Price Index CPI for Argentina, Australia, Canada, Germany, Euro area, France, Italy, Japan, New Zealand and more.
