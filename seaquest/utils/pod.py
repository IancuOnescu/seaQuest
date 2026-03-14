from random import randint
from time import sleep

from kubernetes import client

from .loggus import init_logger

logger = init_logger(__name__, level="debug")


def make_pod_name_unique(api_instance: client.CoreV1Api, namespace: str, pod_name: str) -> str:
     """Make pod name unique by appending a random number if a pod with the same name exists
     Parameters
     ----------
     api_instance: kubernetes client
          Kubernetes client
     namespace: str
          Namespace to get pods from
     pod_name: str
          Desired pod name
     Returns
     -------
     str
          Unique pod name
     """
     all_pod_names = _get_list_of_pods(api_instance, namespace)
     pod_name = "{pod}-{rand}".format(pod=pod_name, rand=randint(1000, 9999))
     while pod_name in all_pod_names:    
          pod_name = "{pod}-{rand}".format(pod=pod_name, rand=randint(1000, 9999))

     return pod_name


def _get_list_of_pods(api_instance: client.CoreV1Api, namespace: str) -> list[str]:
     """Get list of pod names in a namespace

     Parameters
     ----------
     api_instance: kubernetes client
          Kubernetes client
     namespace: str
          Namespace to get pods from

     Returns
     -------
     list
          List of pod names
     """
     pods = api_instance.list_namespaced_pod(namespace=namespace)
     pod_names = [pod.metadata.name for pod in pods.items]
     return pod_names


def _launch_pod(api_instance: client.CoreV1Api, namespace: str, pod_name:str, pvc_name: str) -> None:
     """Launch a pod that will be quickly deleted after the operations are done

     Parameters
     ----------
     api_instance: kubernetes client
          Kubernetes client
     namespace: str
          Namespace to use for creating pod
     pod_name: str
          Name of pod
     pvc_name: str
          Name of pvc to bind the pod to

     Returns
     -------
     None
     """

     body = client.V1Pod(
          api_version="v1",
          kind="Pod",
          metadata=client.V1ObjectMeta(name=pod_name, namespace=namespace),
          spec=client.V1PodSpec(
               containers=[
                    client.V1Container(
                    name="alpine",
                    image="alpine:latest",
                    command=['tail', '-f', '/dev/null'],
                    volume_mounts=[client.V1VolumeMount(mount_path="/{x}".format(x=pvc_name), name=pvc_name)]
                    )
               ],
               volumes=[client.V1Volume(name=pvc_name, persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name))],
          )
     )

     api_instance.create_namespaced_pod(namespace, body)

     logger.info("Succesfully created pod {pod}".format(pod=pod_name))


def _delete_pod(api_instance: client.CoreV1Api, namespace: str, pod_name: str) -> None:
     """Delete the temporary pod used to upload files to the pvc

     Parameters
     ----------
     api_instance: kubernetes client
          Kubernetes client
     namespace: str
          Namespace to use for creating pvc
     pod_name: str
          Name of the pod to delete

     Returns
     -------
     None
          None
     """
     all_pods = _get_list_of_pods(api_instance, namespace)
     if pod_name not in all_pods:
          logger.warning(f"Pod {pod_name} not found in namespace {namespace}. Skipping deletion.")
          return

     api_instance.delete_namespaced_pod(name=pod_name, namespace=namespace)

     logger.info("Successfully deleted pod {pod}.".format(pod=pod_name))


def _is_running(api_instance: client.CoreV1Api, pod_name: str, namespace: str, timeout: int) -> bool:
     """Check if the pod is done initializing and is running

     Parameters
     ----------
     api_instance: kubernetes client
          Kubernetes client
     pod_name: str
          Name of the pod to check
     namespace: str
          Namespace to use for creating pvc
     timeout: int
          Time to wait for pod to reach running state until raising error 

     Returns
     -------
     bool
          True if the pod is done initializing, False otherwise
     """

     # Watch and streaming solutions didn't work so we use this for now ): 
     # (this snippet is also present in the official examples)
     # decorators for timeout didn't work because function is unpicklable
     while True:
          resp = api_instance.read_namespaced_pod(name=pod_name, namespace=namespace)
          if resp.status.phase == 'Running':
               return True
          sleep(1)
          
          timeout -= 1
          if timeout == 0:
               raise TimeoutError("Timeout waiting for pod to be in running state.")


def _wait_for_running_state(api_instance: client.CoreV1Api, namespace: str, pod_name: str, timeout: int) -> bool:
     """Wait for the pod to be in running state, else timeout after 60 seconds

     Parameters
     ----------
     api_instance: kubernetes client
          Kubernetes client
     namespace: str
          Namespace to use for creating pvc
     pod_name: str
          Name of the pod to check
     timeout:
          Time to wait for pod to reach running state until raising error      
     
     Returns
     -------
     bool
          True if the pod is done initializing, else raise TimeoutError
     """
     try:
          _is_running(api_instance, pod_name, namespace, timeout)
     except TimeoutError:
          logger.error("Timeout error: Pod {pod} failed to start in {t} seconds".format(pod=pod_name, t=timeout))
          raise TimeoutError(f"Pod {pod_name} failed to start.")