import os
from pathlib import Path
from kubernetes import client, config

config.load_kube_config()
api_instance_core = client.CoreV1Api()
api_instance_batch = client.CoreV1Api()

namespace = "dl4nlpspace"
prefix = "ionestest"

pvc_name = "test-pvc"
pvc_name_prefix = "ionestest-test-pvc"

pod_name = "seaquest-test-pod"
pod_name_prefix = "iones-seaquest-test-pod"

pod_wait_timeout = 300 # seconds

config_file_path = Path(Path(__file__).parent.resolve()).joinpath("test_config_nogpu.yaml")
test_model_dir_path = Path(Path(__file__).parent.resolve()).joinpath("test_model_dir")

COMPLETE_ARGS = ["-cf", str(config_file_path),
                  "-md", "/models",
                  "-mn", "ExampleModel",
                  "-f", "infer",
                  "-p", "iones",
                  "-df", "tests/unit/test_config_nogpu.yaml"]

INCOMPLETE_ARGS_1= ["-md", "/models"]
INCOMPLETE_ARGS_2= ["-md", "/models", "-cf", str(config_file_path)]

