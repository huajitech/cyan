import sys
import toml
import os
from datetime import datetime, timedelta, timezone


if len(sys.argv) > 2:
    raise ValueError("More than 1 arguments were got.")
dir = os.path.abspath(sys.argv[1] if len(sys.argv) == 2 else os.path.curdir)
print(f"Project path was defined as: {dir}")
path = os.path.join(dir, "pyproject.toml")
if not os.path.exists(path):
    raise FileNotFoundError(f"Could not found project config file: {path}")
print(f"Project config was found: {path}")
with open(path, "r") as fp:
    print("Loading project config...")
    config = toml.load(fp)
print(f"Project config was loaded:\n {config}")
tz = timezone(timedelta(hours=8))
date = datetime.now(tz).strftime("%Y%m%d")
version = config["tool"]["poetry"]["version"] + f".dev{date}"
config["tool"]["poetry"]["version"] = version
print(f"Version was modified as: {version}")
with open(path, "w") as fp:
    print("Serializing and writing config to file...")
    toml.dump(config, fp)
print("Config was successfully serialized and written to file.")
print("Config was successfully updated.")
