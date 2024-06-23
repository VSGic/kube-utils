from kubernetes import client, config
from kubernetes.client.rest import ApiException
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
namespace_pods = "kube-system"

###### END VARIABLES ######
dns_pods = []
dns_pods_check = []
pod_state = []

# Create an API client with the provided token
configuration.api_key = {"authorization": "Bearer " + token}
client.Configuration.set_default(configuration)
v1 = client.CoreV1Api()

def get_coredns_pods():
    try:
        ret = v1.list_namespaced_pod(namespace=namespace_pods)
        for pod in ret.items:
            if "coredns" in pod.metadata.name:
                dns_pods.append(pod.metadata.name)
        print(dns_pods)
    except ApiException as e:
        print(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")

def get_phase():
    try:
        ret = v1.list_namespaced_pod(namespace=namespace_pods)
        for pod in ret.items:
            if "coredns" in pod.metadata.name:
                print(pod.status.phase)
    except ApiException as e:
        print(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")

def get_image():
    try:
        ret = v1.list_namespaced_pod(namespace=namespace_pods)
        for pod in ret.items:
            if "coredns" in pod.metadata.name:
                print(pod.status.container_statuses[0].image)
    except ApiException as e:
        print(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")

def pod_restart(pod_to_restart):
    try:
        # Delete the pod
        v1.delete_namespaced_pod(name=pod_to_restart, namespace=namespace_pods)
        print(f"Pod {pod_to_restart} in namespace {namespace_pods} deleted successfully.")
        time.sleep(10)
    except client.exceptions.ApiException as e:
        print(f"Exception when calling CoreV1Api->delete_namespaced_pod: {e}")

def check_coredns_pods():
    try:
        ret = v1.list_namespaced_pod(namespace=namespace_pods)
        for pod in ret.items:
            if "coredns" in pod.metadata.name:
                dns_pods_check.append(pod.metadata.name)
        print(f"checking {dns_pods_check}")
    except ApiException as e:
        print(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")

def get_phase_coredns():
    try:
        for i in range(len(dns_pods_check)):
            pod = v1.read_namespaced_pod(name=dns_pods_check[i], namespace=namespace_pods)
            if pod.status.phase != "Running":
                print(pod.status.phase)
                sys.exit("Check coredns logs!")                               
            else:
                print(pod.status.phase)       
    except ApiException as e:
        print(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")


if __name__ == "__main__":

    get_coredns_pods()
    for i in range(len(dns_pods)):
        pod_restart(dns_pods[i])
        check_coredns_pods()        
        get_phase_coredns()
        dns_pods_check.clear()
    dns_pods.clear()
    get_coredns_pods()
