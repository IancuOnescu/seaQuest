import io
import pathlib
import tarfile
from random import randint

from kubernetes import client, stream

from .utils import pod
from .utils.loggus import init_logger


logger = init_logger(__name__ if __name__ != "__main__" else pathlib.Path(__file__).stem, level="debug")


def _create_pvc(api_instance: client.CoreV1Api, namespace: str, pvc_name: str) -> None:
    """Create a persistent volume claim (pvc) if it does not exist
    
    Parameters
    ----------
     api_instance: kubernetes client
          Kubernetes client
     namespace: str
          Kubernetes Namespace
     pvc_name: str
          Name used in the creation of the pvc
    
    Returns
    -------
    None
         None
    """
    # check if pvc already exists
    pvcs = api_instance.list_namespaced_persistent_volume_claim(namespace=namespace)
    for pvc in pvcs.items:
        if pvc.metadata.name == pvc_name:
            logger.info(f"PVC {pvc_name} already exists in namespace {namespace}. Skipping creation.")
            return
        
    # create pvc
    logger.info("Creating PVC {pvc} in namespace {namespace}.".format(pvc=pvc_name, namespace=namespace))

    body = client.V1PersistentVolume(
        api_version="v1",
        kind="PersistentVolumeClaim",
        metadata=client.V1ObjectMeta(name=pvc, namespace=namespace),
        spec=client.V1PersistentVolumeClaimSpec(
            access_modes=["ReadWriteMany"],
            resources=client.V1ResourceRequirements(requests={"storage": "100Gi"}), #TODO: make this configurable
            storage_class_name="rook-cephfs", #TODO: make this configurable
        )
    )
    api_instance.create_namespaced_persistent_volume_claim(namespace=namespace, body=body)


# taken from https://github.com/kubernetes-client/python/issues/476
# I don't know why there isn't a built-in function for this yet
def _copy_files_to_pod(api_instance: client.CoreV1Api, namespace: str, pod_name: str, source_path: pathlib.Path, dest_path: pathlib.Path) -> None:
     """Copy files to the temporary pod

     Parameters
     ----------
     api_instance: kubernetes client
          Kubernetes client
     namespace: str
          Namespace to use for creating pvc
     pod_name: str
          Name of the pod to copy files to
     source_path: pathlib.Path
          Path to the files to copy
     dest_path: pathlib.Path
          Mount path of the pvc in the pod

     Returns
     -------
     None
          None"""
     buf = io.BytesIO()
     with tarfile.open(fileobj=buf, mode='w:tar') as tar:  # To compress set 'w:gz'
          tar.add(source_path, arcname=dest_path.joinpath(source_path.name))
     buf.seek(0)

     exec_command = ['tar', 'xvf', '-', '-C', '/']   # To decompress set 'xzvf'
     resp = stream.stream(api_instance.connect_get_namespaced_pod_exec, pod_name, namespace,
                         command=exec_command,
                         stderr=True, stdin=True,
                         stdout=True, tty=False,
                         _preload_content=False)

     # copy data to pod in chunks to avoid issues with larger files
     chunk_size = 10 * 1024 * 1024
     while resp.is_open():
          resp.update(timeout=1)
          # if resp.peek_stdout():
          # logger.debug(f"STDOUT: {resp.read_stdout()}")
          if resp.peek_stderr():
               logger.error(f"STDERR: {resp.read_stderr()}")
               raise RuntimeError(f"Error copying files to pod: {resp.read_stderr()}")
          if read := buf.read(chunk_size):
               logger.debug(f"Uploading chunk: {read}")
               resp.write_stdin(read)
          else:
               break
     resp.close()

     logger.info("Files succesfully transfered to kube pvc!")


def _update_file_dest_name(api_instance: client.CoreV1Api, namespace: str, pod_name: str, old_name: pathlib.Path, new_name: pathlib.Path) -> None:
     """Copy files to the temporary pod

     Parameters
     ----------
     api_instance: kubernetes client
          Kubernetes client
     namespace: str
          Namespace to use for creating pvc
     pod_name: str
          Name of the pod to copy files to
     old_name: str
          Name of the directory where the files have been copied
     new_name: str
          Name of the new directory

     Returns
     -------
     None
          None"""

     exec_command = ["/bin/sh", "-c", 'mv {o} {n}'.format(o=old_name, n=new_name)]
     resp = stream.stream(api_instance.connect_get_namespaced_pod_exec, pod_name, namespace,
                         command=exec_command,
                         stderr=True, stdin=True,
                         stdout=True, tty=False,
                         _preload_content=False)

     while resp.is_open():
          resp.update(timeout=1)
          if resp.peek_stdout():
               print(f"STDOUT: \n{resp.read_stdout()}")
          if resp.peek_stderr():
               print(f"STDERR: \n{resp.read_stderr()}")

     resp.close()

     logger.info("Files directory successfully renamed to avoid conflicts!")


def upload_files_to_pvc(namespace: str, prefix: str, pvc: str, files_path: list[(pathlib.Path, pathlib.Path)]) -> str:
     """Upload model and data files to the pvc
     Parameters
     ----------
     kube: kubernetes client
          Kubernetes client
     pvc: str
          Name of pvc to use for data and model storage
     namespace: str
          Namespace to use for creating pvc
     Returns
     -------
     None
          None
     """
     api_instance = client.CoreV1Api()
     
     pvc_name = "{x}-{y}".format(x=prefix, y=pvc) if prefix else pvc
     pod_name = "{x}-seaquest-tmp-uploader".format(x=prefix)
     pod_name = pod.make_pod_name_unique(api_instance, namespace, pod_name)

     try:
          _create_pvc(api_instance, namespace, pvc_name)

          logger.info("Creating pod to move data to pvc ...")
          pod._launch_pod(api_instance, namespace, pod_name, pvc_name)

          pod._wait_for_running_state(api_instance, namespace, pod_name, 120) #TODO: make this configurable

          logger.info("Attempting to upload files to pvc ...")
          for (file_path, dest_dir) in files_path:
               dest_path = pathlib.PurePosixPath(pvc_name)
               if dest_dir is not None:
                   dest_path = dest_path.joinpath(dest_dir)
               _copy_files_to_pod(api_instance, namespace, pod_name, file_path, dest_path)

          # change dir name to avoid conflicts in case of multiple jobs with the same model and different config (e.g. different data files)
          # model_dir in _generate_runner_config should also be changed if this part changes

          new_name = pathlib.PurePosixPath(pvc_name).joinpath("_".join([files_path[1][1], files_path[1][0].stem]))
          _update_file_dest_name(api_instance, namespace, pod_name, dest_path, new_name)

     except Exception as e: # TODO: handle stuff here
          pod._delete_pod(api_instance, namespace, pod_name)
          logger.error(e)
          raise e

     pod._delete_pod(api_instance, namespace, pod_name)

     return pvc_name
