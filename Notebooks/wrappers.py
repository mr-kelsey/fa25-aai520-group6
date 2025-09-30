from typing import Callable
from inspect import signature, _empty


class Tool:
    """
    A class representing a tool as adapted from https://huggingface.co/learn/agents-course/en/unit1/tools Sep 2025

    Attributes:
        name (str): Name of the tool.
        description (str): A textual description of what the tool does.
        func (callable): The function this tool wraps.
        arguments (list): A list of arguments.
        outputs (str or list): The return type(s) of the wrapped function.
    """
    def __init__(self, name:str, description:str, func:Callable, arguments:list, outputs:str):
        self.name = name
        self.description = description
        self.func = func
        self.arguments = arguments
        self.outputs = outputs

    def to_string(self) -> str:
        """
        Return a string representation of the tool.
        """
        args_str = ", ".join([
            f"{arg_name}: {arg_type}" for arg_name, arg_type in self.arguments
        ])

        return f"Tool Name: {self.name}, Description: {self.description}, Arguments: {args_str}, Outputs: {self.outputs}"

    def __call__(self, *args, **kwargs):
        """
        Invoke the underlying function (callable) with provided arguments.
        """
        return self.func(*args, **kwargs)


def tool(func):
    """
    A decorator for wrapping a function into a callable Tool class.
    Adapted from https://huggingface.co/learn/agents-course/en/unit1/tools Sep 2025
    """
    assert func.__doc__, f"{func.__name__} requires a description to be used as a tool"

    name = func.__name__
    description = func.__doc__

    function_signature = signature(func)

    arguments = []
    for param in function_signature.parameters.values():
        assert param.annotation is not _empty, f"{func.__name__} requires parameter annotation to be used as a tool"
        annotation_name = param.annotation.__name__
        arguments.append((param.name, annotation_name))

    return_annotation = function_signature.return_annotation
    assert return_annotation is not _empty, f"{func.__name__} requires a return annotation to be used as a tool"
    outputs = return_annotation.__name__

    return Tool(name, description, func, arguments, outputs)


if __name__ == "__main__":
    # Test our implementation of the tool wrapper
    @tool
    def int2str(int_in:int) -> str:
        """Take in an integer and convert it to a string"""
        return str(int_in)
    
    print(int2str.to_string())