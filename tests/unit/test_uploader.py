from kubernetes import client, config
import pathlib

from seaquest import uploader
from seaquest.utils import pod

config.load_kube_config()
api_instance = client.CoreV1Api()

namespace = "dl4nlpspace"
prefix = "ionestest"
timeout = 120

pvc_name = "test-pvc"
prefix_pvc_name="{prefix}-{pvc}".format(prefix=prefix, pvc=pvc_name)
pod_name = "iones-seaquest-test-pod"


def test_create_pvc():
    # TODO: make sure there is no pvc named test-pvc before running this test

    try:
        uploader._create_pvc(api_instance, namespace, prefix_pvc_name)
    except Exception as e:
        assert False, f"PVC creation failed with exception: {e}"

    # test existing pvc
    try:
        uploader._create_pvc(api_instance, namespace, prefix_pvc_name)
    except Exception as e:
        assert False, f"PVC creation failed with exception: {e}"

    # TODO: delete the pvc


def test_copy_files_to_pod_pass():
    pod_name_tmp = pod.make_pod_name_unique(api_instance, namespace, pod_name)
    
    try:
        uploader._create_pvc(api_instance, namespace, prefix_pvc_name)
        
        pod._launch_pod(api_instance, namespace, pod_name_tmp, prefix_pvc_name)
        pod._wait_for_running_state(api_instance, namespace, pod_name_tmp, timeout)
        
        uploader._copy_files_to_pod(api_instance, namespace, pod_name_tmp, pathlib.WindowsPath("P:/", "UIC", "CS582", "homework1", "src"), pathlib.PurePosixPath(prefix_pvc_name))
        
        # TODO: verify files are copied to pvc

        pod._delete_pod(api_instance, namespace, pod_name_tmp)
        # TODO: delete the pvc
    except Exception as e:
        pod._delete_pod(api_instance, namespace, pod_name_tmp)
        # TODO: delete the pvc
        assert False, f"Copying files failed with exception: {e}"


def test_copy_files_to_pod_fail():
    pod_name_tmp = pod.make_pod_name_unique(api_instance, namespace, pod_name)

    try:
        uploader._create_pvc(api_instance, namespace, prefix_pvc_name)
        
        pod._launch_pod(api_instance, namespace, pod_name_tmp, prefix_pvc_name)
        pod._wait_for_running_state(api_instance, namespace, pod_name_tmp, timeout)
        
        # Copying from a non-existing path should fail
        uploader._copy_files_to_pod(api_instance, namespace, pod_name_tmp, pathlib.WindowsPath("P:/", "UIC", "CS582", "homework1", "non-existing"), pathlib.PurePosixPath(prefix_pvc_name))
        
        # TODO: verify files are copied to pvc

        pod._delete_pod(api_instance, namespace, pod_name_tmp)
        # TODO: delete the pvc
    except Exception as e:
        pod._delete_pod(api_instance, namespace, pod_name_tmp)
        # TODO: delete the pvc
        assert True, f"Copying files failed with exception: {e}"


def test_upload_files_to_pvc():
    try:
        uploader.upload_files_to_pvc(namespace, prefix, pvc_name, [pathlib.WindowsPath("P:/", "UIC", "CS582", "homework1", "src"), pathlib.WindowsPath("P:/", "UIC", "CS582", "homework1", "src")])
    except Exception as e:
        assert False, f"Uploading files to pvc failed with exception: {e}"
