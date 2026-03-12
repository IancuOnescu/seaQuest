import os
from pathlib import Path
from kubernetes import client, config

config.load_kube_config()
api_instance_core = client.CoreV1Api()
api_instance_batch = client.BatchV1Api()

namespace = "dl4nlpspace"
prefix = "iones"

pvc_name = "test-pvc"
pvc_name_prefix = "iones-test-pvc"

pod_name = "seaquest-test-pod"
pod_name_prefix = "iones-seaquest-test-pod"

pod_wait_timeout = 300 # seconds

config_file_path = Path(Path(__file__).parent.resolve()).joinpath("test_config_nogpu.yaml")
test_model_dir_path = Path(Path(__file__).parent.resolve()).joinpath("test_model_dir")
data_file_path = Path(Path(__file__).parent.resolve()).joinpath("test_model_dir").joinpath("test-weights.txt")

test_model_name = "ExampleModel"
COMPLETE_ARGS = ["-cf", str(config_file_path),
                  "-md", str(test_model_dir_path),
                  "-mn", test_model_name,
                  "-f", "infer",
                  "-p", "iones",
                  "-df", str(data_file_path)]

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

