import pathlib
import sys
import os

from kubernetes import client, config
from yaml import safe_dump

from seaquest import uploader, launcher
from seaquest.utils import validate, loggus, pod

config.load_kube_config()
logger = loggus.init_logger(__name__ if __name__ != "__main__" else pathlib.Path(__file__).stem)


def _generate_runner_config(args: dict) -> pathlib.Path:
    """generate and save the runner config file
    
    Parameters
    ----------
    args: dict
        Dictionary of parsed arguments
    Returns
    -------
    file_path: pathlib.Path
        Path to the location where the runner configuration is saved
    """
    dir = pathlib.Path(args["md_dir"]).resolve()

    file_path = dir / "runner.yaml"
    args_cp = args.copy()
    args_cp["md_dir"] = "_".join([dir.name, pathlib.Path(args["data_file"]).stem])
    args_cp["data_file"] = pathlib.Path(args["data_file"]).name
    with open(file_path, "w") as file:
        safe_dump(args_cp, file)

    return file_path


def _delete_runner_config(path: pathlib.Path) -> None:
    """remove the generated runner config file

    Parameters
    ----------
    path: pathlib.Path
        Path to the location where the runner configuration is saved
    Returns
    -------
    None
    """
    os.remove(path)


def _upload_files(args: dict) -> None:
    """upload the model directory and the data file to the PVC.

    Parameters
    ----------
    args: dict
        Dictionary of parsed arguments
    Returns
    -------
    None
    """
    pvc_name = args["pvc_params"]["pvc-name"] if "pvc_params" in args \
            else "seaquest-pvc"
    
    files = [(pathlib.Path(args["md_dir"]).resolve(), None), 
             (pathlib.Path(args["data_file"]).resolve(), pathlib.Path(args["md_dir"]).resolve().name)]
    try:
        pvc_name = uploader.upload_files_to_pvc(args["kube_env"]["namespace"], args["prefix"], pvc_name, \
                                    files)

    except Exception as e:
        logger.error("Could not upload the model and data to the pvc! Error: {e}".format(e=e))
        raise e
    
    return pvc_name


def _launch_jobs(args: dict, pvc_name: str) -> None:
    """launch the experimental jobs

    Parameters
    ----------
    args: dict
        Dictionary of parsed arguments
    pvc_name: str
        Name of PVC to mount
    Returns
    -------
    None
    """
    data_file = pathlib.Path(args["data_file"]).stem
    model_dir = "_".join([pathlib.Path(args["md_dir"]).name, data_file])

    api_instance = api_instance = client.BatchV1Api()
    try:
        all_created_jobs = launcher.create_jobs(api_instance, 1, args["kube_env"]["namespace"], args["job_spec"], args["prefix"], \
                            args["suffix"], args["model_name"], args["model_fun"], pvc_name, model_dir, data_file)
    except Exception as e:
        logger.error("Could not launch jobs!".format(e=e))
        raise e

    return all_created_jobs


def _save_config_and_jobs(args: dict) -> None:
    """save a file containing the names of the launched jobs to feed to the monitor module

    Parameters
    ----------
    args: dict
        Dictionary of parsed arguments
    Returns
    -------
    None
    """
    PATH_MAPPING = {
        "linux": "./config",
        "darwin": "Library/Preferences/seaquest",
        "win32": "AppData/Local/seaquest",
    }

    file_path = pathlib.Path(pathlib.Path.home()).joinpath(PATH_MAPPING[str(sys.platform).lower()]) 
    file_path.mkdir(parents=True, exist_ok=True)
    file_path = file_path / "seaquest.yaml" 
    
    with open(file_path, "w") as file:
        safe_dump(args, file)


def main(argv):
    """parse arguments, create a runner config, upload the model and data, launch the jobs save the names of the launched jobs.

    Parameters
    ----------
    argv: list
        List of arguments passed to the module
    Returns
    -------
    None
    """
    args = validate.parse_and_validate_args(argv)
    logger.info("Arguments parsed and validated succesfully!")

    rc_path = _generate_runner_config(args)
    pvc_name = _upload_files(args)
    _delete_runner_config(rc_path)

    all_created_jobs = _launch_jobs(args, pvc_name)

    all_created_jobs = ["iones-llama3infer-infer-job-0"]

    # save the output to a file: config used and jobs
    args["launched_jobs"] = all_created_jobs
    _save_config_and_jobs(args)


if __name__ == "__main__":
    main(sys.argv)