
"""
#
# Register CLM datasets to CKAN under the organization
# California Wildfire & Forest Resilience Task Force
#
"""

import json
import os
import re
import unicodedata
import xml.etree.ElementTree as ET
import unicodedata

import requests
from dotenv import load_dotenv
from pyproj import Transformer

from dataset_hierarchy import get_category, get_clm_hierarchy
from wms_extent import get_extent_for_wms_layer


load_dotenv()


def fix_text(input_text):
    if input_text is None:
        return ""
    
    # Replace common problematic characters
    replacements = {
        '\u201d': '"',  # right double quote
        '\u201c': '"',  # left double quote
        '\u2018': "'",  # left single quote
        '\u2019': "'",  # right single quote
        '\u00e2\u0080\u0099': "'",  # corrupted apostrophe
        '\u00e2\u0080\u009c': '"',  # corrupted left double quote
        '\u00e2\u0080\u009d': '"',  # corrupted right double quote
        'â': "'",  # another form of corrupted apostrophe
    }
    
    # First normalize the Unicode text
    normalized = unicodedata.normalize('NFKC', input_text)
    
    # Apply all replacements
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    
    return normalized


def convert_coordinates_to_lat_lon(lower_coords, upper_coords):
    """
    Convert bounding box coordinates from EPSG:3310 to latitude and longitude (EPSG:4326).

    Parameters:
    - lower_coords: list of float, lower corner coordinates [x_min, y_min].
    - upper_coords: list of float, upper corner coordinates [x_max, y_max].

    Returns:
    - lat_lon_bbox: tuple, ((lat_min, lon_min), (lat_max, lon_max)).
    """

    transformer = Transformer.from_crs("EPSG:3310", "EPSG:4326", always_xy=True)
    lon_min, lat_min = transformer.transform(lower_coords[0], lower_coords[1])
    lon_max, lat_max = transformer.transform(upper_coords[0], upper_coords[1])
    return ((lat_min, lon_min), (lat_max, lon_max))


def get_wcs_extent(wcs_url, coverage_id):
    """
    Get the extent (bounding box) of a WCS coverage.

    Parameters:
    - wcs_url: str, the URL of the WCS service.
    - coverage_id: str, the ID of the coverage.

    Returns:
    - bbox: tuple, (lower_corner, upper_corner) of the bounding box.
    """
    # Construct the DescribeCoverage request URL
    describe_coverage_url = f"{wcs_url}?service=WCS&version=2.0.1&request=DescribeCoverage&coverageId={coverage_id}"

    # Make the request
    response = requests.get(describe_coverage_url)

    # Check if the request was successful
    if response.status_code != 200:
        # print(f"Failed to retrieve coverage details: {response.status_code} {coverage_id}")
        return None
    
    # Parse the XML response
    root = ET.fromstring(response.content)

    # Define namespaces for XML parsing
    namespaces = {
        'gml': 'http://www.opengis.net/gml/3.2',
        'wcs': 'http://www.opengis.net/wcs/2.0'
    }

    # Find the Envelope tag
    envelope = root.find('.//gml:Envelope', namespaces)

    if envelope is not None:
        # Extract EPSG code from srsName attribute and extract only the numeric part
        srs_name = envelope.attrib.get('srsName', None)
        epsg_code = None
        if srs_name:
            match = re.search(r'EPSG/0/(\d+)', srs_name)
            if match:
                epsg_code = match.group(1)  # Extract only the EPSG number

        # Extract the lowerCorner and upperCorner values
        lower_corner = envelope.find('gml:lowerCorner', namespaces).text
        upper_corner = envelope.find('gml:upperCorner', namespaces).text

        # Convert to numeric values for further use
        lower_coords = list(map(float, lower_corner.split()))
        upper_coords = list(map(float, upper_corner.split()))

        return (lower_coords, upper_coords, epsg_code)

    print("Bounding Box not found.")
    return None


def fix_title(text):
    # First apply the standard title case
    title = text.title()
    
    # List of words that should be in specific case
    special_cases = {
        'Ca': 'CA',
        'Usa': 'USA',
        'Or': 'or',
        'Of': 'of',
        'The': 'the',
        'In': 'in',
        'On': 'on',
        'At': 'at',
        'To': 'to',
        'For': 'for',
        'And': 'and',
        'Sdi': 'SDI',
        'Cso': 'CSO'
        # Add more special cases as needed
    }
    
    # Split the title into words
    words = title.split()
    
    # Fix each word if it's in our special cases
    words = [special_cases.get(word, word) for word in words]
    
    # Always capitalize the first word
    if words:
        words[0] = words[0].title()
    
    # Join the words back together
    return ' '.join(words).replace('Sdi:', 'SDI:').replace('Fsh:', 'FSH').replace('(Cso)', '(CSO)')


