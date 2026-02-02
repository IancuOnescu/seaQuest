import os

from seaquest.utils import validate

_COMPLETE_ARGS = ["-cf", os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_config_nogpu.yaml"),
                  "-md", "/models",
                  "-mn", "resnet",
                  "-f", "train",
                  "-p", "iones",
                  "-df", "data_path"]

_INCOMPLETE_ARGS_1= ["-md", "/models"]
_INCOMPLETE_ARGS_2= ["-md", "/models", "-cf", os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_config_nogpu.yaml"),]


def test_parse_args():
    args = validate._parse_args(_COMPLETE_ARGS.copy())

    assert args["config_file"] == os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_config_nogpu.yaml")
    assert args["md_dir"] == "/models"
    assert args["model_name"] == "resnet"
    assert args["model_fun"] == "train"
    assert args["prefix"] == "iones" 
    assert args["data_file"] == "data_path"


def test_parse_args_fail():
    try:
        validate._parse_args(_INCOMPLETE_ARGS_1.copy())
    except:
        assert True


def test_validate_complete_args():
    args = validate._parse_args(_COMPLETE_ARGS.copy())
    assert validate._validate(args) is True


def test_validate_incomplete_args():
    args = validate._parse_args(_INCOMPLETE_ARGS_2.copy())
    try:
        validate._validate(args)
    except Exception as e:
        assert True