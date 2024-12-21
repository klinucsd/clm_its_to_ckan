# CLM & ITS Dataset CKAN Registration Tool

A Python-based tool for registering California Landscape Metrics (CLM) and California Wildfire & Landscape Resilience Interagency Treatments datasets into CKAN data portals.

## Features

- Automated registration of CLM and ITS datasets to CKAN
- Intelligent dataset naming and categorization
- Automatic keyword generation using LLM
- Spatial metadata integration
- Support for WMS, WCS, and WFS endpoints
- Dataset removal capabilities

## Prerequisites

- Python 3.7 or higher
- Access to a CKAN instance
- Valid CKAN API key
- Organization already created in CKAN

## Installation

1. Clone this repository:
   ```bash
   git clone [repository-url]
   cd [repository-name]
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory with the following parameters:

```env
CKAN_URL=your_ckan_url
API_KEY=your_api_key
ORG_CKAN_NAME=your_organization_name
RRK_API_URL=default_value  # Leave as default
```

> **Note**: Ensure your `ORG_CKAN_NAME` corresponds to an existing organization in your CKAN instance.

## Usage

### Register Datasets

To register all CLM and ITS datasets to CKAN:

```bash
python save_clm_and_its_to_ckan.py
```

### Remove Datasets

To remove all previously registered CLM and ITS datasets from CKAN:

```bash
python delete_clm_and_its_from_ckan.py
```

## Data Processing Features

### Naming Convention Improvements

The tool implements intelligent naming conventions to handle challenging dataset names:

- Standardizes diameter measurements (e.g., ">40" Dbh" → "Greater than 40 inch Dbh")
- Clarifies regional datasets by adding category prefixes:
  - "Sierra Nevada" → "Tree Density - Sierra Nevada Region"
  - "Northern California" → "Population Distribution - Northern California"

### Metadata Enhancements

1. **Automated Tagging**
   - Generates three relevant keywords per dataset using LLM
   - All tags undergo manual review for accuracy
   - Tags are standardized for CKAN compatibility

2. **Spatial Data Integration**
   - Captures and includes bounding box coordinates
   - Preserves spatial reference information
   - Maintains dataset projection details

3. **Category Management**
   - Preserves original CLM categorization
   - Implements hierarchical category structure
   - Enables efficient dataset organization

4. **Resource Integration**
   - Automatically adds relevant geospatial endpoints:
     - Web Map Service (WMS)
     - Web Coverage Service (WCS)
     - Web Feature Service (WFS)
   - Validates endpoint accessibility
   - Maintains service metadata

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

[Specify your license here]

## Support

For issues and questions, please [open an issue](issues-url) in the repository.