def slugify(title):
    # Normalize unicode characters
    name = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')

    # Convert to lowercase and replace spaces with hyphens
    name = re.sub(r'[^\w\s-]', '', name.lower())
    name = re.sub(r'[-\s]+', '-', name).strip('-')

    # Ensure it starts with a letter
    name = re.sub(r'^[^a-zA-Z]+', '', name)

    # Truncate to 100 characters
    return name[:96]


def transform_to_ckan_package(rrk_dataset, org, category, label, dataset_keyword_map, dataset_download_urls):

    title = fix_text(rrk_dataset['name'])

    if label in [
            "Functional Species Richness",
            "Annual biomass data (2001-2021)",
            "Sierra Nevada Cost of Potential Treatments",
            "Northern CA Cost of Potential Treatments",
            "Ignition Cause -1992-2020",
            "Fire Return Interval Departure (FRID)",
            "Sierra Nevada - Large Tree Density",
            "Northern CA - Large Tree Density",
            "Density - Snags",
            "SDI: Stand Density Index",
            "SDI: Proportion of Max",
            "Distribution of Above Ground Live Biomass in Vegetation Type Categories",
            "Climate refugia (MIROC MODEL - hotter and drier)",
            "American Indian Or Alaska Native Race Alone And Multi-Race Population Concentration",
            "Hispanic and Latino Population Concentration",
            "Black and African American Population Concentration",
            "Hispanic and Latino Population Concentration",
            "Asian Population Concentration",
            "Multi-race, Except Part-American Indian Pop. Concentration",
            "Low Income Population Concentration",
            "Hispanic and or Black, Indigenous Or People of Color (HSPBIPOC) Population Concentration",
    ]:
        title = f"{label} - {title}"
    
    rrk_package_dict = {
        'name': 'clm-' + slugify(title),
        'title': fix_title(title.title()),
        'owner_org': org,
        'type': 'dataset',
        'extras': [],
        'resources': [],
        'tags':[],
    }

    extras = rrk_package_dict['extras']
    """
    extras.append({
        "key": "Format",
        "value": rrk_dataset['file_type']
    })
    """
    extras.append({
        "key": "File Name",
        "value": rrk_dataset['file_path']
    })
    extras.append({
        "key": "Category",
        "value": category
    })
    extras.append({
      "key": "Collection Name",
      "value": "California Landscape Metrics"
    })
    
    for metadata in rrk_dataset['dataset_metadata']:
        if metadata['name'] == 'creation_method':
            extras.append({
                "key": "Creation Method",
                "value": fix_text(metadata['text_value'].rstrip("\r\n*")).replace('\u00c2\u00b7', ' - ')
            })
        elif metadata['name'] == 'data_vintage':
            extras.append({
                "key": "Data Vintage",
                "value": metadata['text_value'].rstrip("\r\n*")
            })
        elif metadata['name'] == 'metric_definition_and_relevance':
            rrk_package_dict['notes'] = fix_text(metadata['text_value'].rstrip("\r\n*")).replace('\u00c2\u00b7', ' - ')
            extras.append({
                "key": "Metric Definition and Relevance",
                "value": fix_text(metadata['text_value'].rstrip("\r\n*")).replace('\u00c2\u00b7', ' - ')
            })
        elif metadata['name'] == 'data_units':
            extras.append({
                "key": "Data Units",
                "value": metadata['text_value'].rstrip("\r\n*")
            })
        elif metadata['name'] == 'tier':
            extras.append({
                "key": "Tier",
                "value": metadata['text_value'].rstrip("\r\n*")
            })
        elif metadata['name'] == 'min_value':
            extras.append({
                "key": "Minimum Value",
                "value": metadata['float_value']
            })
        elif metadata['name'] == 'max_value':
            extras.append({
                "key": "Maximum Value",
                "value": metadata['float_value']
            })
        elif metadata['name'] == 'data_resolution':
            extras.append({
                "key": "Resolution",
                "value": metadata['text_value']
            })

    # setup tags
    keywords = dataset_keyword_map['clm-' + slugify(title)]
    tags = rrk_package_dict['tags']
    for keyword in keywords:
        tags.append({'name': keyword})
            
    gis_service = rrk_dataset['gis_services'][0]

    # fix an error
    if gis_service['layer_name'] == 'rrk:predlightningigncause_19922015_202406_t3_v5':
        gis_service['layer_name'] = 'wldfireigncauselightning_19922020_202312_t1_v5'
    
    lat_lon_bbox = get_extent_for_wms_layer(gis_service['layer_name'])
    wcs_extent = None
    if lat_lon_bbox:
        spatial_geojson = {
            "type": "Polygon",
            "coordinates": [[
                [lat_lon_bbox[0][1], lat_lon_bbox[0][0]],  # Lower-left corner (lon_min, lat_min)
                [lat_lon_bbox[1][1], lat_lon_bbox[0][0]],  # Lower-right corner (lon_max, lat_min)
                [lat_lon_bbox[1][1], lat_lon_bbox[1][0]],  # Upper-right corner (lon_max, lat_max)
                [lat_lon_bbox[0][1], lat_lon_bbox[1][0]],  # Upper-left corner (lon_min, lat_max)
                [lat_lon_bbox[0][1], lat_lon_bbox[0][0]]   # Close the polygon (lon_min, lat_min)
            ]]
        }
        
        extras.append({
            "key": "spatial",
            "value": json.dumps(spatial_geojson)
        })
    
    wcs_extent = get_wcs_extent("https://sparcal.sdsc.edu/geoserver/rrk/wcs", gis_service['layer_name'])
    if not lat_lon_bbox and wcs_extent:
        lat_lon_bbox = convert_coordinates_to_lat_lon(wcs_extent[0], wcs_extent[1])
        spatial_geojson = {
            "type": "Polygon",
            "coordinates": [[
                [lat_lon_bbox[0][1], lat_lon_bbox[0][0]],  # Lower-left corner (lon_min, lat_min)
                [lat_lon_bbox[1][1], lat_lon_bbox[0][0]],  # Lower-right corner (lon_max, lat_min)
                [lat_lon_bbox[1][1], lat_lon_bbox[1][0]],  # Upper-right corner (lon_max, lat_max)
                [lat_lon_bbox[0][1], lat_lon_bbox[1][0]],  # Upper-left corner (lon_min, lat_max)
                [lat_lon_bbox[0][1], lat_lon_bbox[0][0]]   # Close the polygon (lon_min, lat_min)
            ]]
        }
    
        extras.append({
            "key": "spatial",
            "value": json.dumps(spatial_geojson)
        })
        
    resources = rrk_package_dict['resources']        
    wms_resource = {
        "name": f"{fix_title(title.title())}",
        "description": f"WMS for {fix_title(title.title())}",
        "format": "WMS",
        "resource_type": "api",
        "url": "https://sparcal.sdsc.edu/geoserver/rrk/wms",
        "mimetype": "text/xml",
        "wms_layer": gis_service['layer_name'],
        "wms_version": "1.3.0",
        "service_type": gis_service['service_type'],
        "wms_srs": "EPSG:3310",
    }
    resources.append(wms_resource)

    if wcs_extent:
        wcs_resource = {
            "name": f"{fix_title(title.title())}",
            "description": f"WCS for {fix_title(title.title())}",
            "format": "WCS",
            "resource_type": "api",
            "url": "https://sparcal.sdsc.edu/geoserver/rrk/wcs",
            "mimetype": "text/xml",
            "wcs_coverage_id": gis_service['layer_name'].replace(':', '__'),
            "wcs_version": "2.0.1",
            "service_type": gis_service['service_type'],
            "wcs_srs": "EPSG:3310",
        }
        resources.append(wcs_resource)

        extras.append({
            "key": "format",
            "value": rrk_dataset['file_type']
        })
    else:
        wfs_resource = {
            "name": f"{fix_title(title.title())}",
            "description": f"WFS for {fix_title(title.title())}",
            "format": "WFS",
            "resource_type": "api",
            "url": "https://sparcal.sdsc.edu/geoserver/rrk/wfs",
            "mimetype": "text/xml",
            "wfs_feature_id": gis_service['layer_name'],
            "wfs_version": "1.1.0",
            "service_type": gis_service['service_type'],
            "wfs_srs": "EPSG:3310",
        }
        resources.append(wfs_resource)

        extras.append({
            "key": "format",
            "value": "Shapefile"
        })
        
    download_url = None
    for download_url in dataset_download_urls:
        if rrk_dataset['file_path'] in download_url:
            break
    if download_url:
        download_resource = {
            "name": download_url.split('/').pop(),
            "description": "An HTTP link to download the ZIP file",
            "format": rrk_dataset['file_type'] if wcs_extent else 'Shapefile',
            "url": download_url
        }
        resources.append(download_resource)
        
    return rrk_package_dict


