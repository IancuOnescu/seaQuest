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

