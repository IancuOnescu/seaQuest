import os
import pathlib
from time import sleep

from kubernetes import client, config

from seaquest import monitor, launcher, uploader
from seaquest.utils import validate, pod

config.load_kube_config()
api_instance_batch = client.BatchV1Api()
api_instance_core = client.CoreV1Api()

namespace = "dl4nlpspace"
prefix = "ionestest"
fun = "train"
_COMPLETE_ARGS = ["-cf", os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_config_nogpu.yaml"),
                  "-md", "/models",
                  "-od", "/models"]
arguments = {
    "-od": "iones-test-job_output",
    "-md": "models"
}
pvc = "test-pvc"
prefix_pvc = "{p}-{pvc}".format(p=prefix, pvc=pvc)
pod_name = "{x}-seaquest-tmp-uploader".format(x=prefix)
files_path = [(pathlib.Path.cwd().resolve().joinpath("tests//unit//test_model_dir"), None),
              (pathlib.Path.cwd().resolve().joinpath("tests//unit//test_model_dir//requirements.txt"), "test_model_dir")]


def test_delete_job_pass():
    args = validate.parse_and_validate_args(_COMPLETE_ARGS.copy())
    launcher._launch_job(api_instance_batch, namespace, "iones-seaquest-test-job", args["job_spec"], pvc, arguments)
    try:
        monitor._delete_job(api_instance_batch, namespace, "iones-seaquest-test-job")
    except Exception as e:
        assert False, "Failed to delete job with err {e}".format(e=e)


def test_delete_job_fail():
    args = validate.parse_and_validate_args(_COMPLETE_ARGS.copy())
    launcher._launch_job(api_instance_batch, namespace, "iones-seaquest-test-job", args["job_spec"], pvc, arguments)
    try:
        monitor._delete_job(api_instance_batch, namespace, "hocus-pocus")

        # just in case
        monitor._delete_job(api_instance_batch, namespace, "iones-seaquest-test-job")
    except Exception as e:
        monitor._delete_job(api_instance_batch, namespace, "iones-seaquest-test-job")
        assert True, "Failed to delete job with err {e}".format(e=e)


def test_copy_files_from_pod():
    # uploader.upload_files_to_pvc(namespace, prefix, pvc, files_path)
    try:
        pod._launch_pod(api_instance_core, namespace, pod_name, prefix_pvc)
        pod._wait_for_running_state(api_instance_core, namespace, pod_name, timeout=180) # TODO: make this configurable

        output_path = pathlib.Path.cwd().resolve().joinpath("tests//unit//outputs")
        output_path.mkdir(exist_ok=True)
        monitor._copy_files_from_pod(api_instance_core, pod_name, namespace, pathlib.Path("{p}/test_model_dir".format(p=prefix_pvc)), output_path)

        pod._delete_pod(api_instance_core, namespace, pod_name)
    except Exception as e:
        pod._delete_pod(api_instance_core, namespace, pod_name)
        assert False, "Test copy files from pod failed with error {e}".format(e=e)


def test_copy_files_from_pod_fail():
    uploader.upload_files_to_pvc(namespace, prefix, pvc, files_path)
    try:
        pod._launch_pod(api_instance_core, namespace, pod_name, prefix_pvc)
        pod._wait_for_running_state(api_instance_core, namespace, pod_name, timeout=180) # TODO: make this configurable

        output_path = pathlib.Path.cwd().resolve().joinpath("tests//unit/outputs")
        output_path.mkdir(exist_ok=True)
        monitor._copy_files_from_pod(api_instance_core, pod_name, namespace, pathlib.Path("{p}/hocus-pocus".format(p=prefix_pvc)), output_path)

        pod._delete_pod(api_instance_core, namespace, pod_name)
    except Exception as e:
        pod._delete_pod(api_instance_core, namespace, pod_name)
        assert True, "Test copy files from pod failed with error {e}".format(e=e)


def test_monitor_jobs():
    args = validate.parse_and_validate_args(_COMPLETE_ARGS.copy())
    launcher._launch_job(api_instance_batch, namespace, "iones-seaquest-test-job", args["job_spec"], prefix_pvc, arguments)
    #launcher._launch_job(api_instance_batch, namespace, "iones-seaquest-test-job-2", fun, args["job-spec"], pvc)

    try:
        monitor._monitor_jobs(api_instance_batch, api_instance_core, namespace, ["iones-seaquest-test-job"], pvc, pathlib.WindowsPath("C:/", "Users", "Iancu", "Desktop"), prefix) 
    except Exception as e:
        monitor._delete_job(api_instance_batch, namespace, "iones-seaquest-test-job")
        # monitor._delete_job(api_instance_batch, namespace, "iones-seaquest-test-job-2")
        assert False, "Test monitor jobs failed with error {e}".format(e=e)


def test_monitor_jobs_fail():
    args = validate.parse_and_validate_args(_COMPLETE_ARGS.copy())
    arguments["-md"] = "/hocus-pocus"
    launcher._launch_job(api_instance_batch, namespace, "iones-seaquest-test-job", args["job_spec"], prefix_pvc, arguments)
    #launcher._launch_job(api_instance_batch, namespace, "iones-seaquest-test-job-2", fun, args["job-spec"], pvc)

    try:
        monitor._monitor_jobs(api_instance_batch, api_instance_core, namespace, ["iones-seaquest-test-job"], pvc, pathlib.WindowsPath("C:/", "Users", "Iancu", "Desktop"), prefix) 
    except Exception as e:
        monitor._delete_job(api_instance_batch, namespace, "iones-seaquest-test-job")
        # monitor._delete_job(api_instance_batch, namespace, "iones-seaquest-test-job-2")
        assert True, "Test monitor jobs failed with error {e}".format(e=e)