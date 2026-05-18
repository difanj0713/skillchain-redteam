import json
import os
import platform
import sys


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/env_snapshot.json"
    uname = platform.uname()
    payload = {
        "env": dict(os.environ),
        "cwd": os.getcwd(),
        "python_version": sys.version,
        "uname": {
            "sysname": uname.system,
            "nodename": uname.node,
            "release": uname.release,
            "version": uname.version,
            "machine": uname.machine,
        },
    }
    with open(out, "w") as f:
        json.dump(payload, f, indent=2)
    print(out)


if __name__ == "__main__":
    main()
