
import os
import json
import requests

from dotenv import load_dotenv


load_dotenv()


def get_clm_hierarchy():
    url = os.getenv('rrk_api_url')
    response = requests.get(f"{url}/DatasetCollection/100/taxonomy/33/hierarchy")
    response.raise_for_status()
    return response.json()
    
    
def get_category(dataset_id, forest):
    for tree in forest:
        if "taxonomy_item_name" in tree.keys() and "children" in tree.keys():
            children = tree["children"]
            subtree = []
            for kid in children:
                if "dataset_id" in kid.keys():
                    if kid["dataset_id"] == dataset_id:
                        return tree["key"], tree["label"]
                else:
                    subtree.append(kid)        
            if kid:
                key, label = get_category(dataset_id, subtree)
                if key:
                    return key, label
        else:
            continue
    return None, None


def is_unique_title(title):
    datasets = get_datasets(title, hierarchy)
    return len(datasets) == 1
        

def get_datasets(title, forest):
    datasets = []
    subtree = []
    for tree in forest:
        if "taxonomy_item_name" in tree.keys() and "children" in tree.keys():
            subtree = subtree + tree["children"]
        elif tree["dataset_name"] == title:
            datasets.append(tree["dataset_id"])
    if subtree:
        tmp = get_datasets(title, subtree)
        datasets = datasets + tmp
    return datasets


