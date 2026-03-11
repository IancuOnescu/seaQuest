from seaquest import uploader
from seaquest.utils import pod
from test_vars import *


def test_setup_conditions():
    try:
        uploader._create_pvc(api_instance_core, namespace, pvc_name_prefix)
    except Exception as e:
        assert False, "Failed to setup testing environment"


def test_make_pod_name_unique():
    try:
        _ = pod.make_pod_name_unique(api_instance_core, namespace, pod_name_prefix)
    except Exception as e:
        assert False, "Could not generate a unique pod name!"


def test_launch_pod_pass():
    pod_name_tmp = None
    try:
        pod_name_tmp = pod.make_pod_name_unique(api_instance_core, namespace, pod_name_prefix)
        pod._launch_pod(api_instance_core, namespace, pod_name_tmp, pvc_name_prefix)

        pod._delete_pod(api_instance_core, namespace, pod_name_tmp)
    except Exception as e:    
        pod._delete_pod(api_instance_core, namespace, pod_name_tmp)
        assert False, f"Launching temp pod failed with exception: {e}"


def test_launch_temp_pod_fail():
    pod_name_tmp = None
    try:
        # launching a pod with a non-existing pvc should fail
        pod_name_tmp = pod.make_pod_name_unique(api_instance_core, namespace, pod_name_prefix)
        pod._launch_pod(api_instance_core, namespace, pod_name_tmp, "no-pvc")
        pod._delete_pod(api_instance_core, namespace, pod_name_tmp)
    except Exception as e:
        pod._delete_pod(api_instance_core, namespace, pod_name_tmp)
        assert True, "Launching temp pod failed as expected since pvc does not exist."


def test_delete_pod():
    pod_name_tmp = None
    try:
        pod_name_tmp = pod.make_pod_name_unique(api_instance_core, namespace, pod_name_prefix)
        pod._launch_pod(api_instance_core, namespace, pod_name_tmp, pvc_name_prefix)
        
        pod._wait_for_running_state(api_instance_core, namespace, pod_name_tmp, pod_wait_timeout)
        pod._delete_pod(api_instance_core, namespace, pod_name_tmp)
    except Exception as e:
        pod._delete_pod(api_instance_core, namespace, pod_name_tmp)
        assert False, f"Deleting temp pod failed with exception: {e}"


def test_timeout_waiting_for_pod():
    pod_name_tmp = None
    try:
        pod_name_tmp = pod.make_pod_name_unique(api_instance_core, namespace, pod_name_prefix)
        pod._launch_pod(api_instance_core, namespace, pod_name_tmp, pvc_name_prefix)
        
        pod._wait_for_running_state(api_instance_core, namespace, pod_name_tmp, 1) # wait 1 second
        pod._delete_pod(api_instance_core, namespace, pod_name_tmp)
    except TimeoutError:
        pod._delete_pod(api_instance_core, namespace, pod_name_tmp)
        assert True
    except Exception as e:
        pod._delete_pod(api_instance_core, namespace, pod_name_tmp)
        assert False, f"Test failed with exception: {e}"


def test_clean_up():
    try:
        uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)
    except Exception as e:
        assert False, "Cleanup failed with exception: {e}".format()
    pass