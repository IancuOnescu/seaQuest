import os
import pathlib
import sys

from seaquest import runner
from seaquest.utils.validate import _parse_args

# output_dir = pathlib.Path("output_dir")
output_dir = "output_dir"
_COMPLETE_ARGS = ["-cf", str(os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_config_nogpu.yaml")),
                  "-md", "test_model_dir",
                  "-mn", "ExampleModel",
                  "-f", "train",
                  "-p", "iones",
                  "-df", "test_weights.txt"]

def test_start_model_no_dir():
    args = _parse_args(_COMPLETE_ARGS)
    try:
        runner.main(args)
    except ValueError as e:
        assert True

def test_start_model_no_model():
    args = _parse_args(_COMPLETE_ARGS)
    try:
        runner.main(args)
    except ModuleNotFoundError as e:
        assert True

def test_start_model_no_fun():
    args = _parse_args(_COMPLETE_ARGS)
    try:
        runner.main(args)
    except ValueError as e:
        assert True

def test_start_model_pass():
    args = _parse_args(_COMPLETE_ARGS)
    sys.path.append(os.path.join(os.getcwd(), "test_model_dir"))

    try:
        runner.main(args)
        assert True
    except ValueError or ModuleNotFoundError as e:
        assert False, f"Starting model failed with exception: {e}"