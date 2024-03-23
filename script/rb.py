import sys
import json


def write_config(links):
    config = {"urls": links}
    with open("config.json", "w") as f:
        json.dump(config, f)


if __name__ == "__main__":
    write_config(sys.argv[1:])
