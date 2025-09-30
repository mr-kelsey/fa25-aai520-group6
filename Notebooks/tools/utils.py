from inspect import getsourcelines


def get_tool_names(module):
    source, *_ = getsourcelines(module)
    for line_number, line in enumerate(source):
        if line.strip() == "@tool":
            yield source[line_number + 1].split()[1].split("(")[0]