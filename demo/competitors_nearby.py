import requests
import json

from secret_config import BASE_URL


# Define the URL and headers
url = BASE_URL + "/competitors_nearby"                   # via deployed endpoint
# url = "http://localhost:5000/competitors_nearby"           # via localhost

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Define the data to be sent in the POST request
data = {
    "arglatitude": -6.272,
    "arglongitude": 106.876
}

# # Bad data type
# data = {
#     "arglatitude": -6,
#     "arglongitude": "0"
# }

# Send the POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Check if the request was successful
if response.status_code == 200:
    # Parse the response JSON
    response_json = response.json()
    
    # Print the response JSON
    print("Response JSON: \n", json.dumps(response_json, indent=4))
    
    # Save the response JSON to a file with pretty formatting
    with open('demo/competitors_nearby.json', 'w') as json_file:
        json.dump(response_json, json_file, indent=4)
else:
    # Parse the response JSON
    response_json = response.json()
    
    # Parse the response JSON
    print("Response JSON: \n", json.dumps(response_json, indent=4))
