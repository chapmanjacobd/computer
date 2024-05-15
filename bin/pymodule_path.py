#!/usr/bin/python3
import importlib.util
import sys

if len(sys.argv) < 2:
    print("Please provide the module name as an argument.")
else:
    module_name = sys.argv[1]
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            module_location = spec.origin
            print(module_location)
        else:
            print(f"Module '{module_name}' not found.")
    except ImportError:
        print(f"Unable to import '{module_name}'.")
