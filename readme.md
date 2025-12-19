# Redcap Project Backup via API Tokens


### Getting Started
---
- Usage: `redcap_backup --pi <pi-name> --type <records | project>`


- [Config Template](https://codeberg.org/ryantcool/redcap_api/src/branch/main/configs/config.json.template) <sup>[\[1\]](#note_1)</sup>


```
{
    "date-last-updated": "YYYY-mm-dd",
    "days": "number-of-days",
    "output_directory": "/path/to/output/",
    "redcap_url": "https://your-project/api/",
    "export": {
        "project": {
            "content": "project_xml",
            "exportDataAccessGroups": "true",
            "exportFiles": "true",
            "exportSurveyFields": "true",
            "format": "xml",
            "returnFormat": "xml",
            "returnMetadataOnly": "false",
            "token": ""
        },
        "records": {
            "action": "export",
            "content": "record",
            "csvDelimiter": ",",
            "exportCheckboxLabel": "false",
            "exportDataAccessGroups": "false",
            "exportSurveyFields": "false",
            "format": "csv",
            "rawOrLabel": "raw",
            "rawOrLabelHeaders": "raw",
            "returnFormat": "json",
            "token": "",
            "type": "flat"
        }
    },
    "tokens": [
        {
            "pi": "SuPerSeCr3tT0k3N"
        }
    ]
}
```

- `date-last-updated`: The date the script was last run.
    - This gets updated in the config file every time you run the script and it's been n amount of days since the last run, where n is `days`
    - **IF THIS IS NOT SET IT WILL DEFAULT TO THE CURRENT DATE YOU'RE RUNNING THE SCRIPT**
- `days`: The amount of days that need to pass for next backup. Defaults to 7 days if not specifically set
    - i.e. for it to run every week, set days to 7
    - **FOR FIRST RUN, SET THIS TO 0 SO IT RUNS, THEN CHANGE IT TO TIME-FRAME YOU WANT**
- `tokens`: This is where you store the api tokens for each redcap project
    - `pi-name`: The name of the pi
    - `api-token`: The api token associated with that pi's project
- `output_directory`: The full file-path on the system to where you want the backup to be saved

### Notes
<!----><a name="note_1"></a>
1) Currently needs to be placed in same directory as script
