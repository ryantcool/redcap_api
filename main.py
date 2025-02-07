#!/usr/bin/env python3

"""
This script is used to query data from multiple redcap projects via api tokens
and save the data as a form of backup.
"""

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


#########################
#   Data for API Calls  #
#########################

# Exports all records

records_data = {
    "token": "",
    "content": "record",
    "action": "export",
    "format": "csv",
    "type": "flat",
    "csvDelimiter": ",",
    "rawOrLabel": "raw",
    "rawOrLabelHeaders": "raw",
    "exportCheckboxLabel": "false",
    "exportSurveyFields": "false",
    "exportDataAccessGroups": "false",
    "returnFormat": "json",
}

# Exports entire project

project_data = {
    "token": "",
    "content": "project_xml",
    "format": "xml",
    "returnMetadataOnly": "false",
    "exportFiles": "true",
    "exportSurveyFields": "true",
    "exportDataAccessGroups": "true",
    "returnFormat": "xml",
}

#############################
#   End of API Call Data    #
#############################


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


def set_token(pi_name: str):
    api_key = config["tokens"][0][pi_name]
    records_data["token"] = api_key
    project_data["token"] = api_key


def date_check():
    date = config["date-last-updated"]
    # Default to current date if not set in config
    if not date:
        date = datetime.today().strftime("%Y-%m-%d")
        config["date-last-updated"] = date
    else:
        pass
    days_passed = config["days"]
    # Default to 7 days if not set in config
    if not days_passed:
        days_passed = 7
        config["days"] = days_passed
    else:
        pass
    date_object = datetime.strptime(date, "%Y-%m-%d")
    if (datetime.today() - date_object).days >= int(days_passed):
        print(f"The date is/is over {days_passed} days ago")
        date = datetime.today().strftime("%Y-%m-%d")
        config["date-last-updated"] = date
        with open(path_to_config, "w") as config_file:
            json.dump(config, config_file, indent=4, sort_keys=True)
        return True
    else:
        print(f"The date is not {days_passed} days ago")
        return False


def file_org(
    pi: str, export_type: str, file_ext: str, records: str, output_dir: str
):
    export_date = datetime.today().strftime("%Y-%m-%d")
    title = f"all_{pi}_studies"
    file_name = f"{export_date}_{title}_{export_type}.{file_ext}"
    output_dir = os.path.join(output_dir, "")
    if file_ext == "xml":
        soup = BeautifulSoup(records, "xml")
        with open(
            os.path.join(output_dir, file_name), "w", encoding="utf-8"
        ) as file:
            file.write(str(soup.prettify()))
    elif file_ext == "csv":
        with open(
            os.path.join(output_dir, file_name), "w", encoding="utf-8"
        ) as file:
            file.write(records)


def main():
    try:
        output_dir = config["output_directory"]
        if not os.path.isdir(output_dir):
            print(f"Error: The directory {output_dir} does not exist")
            sys.exit(1)
    except KeyError:
        print("Error: output_directory not found in config.json")
        sys.exit(1)
    pi, export_type = sys.argv[1:3]
    if pi not in ["cosgrove", "davis", "esterlis"] or export_type not in [
        "records",
        "project",
    ]:
        print("Invalid arguments provided.")
        exit(1)

    set_token(pi)

    file_ext = "csv" if export_type == "records" else "xml"

    if export_type == "records":
        api_call = records_data
    elif export_type == "project":
        api_call = project_data
    else:
        print(f"{export_type} is not an acceptable value")
        exit(1)

    try:
        r = requests.post("https://poa-redcap.med.yale.edu/api/", data=api_call)
        print("HTTP Status: " + str(r.status_code))
        records = r.text
    except Exception as e:
        print(f"Error occurred: {e}")
        exit(1)

    file_org(pi, export_type, file_ext, records, output_dir)

    if date_check():
        print("THIS SCAN IS OLD AS FUQQQQQQQ")


if __name__ == "__main__":
    main()
