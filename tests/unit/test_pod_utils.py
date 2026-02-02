from kubernetes import client, config

from seaquest import uploader
from seaquest.utils import pod

config.load_kube_config()
api_instance = client.CoreV1Api()

namespace = "dl4nlpspace"
prefix = "ionestest"

pod_name = "iones-seaquest-test-pod"
pvc_name = "ionestest-test-pvc"
timeout = 120 # seconds


def setup_conditions():
    try:
        uploader._create_pvc(api_instance, namespace, pvc_name)
    except Exception as e:
        assert False, "Failed to setup testing environment"


def test_make_pod_name_unique():
    try:
        pod_name_tmp = pod.make_pod_name_unique(api_instance, namespace, pod_name)
    except Exception as e:
        assert False, "Could not generate a unique pod name!"

def test_launch_pod_pass():
    pod_name_tmp = pod.make_pod_name_unique(api_instance, namespace, pod_name)
    try:
        pod._launch_pod(api_instance, namespace, pod_name_tmp, pvc_name)

        pod._delete_pod(api_instance, namespace, pod_name_tmp)
        # TODO: delete the pvc
    except Exception as e:    
        pod._delete_pod(api_instance, namespace, pod_name_tmp)
        # TODO: delete the pvc
        assert False, f"Launching temp pod failed with exception: {e}"


def test_launch_temp_pod_fail():
    # launching a pod with a non-existing pvc should fail
    pod_name_tmp = pod.make_pod_name_unique(api_instance, namespace, pod_name)
    try:
        pod._launch_pod(api_instance, namespace, pod_name_tmp, "no-pvc")
        pod._delete_pod(api_instance, namespace, pod_name_tmp)
    except Exception as e:
        pod._delete_pod(api_instance, namespace, pod_name_tmp)
        assert True, "Launching temp pod failed as expected since pvc does not exist."


def test_delete_pod():
    pod_name_tmp = pod.make_pod_name_unique(api_instance, namespace, pod_name)
    try:
        pod._launch_pod(api_instance, namespace, pod_name_tmp, pvc_name)
        
        pod._wait_for_running_state(api_instance, namespace, pod_name_tmp, timeout)
        pod._delete_pod(api_instance, namespace, pod_name_tmp)
    except Exception as e:
        pod._delete_pod(api_instance, namespace, pod_name_tmp)
        assert False, f"Deleting temp pod failed with exception: {e}"


def test_timeout_waiting_for_pod():
    pod_name_tmp = pod.make_pod_name_unique(api_instance, namespace, pod_name)
    try:
        pod._launch_pod(api_instance, namespace, pod_name_tmp, pvc_name)
        
        pod._wait_for_running_state(api_instance, namespace, pod_name_tmp, 1)
        pod._delete_pod(api_instance, namespace, pod_name_tmp)
    except TimeoutError:
        pod._delete_pod(api_instance, namespace, pod_name_tmp)
        assert True
    except Exception as e:
        pod._delete_pod(api_instance, namespace, pod_name_tmp)
        assert False, f"Test failed with exception: {e}"


def clean_up():
    #TODO: delete pvc
    pass