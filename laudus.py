import requests
import json
import sys
from collections import OrderedDict
from datetime import datetime

class LaudusAPI_Examples:
    
    # API host
    hostAPI = "https://api.laudus.cl"

    # Object to store API credentials
    credential = {"token": "", "expiration": ""}
    
    # Object to represent the Account entity (Chart of accounts)
    account = {}

    # Object to represent the Customer entity
    customer = {}

    ##########################################################################################

    def getToken(self):
        # Obtains a token by making a request to the API

        vReturn = False
        self.credential = {}

        # Login request schema
        requestLoginSchema = {"userName": "", "password": "", "companyVATId": ""}
        # Assign final values
        requestLoginSchema["userName"] = "api guias"
        requestLoginSchema["password"] = "77VV77VV"
        requestLoginSchema["companyVATId"] = "76278745-8"
        
        # Convert request body to JSON
        requestBodyJson = json.dumps(requestLoginSchema)
        # Build required headers
        requestHeaders = {"Content-type": "application/json", "Accept": "application/json"}
        
        print("-----------------------<< Get Token >>-----------------------")
        
        try:
            request = requests.post(self.hostAPI + "/security/login", data=requestBodyJson, headers=requestHeaders)
            respondStatusCode = request.status_code

            # Check response status code
            if respondStatusCode == requests.codes.ok:
                vReturn = True
                self.credential = json.loads(request.text)
                print("token = " + self.credential["token"])
                print("expiration = " + self.credential["expiration"])
            else:
                vReturn = False
                requestError = json.loads(request.text)
                requestErrorMessage = requestError.get('message', '')
                print('Login error: ' + requestErrorMessage)
        except:
            vReturn = False
            print("Unexpected error:", sys.exc_info()[0])
        
        return vReturn

    ##########################################################################################

    def isValidToken(self):
        # Checks if the stored token is valid; if not, retrieves a new one

        vReturn = True

        if "expiration" in self.credential and len(self.credential["expiration"]) > 0:
            ltNow = datetime.now()
            ltToken = datetime.fromisoformat(self.credential["expiration"])
            ltToken = ltToken.replace(tzinfo=None)
            if ltToken < ltNow:
                return self.getToken()
            else:
                return vReturn
        else:
            return self.getToken()

    ##########################################################################################

    def getCustomer(self, customer_id):

        print("-----------------------<< Get Customer >>-----------------------")

        vReturn = False

        # Validate token or get a new one
        if not self.isValidToken():
            print("Failed to get a valid token")
            return vReturn

        self.customer = {}

        # Build request headers
        requestHeaders = {'Authorization': 'Bearer ' + self.credential["token"], 'Accept': 'application/json'}
        
        try:
            # Make request
            request = requests.get(self.hostAPI + "/sales/customers/" + str(customer_id), headers=requestHeaders)
            respondStatusCode = request.status_code

            if respondStatusCode == requests.codes.ok:
                vReturn = True
                self.customer = json.loads(request.text)
                print(self.customer)
            else:
                vReturn = False
                requestError = json.loads(request.text)
                requestErrorMessage = requestError.get('message', '')
                print('Get customer error: ' + requestErrorMessage)
        except:
            vReturn = False
            print("Unexpected error:", sys.exc_info()[0])
        
        return vReturn        

    ##########################################################################################

    def putCustomer(self, customer_id):

        print("-----------------------<< Save Customer >>-----------------------")
        
        vReturn = False

        # Validate token or get a new one
        if not self.isValidToken():
            print("Failed to get a valid token")
            return vReturn        

        # Build request body JSON
        requestBodyJson = json.dumps(self.customer)

        # Build request headers
        requestHeaders = {
            'Authorization': 'Bearer ' + self.credential["token"],
            'Accept': 'application/json',
            "Content-type": "application/json"
        }
        
        try:
            # Make request
            request = requests.put(self.hostAPI + "/sales/customers/" + str(customer_id), data=requestBodyJson, headers=requestHeaders)
            respondStatusCode = request.status_code

            if respondStatusCode == requests.codes.ok:
                vReturn = True
                self.customer = json.loads(request.text)
                print(self.customer)
            else:
                vReturn = False
                requestError = json.loads(request.text)
                requestErrorMessage = requestError.get('message', '')
                print('Put customer error: ' + requestErrorMessage)
        except:
            vReturn = False
            print("Unexpected error:", sys.exc_info()[0])
        
        return vReturn          

    ##########################################################################################
    def getWaybillsList(self, payload: dict):
        print("-----------------------<< Get Waybills List >>-----------------------")

        vReturn = False
        result = {}

        if not self.isValidToken():
            print("Failed to get a valid token")
            return vReturn

        url = self.hostAPI + "/sales/waybills/list"
        headers = {
            'Authorization': 'Bearer ' + self.credential["token"],
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code == requests.codes.ok:
                result = response.json()
                print(json.dumps(result, indent=2))
                vReturn = True
            else:
                print("Error:", response.status_code, response.text)
        except Exception as e:
            print("Unexpected error:", e)

        return vReturn

if __name__ == '__main__':
    
    example = LaudusAPI_Examples()
    
    if example.getToken():

        # # Optionally call 'python code.py 606' to pass a customer ID (606), otherwise use 18
        # customerId = 18
        # if len(sys.argv) > 1 and int(sys.argv[1]) > 0:
        #     customerId = int(sys.argv[1])

        # if example.getCustomer(customerId):
        #     example.customer["legalName"] = "new legalName"
        #     if example.putCustomer(customerId):
        #         pass

        from datetime import datetime, timedelta

        # Get yesterday's date range
        yesterday = datetime.now() - timedelta(days=1)
        start_date = yesterday.strftime('%Y-%m-%d')
        end_date = start_date  # Same day range

        payload = {
            "options": {
                "offset": 0,
                "limit": 100
            },
            "fields": [
                "salesWaybillId", "issuedDate", "customer.legalName"
            ],
            "filterBy": [
                {
                    "field": "issuedDate",
                    "operator": ">=",
                    "value": start_date + "T00:00:00"
                },
                {
                    "field": "issuedDate",
                    "operator": "<=",
                    "value": start_date + "T23:59:59"
                }
            ],
            "orderBy": [
                {
                    "field": "issuedDate",
                    "direction": "DESC"
                }
            ]
        }

        example.getWaybillsList(payload)