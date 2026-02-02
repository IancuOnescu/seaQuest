import os
import pathlib
from time import sleep

from kubernetes import client, config

from seaquest import monitor, launcher, uploader
from seaquest.utils import validate

config.load_kube_config()
api_instance_batch = client.BatchV1Api()
api_instance_core = client.CoreV1Api()

namespace = "dl4nlpspace"
prefix = "ionestest"
fun = "train"
_COMPLETE_ARGS = ["-cf", os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_config_nogpu.yaml"),
                  "-md", "/models",
                  "-mn", "resnet",
                  "-f", "train",
                  "-p", "iones"]

# def test_delete_job_pass():
#     #jobs = launcher._launch_job()
#     try:
#         monitor._delete_job(api_instance_batch, namespace, "iones-seaquest-test-job")
#     except Exception as e:
#         assert False, "Failed to delete job with err {e}".format(e=e)


# def test_delete_job_fail():
#     #jobs = launcher._launch_job()
#     try:
#         monitor._delete_job(api_instance_batch, namespace, "hocus-pocus")
#     except Exception as e:
#         assert True, "Failed to delete job with err {e}".format(e=e)


# def test_copy_files_from_pod():
#     uploader._create_pvc(api_instance_core, "test-pvc", namespace, prefix)
#     pod_name = uploader._launch_temp_pod(api_instance_core, "test-pvc", namespace, prefix)
#     uploader._wait_for_running_state(api_instance_core, pod_name, namespace)
    
#     # uploader._copy_files_to_pod(api_instance_core, pod_name, namespace, "/ionestest-test-pvc", pathlib.WindowsPath("P:/", "UIC", "CS582", "homework1", "src"))
    
#     try:
#         # sleep(20)
#         src_path = pathlib.PurePosixPath("ionestest-test-pvc").joinpath("src")
#         monitor._copy_files_from_pod(api_instance_core, pod_name, namespace, src_path, pathlib.WindowsPath("C:/", "Users", "Iancu", "Desktop"))

#         uploader._delete_temp_pod(api_instance_core, namespace, pod_name)
#     except Exception as e:
#         uploader._delete_temp_pod(api_instance_core, namespace, pod_name)
#         assert False, "Test copy files from pod failed with error {e}".format(e=e)


def test_monitor_jobs():
    args = validate.parse_and_validate_args(_COMPLETE_ARGS.copy())
    launcher._launch_job(api_instance_batch, namespace, "iones-seaquest-test-job", fun, args["job-spec"], "ionestest-test-pvc")
    #launcher._launch_job(api_instance_batch, namespace, "iones-seaquest-test-job-2", fun, args["job-spec"], "ionestest-test-pvc")

    try:
        monitor._monitor_jobs(api_instance_batch, api_instance_core, namespace, ["iones-seaquest-test-job"], "test-pvc", pathlib.WindowsPath("C:/", "Users", "Iancu", "Desktop"), "ionestest") 
    except Exception as e:
        monitor._delete_job(api_instance_batch, namespace, "iones-seaquest-test-job")
        # monitor._delete_job(api_instance_batch, namespace, "iones-seaquest-test-job-2")
        assert False, "Test monitor jobs failed with error {e}".format(e=e)