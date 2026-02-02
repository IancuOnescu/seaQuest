import os
import pathlib

from kubernetes import client, config

from seaquest import launcher, uploader
from seaquest.monitor import _delete_job
from seaquest.utils import validate, loggus

logger = loggus.init_logger(__name__)

config.load_kube_config()
api_instance = client.BatchV1Api()

namespace = "dl4nlpspace"
prefix = "ionestest"
fun = "train"
_COMPLETE_ARGS = ["-cf", os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_config_nogpu.yaml"),
                  "-md", "test_model_dir",
                  "-mn", "ExampleModel",
                  "-f", "train",
                  "-p", "iones",
                  "-df", "test_weights.txt"]

output_dir = "iones-seaquest-test-job_output"
data_file = "test_weights.txt"
arguments = {
    "-od": output_dir,
    "-md": "test_model_dir"
}


def test_launch_job_fail():
    args = validate._parse_args(_COMPLETE_ARGS.copy())
    try:
        launcher._launch_job(api_instance, "nonexisting-namespace", "iones-seaquest-test-job", args["job_spec"], "ionestest-test-pvc", arguments)
    except Exception as e:
        assert True


def test_launch_job():
    args = validate._parse_args(_COMPLETE_ARGS.copy())
    args["output_dir"] = output_dir # workaround
    try:
        uploader.upload_files_to_pvc(namespace, prefix, "test-pvc", [pathlib.Path("P:\\research\\seaQuest\\tests\\unit\\test_model_dir")])
        
        arguments["-od"] = output_dir
        logger.info(arguments)
        launcher._launch_job(api_instance, namespace, "iones-seaquest-test-job", args["job_spec"], "ionestest-test-pvc", arguments)
        #_delete_job(api_instance, namespace, "iones-seaquest-test-job")
    except Exception as e:
        _delete_job(api_instance, namespace, "iones-seaquest-test-job")
        assert False, "Job launch failed with error {e}".format(e=e)


# def test_create_jobs():
#     pass    