import pathlib

from seaquest import experiment, monitor, uploader
from seaquest.utils import validate

from test_vars import *

def cleanup():
    args = validate._parse_args(COMPLETE_ARGS.copy())

    job_name = "{prefix}-{model}-{fun}-{data_file}-job{suffix}-{idx}".format(prefix=prefix, model=args["model_name"], fun=args["model_fun"], idx=0, data_file=data_file, suffix="")
    job_name = job_name.lower()
    monitor._delete_job(api_instance_batch, namespace, job_name)
    uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)


def test_upload_files():
    try:
        args = validate._parse_args(COMPLETE_ARGS.copy())

        experiment._upload_files(args)
        uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)
    except Exception as e:
        uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)
        assert False, "[experiment] upload_files failed with error: {e}".format(e=e)


def test_launch_jobs():
    try:
        args = validate._parse_args(COMPLETE_ARGS.copy())

        experiment._launch_jobs(args, pvc_name_prefix)
        cleanup()
    except Exception as e:
        cleanup()
        assert False, "[experiment] upload_files failed with error: {e}".format(e=e)


def test_main_func():
    try:
        experiment.main(COMPLETE_ARGS.copy())
        cleanup()
    except Exception as e:
        cleanup()
        assert False, "[experiment] upload_files failed with error: {e}".format(e=e)