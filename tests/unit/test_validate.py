import os

from seaquest.utils import validate
from test_vars import *

def test_parse_args():
    args = validate._parse_args(COMPLETE_ARGS.copy())

    assert args["config_file"] == COMPLETE_ARGS[1]
    assert args["md_dir"] == COMPLETE_ARGS[3]
    assert args["model_name"] == COMPLETE_ARGS[5]
    assert args["model_fun"] == COMPLETE_ARGS[7]
    assert args["prefix"] == COMPLETE_ARGS[9]
    assert args["data_file"] == COMPLETE_ARGS[11]


def test_parse_args_fail():
    try:
        validate._parse_args(INCOMPLETE_ARGS_1.copy())
    except:
        assert True


def test_validate_complete_args():
    args = validate._parse_args(COMPLETE_ARGS.copy())
    assert validate._validate(args) is True


def test_validate_incomplete_args():
    args = validate._parse_args(INCOMPLETE_ARGS_2.copy())
    try:
        validate._validate(args)
    except Exception as e:
        assert True