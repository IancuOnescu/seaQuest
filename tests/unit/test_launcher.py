from time import sleep

from seaquest import launcher, uploader
from seaquest.monitor import _delete_job
from seaquest.utils import validate
from test_vars import *


def test_launch_job_fail():
    args = validate._parse_args(COMPLETE_ARGS.copy())
    try:
        launcher._launch_job(api_instance_batch, "hocus-pocus-namespace", test_job_name_prefix, args["job_spec"], pvc_name_prefix, job_arguments)
    except Exception as e:
        pass


def test_launch_job():
    args = validate._parse_args(COMPLETE_ARGS.copy())
    args["output_dir"] = job_output_dir # workaround
    try:
        # uploader.upload_files_to_pvc(namespace, prefix, pvc_name, [ \
        #         [test_model_dir_path, None],
        #         [config_file_path, test_model_dir_path.name]
        #     ])
        
        launcher._launch_job(api_instance_batch, namespace, test_job_name_prefix, args["job_spec"], pvc_name_prefix, job_arguments)
        _delete_job(api_instance_batch, namespace, test_job_name_prefix)
        
        # uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)
        # sleep(5) # for deletion changes to take effect
    except Exception as e:
        # uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)
        _delete_job(api_instance_batch, namespace, test_job_name_prefix)
        assert False, "Job launch failed with error {e}".format(e=e)


def test_create_jobs():
    args = validate._parse_args(COMPLETE_ARGS.copy())
    args["output_dir"] = job_output_dir # workaround
    try:
        uploader.upload_files_to_pvc(namespace, prefix, pvc_name, [ \
                [test_model_dir_path, None],
                [config_file_path, test_model_dir_path.name]
            ])
        launcher.create_jobs(api_instance_batch, 1, namespace, args["job_spec"], prefix, None, args["model_name"], args["model_fun"], pvc_name_prefix, args["md_dir"], data_file)

        job_name = "{prefix}-{model}-{fun}-{data_file}-job{suffix}-{idx}".format(prefix=prefix, model=args["model_name"], fun=args["model_fun"], idx=0, data_file=data_file, suffix="")
        job_name = job_name.lower()
        _delete_job(api_instance_batch, namespace, job_name)
        uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)
    except Exception as e:
        uploader._delete_pvc(api_instance_core, namespace, pvc_name_prefix)

        job_name = "{prefix}-{model}-{fun}-{data_file}-job{suffix}-{idx}".format(prefix=prefix, model=args["model_name"], fun=args["model_fun"], idx=0, data_file=data_file, suffix="")
        job_name = job_name.lower()
        _delete_job(api_instance_batch, namespace, job_name)
        assert False, "Job launch failed with error {e}".format(e=e)
    