# Registering CLM and ITS datasets to CKAN

The code in this repo is used to register datasets from California Landscape Metrics (CLM) and California Wildfire & Landscape Resilience Interagency Treatments into the target CKAN.

## Installation Instructions

1. **Install Required Libraries**  

   Use the `requirements.txt` file to install the necessary Python libraries:
   
   `pip install -r requirements.txt`

3. **Configure .env**

   Setup `ckan_url` as your CKAN URL.

   Setup `api_key` as the api-token to access your CKAN.	

   Setup `org_ckan_name` as the organization name as the owner organization for regsitering datasets.
