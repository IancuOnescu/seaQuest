from abc import ABC, abstractmethod
import os
import pathlib


class OutputContext:
    """Class that handles the context switch for saving output files on the PVC"""

    def __init__(self, output_dir: pathlib.Path):
        self.output_dir = output_dir

    def __enter__(self):
        """"""
        self.curr_wd = os.getcwd()
        os.chdir(self.output_dir) # .resolve())

        return self

    def __exit__(self, exc_type, exc_value, traceback):
       """"""
       os.chdir(self.curr_wd)


class NautPipelineModel(ABC):
    """Base class to be inherited by all models to ensure minimum required constructor arguments and methods"""
    def __init__(self, output_dir: pathlib.Path, data_file: pathlib.Path):
        super().__init__()

        self.output_dir = output_dir
        self.data_file = data_file

    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def infer(self):
        pass