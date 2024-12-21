import os
import json
from save_clm_to_ckan import create_dataset, slugify
from dotenv import load_dotenv

load_dotenv()


def save_its_to_ckan():
    title = "California Wildfire & Landscape Resilience Interagency Treatments"
    name = slugify(f'its-{title}')
    org = os.getenv('org_ckan_name')
    notes = """
WildfireTaskForce.org

As California works toward ambitious wildfire and landscape resilience goals, transparency and effective planning tools are critical to success. The California Wildfire and Landscape Interagency Treatment Tracking System, for the first time ever in California, provides a single source for displaying recently completed forest and wildland projects from over a dozen different federal and state agencies.

What is the Wildfire & Landscape Resilience Interagency Treatment Tracking System and Dashboard?

The Interagency Treatment Tracking System is a first-of-its-kind database that catalogs the location and extent of federal and state wildfire and landscape resilience treatments throughout the state. The Wildfire & Landscape Resilience Interagency Treatment Dashboard (hereafter Dashboard) provides a highly interactive online tool by which users can explore these data, sorting treatments by region, county, land ownership, and more. By charting the work of what has been accomplished to date, this information can be used to guide practitioners on where to plan new projects.

What is included in the geodatabase download?

The geodatabase provided here provides treatment point, line, and polygon data from state and federal land management databases covering the State of California. Please see the documentation available at https://wildfiretaskforce.org/treatment-dashboard/ for information on the original data sources and processing procedures. The information in the geodatabase contains the data processed into the Interagency Treatment Tracking System schema. A subset of these data are included on the Dashboard, but the geodatabase includes activity types (such as some forms of timber harvest or ecological restoration) and years of data that are not included on the Dashboard. The additional data should not be considered complete and comprehensive because there are known gaps in the source data.
    """

    lat_lon_bbox = ((-1383489.9179190733, 3836082.3922780156), (-12735118.01130016, 5161279.835675545))
    spatial_geojson = {
        "type": "Polygon",
        "coordinates": [[
            [lat_lon_bbox[0][1], lat_lon_bbox[0][0]],  # Lower-left corner (lon_min, lat_min)
            [lat_lon_bbox[1][1], lat_lon_bbox[0][0]],  # Lower-right corner (lon_max, lat_min)
            [lat_lon_bbox[1][1], lat_lon_bbox[1][0]],  # Upper-right corner (lon_max, lat_max)
            [lat_lon_bbox[0][1], lat_lon_bbox[1][0]],  # Upper-left corner (lon_min, lat_max)
            [lat_lon_bbox[0][1], lat_lon_bbox[0][0]]  # Close the polygon (lon_min, lat_min)
        ]],
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:EPSG::3857"
            }
        }
    }

    package_dict = {
        'name': name,
        'title': title,
        'owner_org': org,
        'notes': notes,
        'type': "dataset",
        "private": False,
        "resources": [
            {
                "name": "Interagency_Tracking_System_V1.1_output_data_only.gdb.zip",
                "description": "Zipped Geodatabase containing Interagency Tracking System V1.1 output data",
                "url": "https://portal.sparcal.sdsc.edu/arcgis/sharing/rest/content/items/382c2b34f6b9405594f7066118e240d5/data",
                "format": "GDB",
            }, {
                "name": "ITS_V1_1_points_gdb",
                "description": "Point geometries from ITS_Geodatabase_V1.1",
                "url": "https://sparcal.sdsc.edu/arcgis/rest/services/Hosted/ITS_V1_1_points_gdb/FeatureServer/0",
                "format": "ArcGIS Feature Service",
            }, {
                "name": "ITS_V1_1_lines_gdb",
                "description": "Line geometries from ITS_Geodatabase_V1.1",
                "url": "https://sparcal.sdsc.edu/arcgis/rest/services/Hosted/ITS_V1_1_lines_gdb/FeatureServer/0",
                "format": "ArcGIS Feature Service",
            }, {
                "name": "ITS_V1_1_polygons_gdb",
                "description": "Polygon geometries from ITS_Geodatabase_V1.1",
                "url": "https://sparcal.sdsc.edu/arcgis/rest/services/Hosted/ITS_V1_1_polygons_gdb/FeatureServer/0",
                "format": "ArcGIS Feature Service",
            }
        ],
        "tags": [
            {"name": "ITS"},
            {"name": "Million Acres"},
            {"name": "Vegetation Management"},
            {"name": "Interagency Tracking System"},
            {"name": "Fuels Reduction"},
            {"name": "Forest Resilience"},
            {"name": "Forest"},
            {"name": "Forest Health"},
            {"name": "Fire"},
            {"name": "California Wildfire and Forest Resilience Task Force"},
            {"name": "California"},
        ],
        "extras": [
            {
                "key": "spatial",
                "value": json.dumps(spatial_geojson)
            }, {
                "key": "EPSG",
                "value": "3857"
            }
        ]
    }
    print(f"creating {package_dict['title']}")
    create_dataset(package_dict)


if __name__ == "__main__":
    try:
        save_its_to_ckan()
    except BaseException as e:
        if "That URL is already in use." in str(e):
            print(f"Error: the dataset with the same name exists in CKAN")
        elif "Organization does not exist" in str(e):
            print(f"Error: No orgnaization in CKAN has the name: {os.getenv('org_ckan_name')}")
        else:
            print(f"Error: {str(e)}")
