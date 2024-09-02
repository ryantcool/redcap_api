#!/usr/bin/env python3

"""
This script is used to query data from multiple redcap projects via api tokens
and save the data as a form of backup.
"""

import sys
import os
import requests
import json
from datetime import datetime, timedelta
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
    'token': '',
    'content': 'record',
    'action': 'export',
    'format': 'csv',
    'type': 'flat',
    'csvDelimiter': ',',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'false',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json'
}

# Exports entire project

project_data = {
    'token': '',
    'content': 'project_xml',
    'format': 'xml',
    'returnMetadataOnly': 'false',
    'exportFiles': 'true',
    'exportSurveyFields': 'true',
    'exportDataAccessGroups': 'true',
    'returnFormat': 'xml'
}

#############################
#   End of API Call Data    #
#############################


def load_config():
    script_dir = os.path.dirname(__file__)
    path_to_config = os.path.join(script_dir, 'config.json')
    with open(path_to_config) as config_file:
        config = json.load(config_file)
    return path_to_config, config


path_to_config, config = load_config()


def set_token(pi_name):
    api_key = config['tokens'][0][pi_name]
    records_data['token'] = api_key
    project_data['token'] = api_key


def date_check():
    date = config['date']
    if not date:
        date = datetime.today().strftime('%Y-%m-%d')
        config['date'] = date
    else:
        pass
    date_object = datetime.strptime(date, '%Y-%m-%d')
    seven_days_ago = date_object + timedelta(days=7)
    if seven_days_ago.date() == datetime.today().date():
        print("The date is 7 days ago")
        date = datetime.today().strftime('%Y-%m-%d')
        config['date'] = date
        with open(path_to_config, 'w') as config_file:
            json.dump(config, config_file, indent=4, sort_keys=True)
        return True
    else:
        print("The date is not 7 days ago")
        return False


def file_org(pi, export_type, file_ext, records, output_dir):
    export_date = datetime.today().strftime('%Y-%m-%d')
    title = f"all_{pi}_studies"
    file_name = f"{export_date}_{title}_{export_type}.{file_ext}"

    if file_ext == "xml":
        soup = BeautifulSoup(records, "xml")
        with open(output_dir + file_name, "w", encoding="utf-8") as file:
            file.write(str(soup.prettify()))
    elif file_ext == "csv":
        with open(output_dir + file_name, "w") as file:
            file.write(records)


def main():
    output_dir = "C:\\redcap_backups\\daily\\"
    pi, export_type = sys.argv[1:3]
    if pi not in ["cosgrove", "davis", "esterlis"] or export_type not in ["records", "project"]:
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
        r = requests.post('https://poa-redcap.med.yale.edu/api/', data=api_call)
        print('HTTP Status: ' + str(r.status_code))
        records = r.text
    except Exception as e:
        print(f"Error occurred: {e}")
        exit(1)

    file_org(pi, export_type, file_ext, records, output_dir)

    if date_check():
        print("THIS SCAN IS OLD AS FUQQQQQQQ")


if __name__ == "__main__":
    main()
