import requests
import xml.etree.ElementTree as ET

layers = None


def get_wms_info(wms_url):
    params = {
        'service': 'WMS',
        'version': '1.3.0',  # or '1.1.1'
        'request': 'GetCapabilities'
    }

    try:
        # Make request
        response = requests.get(wms_url, params=params)

        # Try to fix common XML issues
        xml_text = response.text

        # Try to parse XML
        try:
            # Parse XML using default parser
            root = ET.fromstring(xml_text)

            # Find layers (try different possible paths)
            layers = []
            for path in [
                './/{http://www.opengis.net/wms}Layer',
                './/Layer',
                './Capability/Layer/Layer'  # Common path in WMS 1.1.1
            ]:
                layers.extend(root.findall(path))

            layers_info = []
            for layer in layers:
                try:
                    # Try different possible tag paths
                    name = None
                    for name_path in ['./{http://www.opengis.net/wms}Name', './Name']:
                        name_elem = layer.find(name_path)
                        if name_elem is not None:
                            name = name_elem.text
                            break

                    title = None
                    for title_path in ['./{http://www.opengis.net/wms}Title', './Title']:
                        title_elem = layer.find(title_path)
                        if title_elem is not None:
                            title = title_elem.text
                            break

                    bbox = None
                    for bbox_path in ['./{http://www.opengis.net/wms}BoundingBox', './BoundingBox']:
                        bbox_elem = layer.find(bbox_path)
                        if bbox_elem is not None:
                            bbox = {
                                'minx': bbox_elem.get('minx'),
                                'miny': bbox_elem.get('miny'),
                                'maxx': bbox_elem.get('maxx'),
                                'maxy': bbox_elem.get('maxy')
                            }
                            break

                    if name:  # Only add if we found a name
                        layer_info = {
                            'name': name,
                            'title': title,
                            'bbox': bbox
                        }
                        layers_info.append(layer_info)

                except Exception as e:
                    print(f"Error parsing layer: {e}")
                    continue

            return layers_info

        except ET.ParseError as e:
            # If parsing fails, print the XML for debugging
            print(f"XML parsing error: {e}")
            print("Raw XML response:")
            print(xml_text[:1000])  # Print first 1000 chars of response
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None


def get_extent_for_wms_layer(layer_name):
    wms_url = "https://sparcal.sdsc.edu/geoserver/rrk/wms"
    global layers
    if layers is None:
        layers = get_wms_info(wms_url)
    if layers:
        for layer in layers:
            """
            print(f"Layer: {layer['name']}")
            print(f"Title: {layer['title']}")
            print(f"BBox: {layer['bbox']}")
            print("---")
            """
            if layer_name.endswith(layer['name']):
                lat_min = float(layer['bbox']['miny'])
                lon_min = float(layer['bbox']['minx'])
                lat_max = float(layer['bbox']['maxy'])
                lon_max = float(layer['bbox']['maxx'])
                return ((lat_min, lon_min), (lat_max, lon_max))
    return None
