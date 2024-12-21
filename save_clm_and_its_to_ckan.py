
import os
from dotenv import load_dotenv
from save_clm_to_ckan import save_clm_to_ckan
from save_its_to_ckan import save_its_to_ckan


load_dotenv()


if __name__ == "__main__":
    try:
        save_its_to_ckan()
        save_clm_to_ckan() 
    except BaseException as e:
        if "That URL is already in use." in str(e):
            print(f"Error: the dataset with the same name exists in CKAN")
        elif "Organization does not exist" in str(e):
            print(f"Error: No orgnaization in CKAN has the name: {os.getenv('org_ckan_name')}")
        else:
            print(f"Error: {str(e)}")

