import pathlib

from seaquest import uploader
from seaquest.utils import pod

from test_vars import *


def test_check_pvc_exists_false():
    try:
        # in case there is a pvc not deleted by another test
        uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)
    except:
        pass
    try:
        ret = uploader._check_pvc_exists(api_instance_core, namespace, "hocus-pocus")
        assert ret == False, "PVC check failed"
    except Exception as e:
        assert False, f"PVC check failed with exception: {e}"


def test_create_pvc():
    try:
        uploader._create_pvc(api_instance_core, namespace, pvc_name_prefix)
    except Exception as e:
        assert False, f"PVC creation failed with exception: {e}"

    # test existing pvc
    try:
        uploader._create_pvc(api_instance_core, namespace, pvc_name_prefix)
    except Exception as e:
        assert False, f"PVC creation failed with exception: {e}"


def test_check_pvc_exists_true():
    try:
        ret = uploader._check_pvc_exists(api_instance_core, namespace, pvc_name_prefix)
        assert ret == True, "PVC check failed"
    except Exception as e:
        assert False, f"PVC check failed with exception: {e}"    


def test_copy_files_to_pod_pass():
    pod_name_tmp = None
    try:
        pod_name_tmp = pod.make_pod_name_unique(api_instance_core, namespace, pod_name)
        pod._launch_pod(api_instance_core, namespace, pod_name_tmp, pvc_name_prefix)
        pod._wait_for_running_state(api_instance_core, namespace, pod_name_tmp, pod_wait_timeout)
        
        uploader._copy_files_to_pod(api_instance_core, namespace, pod_name_tmp, test_model_dir_path, pathlib.PurePosixPath(pvc_name_prefix))
        
        # TODO: verify files are copied to pvc

        pod._delete_pod(api_instance_core, namespace, pod_name_tmp)
    except Exception as e:
        pod._delete_pod(api_instance_core, namespace, pod_name_tmp)
        assert False, f"Copying files failed with exception: {e}"


def test_copy_files_to_pod_fail():
    pod_name_tmp = None
    try:
        pod_name_tmp = pod.make_pod_name_unique(api_instance_core, namespace, pod_name)
        uploader._create_pvc(api_instance_core, namespace, pvc_name_prefix)
        
        pod._launch_pod(api_instance_core, namespace, pod_name_tmp, pvc_name_prefix)
        pod._wait_for_running_state(api_instance_core, namespace, pod_name_tmp, pod_wait_timeout)
        
        # Copying from a non-existing path should fail
        uploader._copy_files_to_pod(api_instance_core, namespace, pod_name_tmp, pathlib.WindowsPath("C:/", "hocus-pocus"), pathlib.PurePosixPath(pvc_name_prefix))
        
        # TODO: verify files are copied to pvc

        pod._delete_pod(api_instance_core, namespace, pod_name_tmp)
    except Exception as e:
        pod._delete_pod(api_instance_core, namespace, pod_name_tmp)
        assert True, f"Copying files failed with exception: {e}"


def test_upload_files_to_pvc():
    try:
        uploader.upload_files_to_pvc(namespace, prefix, pvc_name, [ \
                [test_model_dir_path, None],
                [config_file_path, test_model_dir_path.name]
            ])
    except Exception as e:
        assert False, f"Uploading files to pvc failed with exception: {e}"


def test_clean_up():
    try:
        uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)
    except Exception as e:
        assert False, "Cleanup failed with exception: {e}".format(e=e)