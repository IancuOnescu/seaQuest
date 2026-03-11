import os
from pathlib import Path
from kubernetes import client, config

config.load_kube_config()
api_instance_core = client.CoreV1Api()
api_instance_batch = client.BatchV1Api()

namespace = "dl4nlpspace"
prefix = "ionestest"

pvc_name = "test-pvc"
pvc_name_prefix = "ionestest-test-pvc"

pod_name = "seaquest-test-pod"
pod_name_prefix = "iones-seaquest-test-pod"

pod_wait_timeout = 300 # seconds

config_file_path = Path(Path(__file__).parent.resolve()).joinpath("test_config_nogpu.yaml")
test_model_dir_path = Path(Path(__file__).parent.resolve()).joinpath("test_model_dir")

test_model_name = "ExampleModel"
COMPLETE_ARGS = ["-cf", str(config_file_path),
                  "-md", "test_model_dir",
                  "-mn", test_model_name,
                  "-f", "infer",
                  "-p", "iones",
                  "-df", "test-weights.txt"]

INCOMPLETE_ARGS_1= ["-md", "/models"]
INCOMPLETE_ARGS_2= ["-md", "/models", "-cf", str(config_file_path)]

test_job_name_prefix = "iones-seaquest-test-job"
job_output_dir = "iones-seaquest-test-job_output"
data_file = "test-weights"
job_arguments = {
    "-od": job_output_dir,
    "-md": "test_model_dir"
}

runner_arguments = [
    "-od", "output_dir",
    "-md", "test_model_dir",
    "-cf", "tests\\unit\\test_config_nogpu.yaml"
]
fun = "infer"

output_dir = "output_dir"

