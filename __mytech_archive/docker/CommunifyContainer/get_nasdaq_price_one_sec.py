import nasdaqdatalink
data = nasdaqdatalink.get_table('SHARADAR/SEP', ticker='NVDA', paginate=True)

# the data object is a data frame, convert it to a csv file
data.to_csv('NVDA.csv', index=False)
