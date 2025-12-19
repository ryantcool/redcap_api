#!/usr/bin/env python3

"""
This script is used to query data from multiple redcap projects via api tokens
and save the data as a form of backup.
"""

import argparse
import json
import os
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

__author__ = "Ryan Cool"
__credits__ = ["Ryan Cool", "Marco Grasso"]
__version__ = ""
__maintainer__ = "Ryan Cool"
__email__ = "ryan.cool@yale.edu"
__status__ = "Dev"


def get_args(args: list[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--pi", "-p", help="set study pi")
    parser.add_argument(
        "--type", "-t", help="set type of export, i.e. records or project"
    )
    return parser.parse_args(args)


def get_config_path():
    if getattr(sys, "frozen", False):
        # If this is running as a frozen executable
        gcp = os.path.dirname(sys.executable)
    else:
        # If this is running as a python script i.e. ./main.py
        gcp = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(gcp, "config.json")


def load_config():
    path_to_config = get_config_path()
    with open(path_to_config) as config_file:
        config = json.load(config_file)
    return path_to_config, config


path_to_config, config = load_config()


def date_check():
    date = config["date-last-updated"]
    days_passed = config["days"]
    # Default to current date if not set in config
    if not date:
        date = datetime.today().strftime("%Y-%m-%d")
        config["date-last-updated"] = date
        if not days_passed:
            days_passed = "7"
            config["days"] = days_passed
        else:
            pass
        # Write default value to config.json
        print(
            f"date_last_updated and/or days not set in {path_to_config}.\nSetting to defaults and running..."
        )
        with open(path_to_config, "w") as config_file:
            json.dump(config, config_file, indent=4, sort_keys=True)
        return True
    else:
        pass
    # Default to 7 days if not set in config
    if not days_passed:
        days_passed = "7"
        date = datetime.today().strftime("%Y-%m-%d")
        config["days"] = days_passed
        config["date-last-updated"] = date
        print(
            f"days not set in {path_to_config}.\nSetting to default (7) and running..."
        )
        # Write default value to config.json
        with open(path_to_config, "w") as config_file:
            json.dump(config, config_file, indent=4, sort_keys=True)
        return True
    else:
        pass
    date_object = datetime.strptime(date, "%Y-%m-%d")
    if (datetime.today() - date_object).days >= int(days_passed):
        date = datetime.today().strftime("%Y-%m-%d")
        config["date-last-updated"] = date
        with open(path_to_config, "w") as config_file:
            json.dump(config, config_file, indent=4, sort_keys=True)
        print("Backup scheduled successfully")
        return True
    else:
        print(f"{days_passed} day(s) have not passed. Skipping backup.")
        return False


def file_org(pi: str, export_type: str, file_ext: str, records: str, output_dir: str):
    export_date = datetime.today().strftime("%Y-%m-%d")
    title = f"all_{pi}_studies"
    file_name = f"{export_date}_{title}_{export_type}.{file_ext}"
    output_dir = os.path.join(output_dir, "")
    if file_ext == "xml":
        soup = BeautifulSoup(records, "xml")
        with open(os.path.join(output_dir, file_name), "w", encoding="utf-8") as file:
            file.write(str(soup.prettify()))
    elif file_ext == "csv":
        with open(os.path.join(output_dir, file_name), "w", encoding="utf-8") as file:
            file.write(records)


def main():
    args = get_args()
    if not args.pi or not args.type:
        print("Please specify BOTH the study pi and export type")
        sys.exit(1)

    pi, export_type = args.pi, args.type
    export_map = config["export"]
    token_map = config["tokens"][0]
    if not token_map.get(pi) or not export_map.get(export_type):
        print("Invalid arguments provided.")
        sys.exit(1)
    if date_check():
        try:
            output_dir = config["output_directory"]
            if not os.path.isdir(output_dir):
                print(f"Error: The output directory {output_dir} does not exist")
                sys.exit(1)
        except KeyError:
            print("Error: output_directory not set in config.json")
            sys.exit(1)

        # Set file extension depending on type specified
        file_ext = "csv" if export_type == "records" else "xml"

        # Set up API call by loading copy of config.json
        # with the correct token written into the token
        # field under export type
        api_call = config["export"][export_type].copy()
        api_call["token"] = token_map[pi]
        try:
            redcap_url = config["redcap_url"]
            r = requests.post(redcap_url, data=api_call)
            print("HTTP Status: " + str(r.status_code))
            records = r.text
        except Exception as e:
            print(f"Error occurred: {e}")
            sys.exit(1)
        file_org(pi, export_type, file_ext, records, output_dir)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