def create_dataset(dataset_dict):
    ckan_url = os.getenv('ckan_url')
    api_key = os.getenv('api_key')
    headers = {
        'X-CKAN-API-Key': api_key,
        'Content-Type': 'application/json'
    }

    # create dataset
    api_url = f"{ckan_url}/api/3/action/package_create"

    # Make the API request to create a new dataset
    response = requests.post(api_url, data=json.dumps(dataset_dict), headers=headers)

    # Check the response
    if response.status_code == 200:
        created_package = response.json()['result']
        # print('-' * 70)
        # print("Dataset created successfully:")
        # print(json.dumps(created_package, indent=2))
    else:
        raise BaseException(f"Error creating dataset: {response.text}")


def fix_metadata(dataset):
    if dataset['name'] == 'Tree Mortality - Past 1 Year':
        dataset["dataset_metadata"] = [
            {
                "name": "metric_definition_and_relevance",
                "text_value": "The dead tree canopy cover fraction change from the Mortality Magnitude Index (MMI) for eDaRT events. This metric is provided to complement data (in terms of spatial resolution and canopy cover loss estimates) available from the Region 5 Insect and Disease Survey that performs aerial detection monitoring in support of tracking tree mortality that includes affected hosts and agents (available at: <https://www.fs.usda.gov/detail/r5/forest-grasslandhealth/?cid=fsbdev3_046696>). ",
            },
            {
                "name": "data_units",
                "text_value": "Percent of 30m pixel (absolute, not relative, value)",
            },
            {
                "name": "tier",
                "text_value": "2",
            },
            {
                "name": "creation_method",
                "text_value": "Insect- and disease-caused tree mortality was compiled at the 30 m scale from the Ecosystem Disturbance and Recovery Tracker (eDaRT; Koltunov et al. 2020), described in the [Introduction](https://docs.google.com/document/d/15tXCMkEzUEgQKHoXL74cftwtLuz3z-Rm/edit#heading=h.2s8eyo1). This metric represents the 2021 status of cumulative tree mortality occurring over the years 2017 to 2021. An additional version represents the mortality of the last 1 year (2021). Note that tree mortality which, since its occurrence, was affected by fire or land management activities has been removed. This data layer currently exists only for the Sierra Nevada region. Efforts are underway to explore development of these data for the rest of California.  ",
            },
            {
                "name": "data_vintage",
                "text_value": "2021",
            },
        ]
    if dataset['name'] == 'Tree Mortality - Past 5 Years':
        dataset["dataset_metadata"] = [
            {
                "name": "metric_definition_and_relevance",
                "text_value": "The dead tree canopy cover fraction change from the Mortality Magnitude Index (MMI) for eDaRT events. This metric is provided to complement data (in terms of spatial resolution and canopy cover loss estimates) available from the Region 5 Insect and Disease Survey that performs aerial detection monitoring in support of tracking tree mortality that includes affected hosts and agents (available at: <https://www.fs.usda.gov/detail/r5/forest-grasslandhealth/?cid=fsbdev3_046696>). ",
            },
            {
                "name": "data_units",
                "text_value": "Percent of 30m pixel (absolute, not relative, value) ",
            },
            {
                "name": "tier",
                "text_value": "2",
            },
            {
                "name": "creation_method",
                "text_value": "Insect- and disease-caused tree mortality was compiled at the 30 m scale from the Ecosystem Disturbance and Recovery Tracker (eDaRT; Koltunov et al. 2020), described in the [Introduction](https://docs.google.com/document/d/15tXCMkEzUEgQKHoXL74cftwtLuz3z-Rm/edit#heading=h.2s8eyo1). This metric represents the 2021 status of cumulative tree mortality occurring over the years 2017 to 2021. An additional version represents the mortality of the last 1 year (2021). Note that tree mortality which, since its occurrence, was affected by fire or land management activities has been removed. This data layer currently exists only for the Sierra Nevada region. Efforts are underway to explore development of these data for the rest of California.",
            },
            {
                "name": "data_vintage",
                "text_value": "2021",
            },
        ]
        
    if dataset['name'] == 'Time Since Last Disturbance':
        dataset["dataset_metadata"] = [
            {
                "name": "metric_definition_and_relevance",
                "text_value": """The metric for time since disturbance ("tsd") was measured as time in years before 2021 since the most recent disturbance of at least 25% canopy cover loss per 30m pixel as defined by eDaRT Mortality Magnitude Index (MMI) layers. MMI values less than 25% were not considered. 

The most recent disturbance class ("dist_class") of the most recent
disturbance of 25% magnitude or greater detected by eDaRT and were prioritized
in the order: fire (1), treatment (2), eDaRT (3). For example, if a pixel
intersected a fire perimeter and a treatment polygon, that pixel would be
assigned a code of 1 (fire) rather than 2 (treatment). Note that while the
occurrence of and magnitude of a disturbance was determined using eDaRT,
disturbance class was determined first using fire perimeters and FACTS
activities, with remaining eDaRT disturbances collectively assigned to insect-
and disease-related tree mortality. This data layer currently exists only for
the Sierra Nevada region.""",
            },
            {
                "name": "data_units",
                "text_value": "Years",
            },
            {
                "name": "tier",
                "text_value": "2",
            },
            {
                "name": "creation_method",
                "text_value": """Layers representing time since disturbance, most recent disturbance magnitude, and most recent disturbance class were produced using the Ecosystem Disturbance and Recovery Tracker (eDaRT), Forest Activities ([FACTS](https://data.fs.usda.gov/nrm/briefingpapers/FACTS.pdf)) and CAL FIRE Timber Harvesting Plan ([THP](https://www.fire.ca.gov/programs/resource-management/forest-practice/timber-harvesting/timber-harvesting-plan-thp/)) databases, and the CAL FIRE Fire and Resource Assessment Program ([FRAP](https://frap.fire.ca.gov/mapping/gis-data/)) fire perimeter dataset. All layers are complete for the entire area within the 300s and 400s eDaRT scenes as well as for scenes 103, 105, and 501. The reference year was set to 2021 since fire history and eDaRT only reported up through 2020. The earliest year assessed was 2010 since eDaRT data prior to 2010 was used for model training and is not reliable.  
""",
            },
            {
                "name": "data_vintage",
                "text_value": "2021",
            },
        ]


