from argparse import ArgumentParser
from cerberus import Validator
import collections.abc
import pathlib
from yaml import safe_load

from .vschema import VALIDATION_SCHEMA


def _update(d: dict, u: dict):
    """merge two dictionaries, keeping the values of second one in case of key collision
    
     Parameters
     ----------
     d: dict
          First dictionary
     u: dict
          Second dictionary

     Returns
     -------
     d: dict
          Merged dictionary
    """
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = _update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def parse_and_validate_args(argv) -> dict:
     """parse and validate the command line arguments

     Parameters
     ----------
     argv: list
          List of command line arguments

     Returns
     -------
     args: dict
          Dictionary of parsed arguments
     """
     args = _parse_args(argv)
     _validate(args)
     return args


def _validate(args: dict) -> bool:
     """validate the parsed arguments
     Check if all the mandatory arguments are provided
     
     Parameters
     ----------
     args: dict
          Dictionary of parsed arguments
     Returns
     -------
     bool
          True if all the mandatory arguments are provided, else raise ValueError
     """
     
     validator = Validator(VALIDATION_SCHEMA)
     validator.validate(args)

     if validator.errors != {}:
          raise KeyError("Not all required arguments have been provided or provided arguments are incorrect: {err}".format(err=validator.errors))

     return True


def _parse_args(argv) -> dict:
     """parse the command line arguments

     Parameters
     ----------
     argv: list
          List of command line arguments
     Returns
     -------
     args: dict
          Dictionary of parsed arguments
     """

     parser = ArgumentParser()

     # required args
     parser.add_argument("-cf", "--config-file", action="store", dest="config_file", required=True, default="./configs/default_job_cfg.yaml", type=str, help="Path to config file")

     # optional args
     parser.add_argument("-lf", "--log-file", action="store", dest="log_file", default="seaquest_logs.logs", required=False, type=str, help="Logging file path")

     parser.add_argument("-md", "--model-data-dir", action="store", dest="md_dir", required=False, type=str, help="Path to directory containing model and data")
     parser.add_argument("-df", "-data-file", action="store", dest="data_file", required=False, type=str, help="Path to file containing the data for the model")
     parser.add_argument("-mn", "--model-name", action="store", dest="model_name", required=False, type=str, help="Name of the model")
     parser.add_argument("-f", "--model-function", action="store", dest="model_fun", required=False, type=str, help="Name of the model function to run", choices=['train', 'infer'])
     parser.add_argument("-p", "--prefix", action="store", dest="prefix", required=False, type=str, help="Prefix to use for naming jobs and other k8s objects")
     parser.add_argument("-s", "--suffix", action="store", dest="suffix", required=False, type=str, help="Suffix to use for naming jobs and other k8s objects")

     cmd_args, _ = parser.parse_known_args(argv)
     config_args = _parse_config_file(pathlib.Path(cmd_args.config_file).resolve())

     return _update(vars(cmd_args), config_args)


def _parse_runner_args(argv) -> dict:
     """parse the command line arguments for the runner

     Parameters
     ----------
     argv: list
          List of command line arguments
     Returns
     -------
     args: dict
          Dictionary of parsed arguments
     """

     parser = ArgumentParser()

     parser.add_argument("-cf", "--config-file", action="store", dest="config_file", required=True, type=str, help="Path to config file")
     
     # parser.add_argument("-md", "--model-data-dir", action="store", dest="model_dir", required=False, type=str, help="Path to directory containing model and data")
     # parser.add_argument("-df", "-data-file", action="store", dest="data_file", required=False, type=str, help="Path to file containing the data for the model")
     # parser.add_argument("-mn", "--model-name", action="store", dest="model_name", required=False, type=str, help="Name of the model")
     # parser.add_argument("-f", "--model-function", action="store", dest="model_fun", required=False, type=str, help="Name of the model function to run", choices=['train', 'infer'])
     parser.add_argument("-od", "--output-dir", action="store", dest="output_dir", required=True, type=str, help="output_dir")

     cmd_args, _ = parser.parse_known_args(argv)
     config_args = _parse_config_file(pathlib.Path(cmd_args.config_file).resolve())

     return _update(vars(cmd_args), config_args)


def _parse_monitor_args(argv) -> dict:
     """parse the command line arguments for the monitor

     Parameters
     ----------
     argv: list
          List of command line arguments
     Returns
     -------
     args: dict
          Dictionary of parsed arguments
     """

     parser = ArgumentParser()

     parser.add_argument("-cf", "--config-file", action="store", dest="config_file", required=False, type=str, help="Path to config file")
     parser.add_argument("-d", "--dest-dir", action="store", dest="dest_dir", required=True, type=str, help="Path to where the output should be saved")
     
     cmd_args, _ = parser.parse_known_args(argv)

     return vars(cmd_args)


def _parse_config_file(file_path: pathlib.Path) -> dict:
     """parse a yaml config file

     Parameters
     ----------
     file_path: str
          Path to the config file

     Returns
     -------
     config: dict
          Dictionary of parsed config file
     """
     with open(file_path, 'r') as f:
          config = safe_load(f)

     return config