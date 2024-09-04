import os
import json
import requests

class WealthTechsAPI:
    def __init__(self, base_url=None, token=None, folder_path=None):
        if token is None:
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VySW5mbyI6IntcIklkXCI6MTAxNixcIklkZW50aXR5SWRcIjpcIjkzYjU2YTkxLWViOTUtNGVhNS1iZmIwLWZkMjdhYmI3MmRiMVwiLFwiVXNlck5hbWVcIjpcIjBfTUlDSEFFTF9TTUlUSFwiLFwiRW1haWxcIjpcIm1pY2hhZWxAanVzdGJ1aWxkaXQuY29tXCIsXCJGaXJzdE5hbWVcIjpcIk1pY2hhZWxcIixcIkxhc3ROYW1lXCI6XCJTbWl0aFwifSIsIm5iZiI6MTcxOTg2MjIxNywiZXhwIjoxNzIyNDg0ODAwLCJpc3MiOiJXZWFsdGhUZWNocyIsImF1ZCI6IkFQSVVzZXJzIn0.ul25WR-rWMgfGUaksqcLu2xm9_TMZnZosL-P-23B9do"
        
        if base_url is None:
            self.base_url="https://api.wealthtechs.com/v2/odata"
        else:
            self.base_url = base_url

        
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        if folder_path is None:
            self.folder_path = "/Users/michasmi/code/data/WealthTechsAPI"
        else:
            self.folder_path = folder_path
            
        os.makedirs(self.folder_path, exist_ok=True)

    def save_results_to_file(self, data, endpoint_name):
        file_path = f"{self.folder_path}/WealthTechs_EndPoint_{endpoint_name}.json"
        with open(file_path, 'w') as f:
            readable_json = json.dumps(data, indent=4)
            f.write(readable_json)

    def get_metadata(self):
        url = f'{self.base_url}/$metadata'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_accounts(self, top=None, select=None, filter=None, expand=None, orderby=None):
        url = f'{self.base_url}/Accounts'
        params = {}
        if top:
            params['$top'] = top
        if select:
            params['$select'] = select
        if filter:
            params['$filter'] = filter
        if expand:
            params['$expand'] = expand
        if orderby:
            params['$orderby'] = orderby

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    # Add similar methods for other endpoints
    def get_currencies(self, top=None):
        url = f'{self.base_url}/Currencies'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_custodians(self, top=None):
        url = f'{self.base_url}/Custodians'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_customers(self, top=None):
        url = f'{self.base_url}/Customers'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_fx_rates(self, top=None):
        url = f'{self.base_url}/FxRates'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_interface_statuses(self, top=None):
        url = f'{self.base_url}/InterfaceStatuses'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_interface_status_types(self, top=None):
        url = f'{self.base_url}/InterfaceStatusTypes'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_major_asset_classes(self, top=None):
        url = f'{self.base_url}/MajorAssetClasses'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_positions(self, top=None):
        url = f'{self.base_url}/Positions'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_prices(self, top=None):
        url = f'{self.base_url}/Prices'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_primary_types(self, top=None):
        url = f'{self.base_url}/PrimaryTypes'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_sectors(self, top=None):
        url = f'{self.base_url}/Sectors'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_securities(self, top=None):
        url = f'{self.base_url}/Securities'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_security_types(self, top=None):
        url = f'{self.base_url}/SecurityTypes'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_tax_lots(self, top=None):
        url = f'{self.base_url}/TaxLots'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_transaction_codes(self, top=None):
        url = f'{self.base_url}/TransactionCodes'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_transactions(self, top=None):
        url = f'{self.base_url}/Transactions'
        params = {}
        if top:
            params['$top'] = top

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_all_data(self):
        endpoints = {
            'metadata': self.get_metadata,
            'accounts': self.get_accounts,
            'currencies': self.get_currencies,
            'custodians': self.get_custodians,
            'customers': self.get_customers,
            'fx_rates': self.get_fx_rates,
            'interface_statuses': self.get_interface_statuses,
            'interface_status_types': self.get_interface_status_types,
            'major_asset_classes': self.get_major_asset_classes,
            'positions': self.get_positions,
            'prices': self.get_prices,
            'primary_types': self.get_primary_types,
            'sectors': self.get_sectors,
            'securities': self.get_securities,
            'security_types': self.get_security_types,
            'tax_lots': self.get_tax_lots,
            'transaction_codes': self.get_transaction_codes,
            'transactions': self.get_transactions
        }

        for key in endpoints.keys():
            endpoint_name = key
            func = endpoints[key]
            
            print(f"Fetching data from {endpoint_name}...")
            try:
                data = func() if endpoint_name != 'metadata' else func()
            except Exception as e:
                print(f"Failed to retrieve data from {endpoint_name}: {e}")
                continue
                  
                    
            self.save_results_to_file(data, endpoint_name)
            print(f"Data from {endpoint_name} saved successfully.")
        

# Example usage:
api = WealthTechsAPI()
api.get_all_data()