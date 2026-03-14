import os
import pathlib
from time import sleep

from kubernetes import client, config

from seaquest import monitor, launcher, uploader
from seaquest.utils import validate, pod, loggus
from test_vars import *

logger = loggus.init_logger("test_monitor")

def test_delete_job_pass():
    try:
        args = validate.parse_and_validate_args(COMPLETE_ARGS.copy())
        launcher._launch_job(api_instance_batch, namespace, test_job_name_prefix, args["job_spec"], pvc_name_prefix, job_arguments)
        monitor._delete_job(api_instance_batch, namespace, test_job_name_prefix)
        sleep(5)
    except Exception as e:
        assert False, "Failed to delete job with err {e}".format(e=e)


def test_delete_job_fail():
    try:
        args = validate.parse_and_validate_args(COMPLETE_ARGS.copy())
        launcher._launch_job(api_instance_batch, namespace, test_job_name_prefix, args["job_spec"], pvc_name_prefix, job_arguments)
        monitor._delete_job(api_instance_batch, namespace, "hocus-pocus")

        # just in case
        monitor._delete_job(api_instance_batch, namespace, test_job_name_prefix)
    except Exception as e:
        monitor._delete_job(api_instance_batch, namespace, test_job_name_prefix)
        assert True, "Failed to delete job with err {e}".format(e=e)


def test_copy_files_from_pod():
    try:
        uploader.upload_files_to_pvc(namespace, prefix, pvc_name, files_path)
        pod._launch_pod(api_instance_core, namespace, pod_name_prefix, pvc_name_prefix)
        pod._wait_for_running_state(api_instance_core, namespace, pod_name_prefix, pod_wait_timeout)

        output_path = pathlib.Path.cwd().resolve().joinpath("tests//unit//outputs")
        output_path.mkdir(exist_ok=True)
        monitor._copy_files_from_pod(api_instance_core, pod_name_prefix, namespace, pathlib.Path("{p}/test_model_dir".format(p=pvc_name_prefix)), output_path)

        pod._delete_pod(api_instance_core, namespace, pod_name_prefix)
        uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)
    except Exception as e:
        pod._delete_pod(api_instance_core, namespace, pod_name_prefix)
        uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)
        sleep(5)
        assert False, "Test copy files from pod failed with error {e}".format(e=e)


def test_copy_files_from_pod_fail():
    try:
        uploader.upload_files_to_pvc(namespace, prefix, pvc_name, files_path)
        pod._launch_pod(api_instance_core, namespace, pod_name_prefix, pvc_name_prefix)
        pod._wait_for_running_state(api_instance_core, namespace, pod_name_prefix, pod_wait_timeout)

        output_path = pathlib.Path.cwd().resolve().joinpath("tests//unit/outputs")
        output_path.mkdir(exist_ok=True)
        monitor._copy_files_from_pod(api_instance_core, pod_name_prefix, namespace, pathlib.Path("{p}/hocus-pocus".format(p=pvc_name_prefix)), output_path)

        pod._delete_pod(api_instance_core, namespace, pod_name_prefix)
        uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)
    except Exception as e:
        pod._delete_pod(api_instance_core, namespace, pod_name_prefix)
        uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)
        sleep(5)
        assert True


def test_monitor_jobs():
    try:
        uploader._create_pvc(api_instance_core, namespace, pvc_name_prefix)

        args = validate.parse_and_validate_args(COMPLETE_ARGS.copy())
        launcher._launch_job(api_instance_batch, namespace, test_job_name_prefix, args["job_spec"], pvc_name_prefix, job_arguments)


        monitor._monitor_jobs(api_instance_batch, api_instance_core, namespace, [test_job_name_prefix], pvc_name_prefix, pathlib.WindowsPath("C:/", "Users", "Iancu", "Desktop"), prefix) 
        
        uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)
    except Exception as e:
        monitor._delete_job(api_instance_batch, namespace, test_job_name_prefix)
        uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)
        assert False, "Test monitor jobs failed with error {e}".format(e=e)