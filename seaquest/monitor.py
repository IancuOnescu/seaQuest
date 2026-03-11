import pathlib
import sys
import tarfile
from tempfile import TemporaryFile
from time import sleep
from yaml import safe_load

from kubernetes import client, config, stream

from .utils.loggus import init_logger
from .utils.validate import _parse_monitor_args
from .utils.pod import _launch_pod, _delete_pod, _wait_for_running_state, make_pod_name_unique

config.load_kube_config()
logger = init_logger(__name__ if __name__ != "__main__" else pathlib.Path(__file__).stem, level="debug")


def _delete_pvc(api_instance: client.V1Affinity, pvc: str,) -> None:
    """"""

    api_instance.delete_persistent_volume(pvc)


def _delete_job(api_instance: client.BatchV1Api, namespace: str, job_name: str) -> None:
    """"""

    api_instance.delete_namespaced_job(name=job_name, namespace=namespace, propagation_policy='Foreground')


def _delete_all_jobs(api_instance: client.BatchV1Api, namespace: str, job_names: str) -> None:
    """"""

    for job in job_names:
        try:
            _delete_job(api_instance, namespace, job)
        except:
            logger.error("Couldn't delete job {job}, please delete it manually!".format(job=job))


def _monitor_jobs(api_instance_batch: client.BatchV1Api, api_instance_core: client.CoreV1Api, namespace: str, job_names: list, pvc: str, dest_dir: pathlib.Path, prefix: str) -> None:
    """"""
    
    # Watch and streaming solutions didn't work so we use this for now ): 
    # (this snippet is also present in the official examples)
    logger.info("Started monitoring jobs!")
    logger.debug("Monitored jobs: {jobs}".format(jobs=" ".join(job_names)))

    jobs_done = [False] * len(job_names)

    while True:
        for idx, job in enumerate(job_names):

            if jobs_done[idx]:
                continue
            
            resp = None
            try:
                resp = api_instance_batch.read_namespaced_job_status(name=job, namespace=namespace)
            except Exception as e:
                jobs_done[idx] = True
                logger.info("Monitoring for job {job} has failed with error: {err}".format(job=job, err=e))
                continue

            if resp.status.succeeded:
                _pull_files(api_instance_core, namespace, prefix, job, pvc, dest_dir)
                stat = "Succeeded"

            elif resp.status.failed:
                stat = "Failed"

            elif not resp.status.active or resp.status.active > 0:
                continue # still initiating or running
            
            jobs_done[idx] = True
            logger.info("Job {job} has finished with status `{stat}`".format(job=job, stat=stat))
            _delete_job(api_instance_batch, namespace, job)

            sleep(1)

        if all(jobs_done) == True:
            logger.info("All jobs are done! Results from successful jobs have been pulled to {dir}".format(dir=str(dest_dir)))
            return
        
        sleep(60)


def _pull_files(api_instance: client.CoreV1Api, namespace:str, prefix: str, job_name:str, pvc: str, dest_dir: str) -> None:
    """"""
    
    logger.info("Pulling output of job {job} ...".format(job=job_name))

    pvc_name = "{x}-{y}".format(x=prefix, y=pvc) if prefix else pvc
    pod_name = "{x}-seaquest-tmp-uploader".format(x=prefix)
    pod_name = make_pod_name_unique(api_instance, namespace, pod_name)

    _launch_pod(api_instance, namespace, pod_name, pvc_name)
    _wait_for_running_state(api_instance, namespace, pod_name, timeout=120) # TODO: make this configurable

    files_path = pathlib.Path("{p}-{pvc}".format(p=prefix, pvc=pvc)).joinpath("{job}_output".format(job=job_name))

    try:
        _copy_files_from_pod(api_instance, pod_name, namespace, files_path, dest_dir)
        _delete_pod(api_instance, namespace, pod_name)
    except Exception as e:
        _delete_pod(api_instance, namespace, pod_name)
        logger.error("Copy files for job {job} has failed with error {err}".format(job=job_name, err=e))


# https://github.com/prafull01/Kubernetes-Utilities/blob/master/kubectl_cp_as_python_client.py
# They should really make a cp method already ):
def _copy_files_from_pod(api_instance: client.CoreV1Api, pod_name: str, namespace: str, src_path: pathlib.Path, dest_dir: pathlib.Path):
    """"""

    logger.info("Starting to copy files from kube storage through pod {pod}".format(pod=pod_name))
    exec_command = ['tar', 'czf', '-', src_path.as_posix()] # for some reason cd-ing and then tar-ing does not return any std output

    with TemporaryFile() as tar_buffer:
        resp = stream.stream(api_instance.connect_get_namespaced_pod_exec, pod_name, namespace,
                      command=exec_command,
                      binary=True,
                      stderr=True, stdin=True,
                      stdout=True, tty=False,
                      _preload_content=False)

        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                out = resp.read_stdout()
                logger.info("Got {num} bytes".format(num=len(out)))
                tar_buffer.write(out)
            if resp.peek_stderr():
                logger.error("STDERR: %s" % resp.read_stderr().decode('utf-8'))
        resp.close()

        tar_buffer.flush()
        tar_buffer.seek(0)

        with tarfile.open(fileobj=tar_buffer, mode='r:gz') as tar:
            subdir_and_files = [
                tarinfo for tarinfo in tar.getmembers()
            ]
            tar.extractall(path=dest_dir, members=subdir_and_files)

    logger.info("Files pulled to {dest}".format(dest=str(dest_dir)))


def _load_config():
    """"""
    PATH_MAPPING = {
        "linux": "./config",
        "darwin": "Library/Preferences/seaquest",
        "win32": "AppData/Local/seaquest",
    }

    file_path = pathlib.Path(pathlib.Path.home()).joinpath(PATH_MAPPING[str(sys.platform).lower()]) 
    file_path.mkdir(parents=True, exist_ok=True)
    file_path = file_path / "seaquest.yaml" 

    with open(file_path, "r") as file:
        args = safe_load(file)

    return args


if __name__ == "__main__":
    # check system arguments
    passed_args = _parse_monitor_args(sys.argv)
    dest_dir = pathlib.Path(passed_args["dest_dir"]).resolve()

    # load config file from default location if not specified
    if "config_file" not in passed_args:
        saved_args = _load_config()
    else:
        with open(passed_args["config_file"], "r") as file:
            saved_args = safe_load(file)

    # if config file found run start monitoring jobs
    api_instance_batch = client.BatchV1Api()
    api_instance_core = client.CoreV1Api()

    _monitor_jobs(api_instance_batch, api_instance_core, saved_args["kube_env"]["namespace"], saved_args["launched_jobs"], saved_args["pvc_params"]["pvc-name"], dest_dir, saved_args["prefix"])