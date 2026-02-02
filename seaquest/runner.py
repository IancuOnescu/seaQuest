from importlib import import_module
import os
import pathlib
import pkgutil
import sys


from seaquest.utils.loggus import init_logger
from seaquest.utils.validate import _parse_runner_args

logger = init_logger(__name__ if __name__ != "__main__" else pathlib.Path(__file__).stem, level="debug")


def _load_model_dir(model_dir):
    """"""

    logger.info("Attempting to load model directory ...")
    try:
        namespace = import_module(model_dir)
    except ModuleNotFoundError as e:
        raise ValueError(f"Model directory '{model_dir}' or one of its imports not found or is not a module!") from e

    logger.info("Model directory successfully loaded!")
    return namespace


def _load_model_class(namespace, model_name):
    """"""

    logger.info("Attempting to load model class ...")
    subpackages = [name for _, name, _ in list(pkgutil.iter_modules(
        namespace.__path__,
        namespace.__name__ + "."
    ))]
    
    # find the model and load it
    found_model = False
    for subp in subpackages:
        try:
            imp_subp = import_module(subp)
            model = getattr(imp_subp, model_name)
            found_model = True
        except ModuleNotFoundError as e:
            pass
        except AttributeError as e:
            pass

    if found_model is False:
        raise ModuleNotFoundError(f"Module '{model_name}' not found in directory {namespace.__name__}")
    logger.info(f"Successfully imported model '{model_name}' from directory '{namespace.__name__}'")

    return model


def _load_model_function(model, fun):
    callable = getattr(model, fun, None)
    if callable is None:
        raise ValueError(f"Function '{fun}' not found in model '{model.__name__}'")

    return callable


def main(args: dict) -> None:
    """Dynamically imports and runs a specified function from a model class.
    
    Parameters:
    -----------
        model_name: str 
            Name of the model to import.
        model_dir: str 
            Directory where the model is located.
        data_dir: str 
            Directory containing the data for training or inference.
        output_dir: str 
            Directory where the output should be stored.
        fun:
          str Function to execute from the model class ('train' or 'infer').
    
    Returns:
    --------
        None
    
    Raises:
    -------
        ValueError: If the model or function cannot be found.
    """

    output_dir = pathlib.Path(args["output_dir"]) # .resolve()
    model_dir = pathlib.Path(pathlib.Path.cwd() / args["md_dir"])
    data_file = pathlib.Path(args["data_file"])
    sys.path.insert(0, str(model_dir.parent)) # needs str

    # TODO: refactor this?
    namespace = _load_model_dir(model_dir=model_dir.name)
    model_class = _load_model_class(namespace=namespace, model_name=args["model_name"])

    # change dir to model_dir so that all relative imports of the model work
    os.chdir(os.path.dirname(namespace.__file__))

    if "model_keyword_args" in args:
        model = model_class(output_dir=output_dir, data_file=data_file, **args["model_keyword_args"])
    else:
        model = model_class(output_dir=output_dir, data_file=data_file)

    # run the experiments
    logger.info("Starting function '{fun}' from model '{mn}'".format(fun=args["model_fun"], mn=args["model_name"]))
    
    if args["model_fun"] == "train":
        model.train()

    elif args["model_fun"] == "infer":
        model.infer()

    else:
        raise ValueError("Provided function should be either test or infer (was {fun})".format(fun=args["model_fun"]))

    logger.info("Function '{fun}' from model '{mn}' completed successfully".format(fun=args["model_fun"], mn=args["model_name"]))


if __name__ == "__main__":
    args = _parse_runner_args(sys.argv)
    main(args)