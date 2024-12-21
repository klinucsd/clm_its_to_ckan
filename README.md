# Registering CLM and ITS Datasets to CKAN

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


## Issues Handled When Registering Datasets

### Inconsistent Dataset Names
Some datasets had names that were not appropriate for CKAN. Examples include:

     “>40” Dbh
     
     “30” - 40” Dbh

Additionally, several datasets used vague region-based names such as "Sierra Nevada", "Northern California", or "Central CA". While these may suffice in category hierarchies, they are unsuitable as CKAN dataset names.

To improve clarity, the script systematically prefixed these dataset names with their category. For example:

     Northern CA - Large Tree Density - >40” Dbh

     Northern CA - Large Tree Density - 30” - 40” Dbh

     Hispanic and Latino Population Concentration - Central CA

     Asian Population Concentration - Sierra Nevada


### Keyword Tagging

Three keywords were generated for each dataset using an LLM and were manually reviewed as CKAN tags.

### Spatial Metadata

The script utilized the bounding box and spatial attributes of each dataset.

### Category Inclusion

The category of each dataset in CLM was added to its metadata.

### Adding Resources

The script included relevant WMS, WCS, or WFS endpoints for each CLM dataset as resources in CKAN.