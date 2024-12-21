# Registering CLM and ITS datasets to CKAN

The code in this repo is used to register datasets from California Landscape Metrics (CLM) and California Wildfire & Landscape Resilience Interagency Treatments into the target CKAN.

## Installation Instructions

1. **Install Required Libraries**  

   Use the `requirements.txt` file to install the necessary Python libraries:
   
   `pip install -r requirements.txt`

3. **Configure .env**

   Update `ckan_url` to your CKAN URL.

   Update `api_key` to the api-token to access your CKAN.	

   Update `org_ckan_name` as the organization name as the owner organization for regsitering datasets. The `org_ckan_name` must exist in the target CKAN.

   Keep `rrk_api_url` unchanged.

## Register CLM and ITS datasets to CKAN

   Run the following command to register all CLM and ITS datasets to CKAN:

   	 `python save_clm_and_its_to_ckan.py`

## Delete Registered CLAM and ITS datasets from CKAN

   Run the following command to remove all CLM and ITS datasets from CKAN:

   	 `python delete_clm_and_its_from_ckan.py`