from kubernetes import client, config
from kubernetes.client.rest import ApiException
from requests.auth import HTTPBasicAuth
import requests
import json
import time
import sys
import os

configuration = client.Configuration()

###### VARIABLES #######
token = os.getenv('PATROL_TOKEN')
configuration.host = os.getenv('PATROL_HOST')
configuration.ssl_ca_cert = "ca.crt"
configuration.cert_file = "client.crt"
configuration.key_file = "client.key"
#configuration.verify_ssl = False  # Set to True with proper certificate if required
namespace_pods = "<namespace of pods>"

base_url = "<base url of nexus repo>"
base_repo = ['<base repo without protocol>']
username = "<your nexus user>"
password = "<your password>"
#cert = "nexus.crt"
#key = "nexus.key"
###### END VARIABLES ######
crm_pods = []
crm_images = []
main_image_filter = []

# Create an API client with the provided token
configuration.api_key = {"authorization": "Bearer " + token}
client.Configuration.set_default(configuration)
v1 = client.CoreV1Api()

def get_crm_pods():
    try:
        ret = v1.list_namespaced_pod(namespace=namespace_pods)
        for pod in ret.items:
            crm_pods.append(pod.metadata.name)
    except ApiException as e:
        print(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")

def temp_filter(crm_images_filtered):
    string_for_process = crm_images_filtered
    app_name, version = string_for_process.split(':')
    return app_name, version

def main_images_filter():
     apps_actual = []
     for repos in base_repo:
         filter_images = [
             item for item in crm_images
             if (repos in item)
     ]   
     for item in filter_images:
         filtered_address = item.split('/')[1:]         
         print("Filtered address: "+ str(filtered_address))
         apps_actual.append(filtered_address[1])
     apps_actual = list(set(apps_actual))
     return apps_actual

def get_image():
    try:
        ret = v1.list_namespaced_pod(namespace=namespace_pods)
        for pod in ret.items:
            crm_images.append(pod.status.container_statuses[0].image)
        print("Images list: " + str(crm_images))
        seen = []
        crm_images_filtered = []
        for item in crm_images:
            if item not in seen:
                seen.append(item)
                crm_images_filtered.append(item)
        return crm_images_filtered
    except ApiException as e:
        print(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")

def get_nexus_images(base_url, application_name, username, password, cert, key):
    url = f"{base_url}/v2/crm-prod/{application_name}/tags/list"
    response = requests.get(url, auth=HTTPBasicAuth(username, password), verify=False)
    if response.status_code == 200:
        data = response.json()
        tags = data.get('tags', [])
        return tags
    else:
        print(f"Failed to retrieve images. Status code: {response.status_code}")
        return None

def remove_images_nexus(base_url, application_name, username, password, cert, key, remove_tags):
    url = f"{base_url}/service/rest/v1/search?repository=docker&name=crm-prod/{application_name}"
    response = requests.get(url, auth=HTTPBasicAuth(username, password), verify=False)
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Error to get list. Status code: {response.status_code}")
    items = data.get("items", [])
    matched_items = []
    for item in items:
        if item.get("version") in remove_tags:
           remove_id = item.get("id")
           url = f"{base_url}/service/rest/v1/components/{remove_id}"
           response = requests.delete(url, auth=HTTPBasicAuth(username, password), verify=False)
           if response.status_code == 202 or response.status_code == 204:
             print("Image removed")
           else:
             print(f"Failed to remove. Status code: {response.status_code}") 


if __name__ == "__main__":
# get list of pods
    get_crm_pods()
# get list of images
    crm_images_filtered = get_image()
# get list of apps 
    apps_actual = main_images_filter()
    print("apps_actual: " + str(apps_actual))
    for item in apps_actual:
        application_name, version_tag = temp_filter(item)
        current_tags = get_nexus_images(base_url, application_name, username, password, cert, key)
        print("Tags to remove: " + str(current_tags))
        remove_tags = [tag for tag in current_tags if tag != version_tag]
        print("Tags removed: " + str(remove_tags))
        remove_images_nexus(base_url, application_name, username, password, cert, key, remove_tags)
