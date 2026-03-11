from seaquest import runner
from seaquest.utils.validate import _parse_args, _parse_runner_args
from test_vars import *


def test_load_model_dir_pass():
    try:
        runner._load_model_dir(test_model_dir_path.name)
    except:
        assert False, "Model dir failed to load"


def test_load_model_dir_fail():
    try:
        runner._load_model_dir("nonexistent_path")
    except:
        pass


def test_load_model_class_pass():
    try:
        namespace = runner._load_model_dir(test_model_dir_path.name)
        runner._load_model_class(namespace, test_model_name)
    except:
        assert False, "Model class failed to load"


def test_load_model_class_fail():
    try:
        runner._load_model_class(None, test_model_name)
    except:
        pass


def test_main():
    args = _parse_args(COMPLETE_ARGS.copy())
    args_runner = _parse_runner_args(runner_arguments)

    args.update(args_runner)
    try:
        runner.main(args)
    except Exception as e:
        assert False, "Main function from runner failed to run: {e}".format(e=e)
    