def validate_org(org_name):
    """
    Validate if an organization exists in CKAN.

    Parameters:
    - ckan_url: str, base URL of the CKAN instance
    - api_key: str, CKAN API key
    - org_name: str, name of the organization to validate

    Returns:
    - bool: True if the organization exists, False otherwise
    """
    ckan_url = os.getenv('ckan_url')
    api_key = os.getenv('api_key')
    headers = {
        'X-CKAN-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    endpoint = f"{ckan_url}/api/3/action/organization_show"
    params = {
        "id": org_name
    }

    response = requests.get(endpoint, headers=headers, params=params)

    if response.status_code != 200:
        raise BaseException(f"The organization {org_name} doesn't exist in CKAN.")

        
def save_clm_to_ckan():
    
    # load CLM datasets from fast api
    url = os.getenv('rrk_api_url')
    org = os.getenv('org_ckan_name')
    validate_org(org)
  
    response = requests.get(f"{url}/DatasetCollection/100/Dataset?skip=0&limit=500&order_by=dataset_id&ascending=true")
    response.raise_for_status()
    datasets = response.json()

    # load clm hierarchy
    hierarchy = get_clm_hierarchy()

    # load clm download urls
    with open("clm_download_urls.json", "r") as json_file:
        dataset_download_urls = json.load(json_file)
        
    # load precalculated keywords
    with open("dataset_keywords_map.json", "r") as json_file:
        dataset_keywords_map = json.load(json_file)

    packages = []
    for index, dataset in enumerate(datasets):
        # print("=" * 70)
        # print(json.dumps(dataset, indent=4))

        # fix missing metadata for three datasets
        has_notes = False
        for metadata in dataset["dataset_metadata"]:
            if metadata["name"] == 'metric_definition_and_relevance':
                has_notes = True
        if not has_notes:
            fix_metadata(dataset)
                    
        # get hierarchy and label 
        category, label = get_category(dataset["dataset_id"], hierarchy)

        # create json for CKAN package 
        package_dict = transform_to_ckan_package(dataset, org, category, label, dataset_keywords_map, dataset_download_urls)

        if not "notes" in package_dict.keys():
            raise ValueError(f'No notes: {package_dict["name"]}')

        packages.append(package_dict)
        
        print(f"creating {package_dict['title']}")
        create_dataset(package_dict)
        
    with open("/tmp/rrk.json", "w") as json_file:
        json.dump(packages, json_file, indent=4)


if __name__ == "__main__":
    try:
        save_clm_to_ckan()
    except BaseException as e:
        if "That URL is already in use." in str(e):
            print(f"Error: the dataset with the same name exists in CKAN")
        elif "Organization does not exist" in str(e):
            print(f"Error: No orgnaization in CKAN has the name: {os.getenv('org_ckan_name')}")
        else:
            print(f"Error: {str(e)}")
            raise
