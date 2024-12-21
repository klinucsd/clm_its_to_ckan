
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_clm_and_its_package_ids():
    ckan_url = os.getenv('ckan_url')
    api_key = os.getenv('api_key')
    headers = {
        'X-CKAN-API-Key': api_key,
        'Content-Type': 'application/json'
    }

    api_url = f"{ckan_url}/api/3/action/package_list"
    response = requests.post(api_url, headers=headers)

    # Check the response
    if response.status_code == 200:
        package_ids = response.json()['result']
        return [ package_id for package_id in package_ids if package_id.startswith('clm-') or package_id.startswith('its-') ]
    else:
        raise BaseException(f"Error creating dataset: {response.text}")    


def delete_clm_and_its_packages():

    ckan_url = os.getenv('ckan_url')
    api_key = os.getenv('api_key')
    headers = {
        'X-CKAN-API-Key': api_key,
	'Content-Type': 'application/json'
    }

    api_url = f"{ckan_url}/api/3/action/package_delete"
    
    package_ids = get_clm_and_its_package_ids()
    for package_id in package_ids:
        dataset_dict = {
            "id": package_id
        }
        response = requests.post(api_url, data=json.dumps(dataset_dict), headers=headers)
        if response.status_code == 200:
            print("deleted", package_id)
       
    
delete_clm_and_its_packages()
