# send_webhook_payload.py
# This action extracts metadata from a GitHub Actions event and sends it via HTTP to a database.
# Note: For now, this action only supports pull request events.
# Inputs:
# os.environ['INPUT_COLLECTOR_ENDPOINT']
# os.environ['INPUT_COLLECTOR_TOKEN']
# os.environ['INPUT_JIRA_KEYS']
# os.environ['INPUT_EVENT']

# imports
import json
import os
import re
import requests

def get_pull_request_info(event_json):
    pull_request_info = {}
    pull_request_info['number'] = event_json["pull_request"]["number"]
    pull_request_info['url'] = event_json["pull_request"]["url"] 
    pull_request_info['title'] = event_json["pull_request"]["title"]
    pull_request_info['created_at'] = event_json["pull_request"]["created_at"]
    pull_request_info['description'] = event_json["pull_request"]["body"]
    pull_request_info['author'] = event_json["pull_request"]["user"]["login"]
    return pull_request_info

if __name__=='__main__':
    # read in env vars
    collector_endpoint = os.environ['INPUT_COLLECTOR_ENDPOINT']
    collector_token = os.environ['INPUT_COLLECTOR_TOKEN']
    jira_keys = os.environ['INPUT_JIRA_KEYS']
    event = os.environ['INPUT_EVENT']

    # extract all JIRA tickets
    jira_tickets = []
    for key in jira_keys.split(","):
        regex_string = "\b" + key + "-\d+"
        matches = re.findall(regex_string, event)
        if matches:
            jira_tickets.append(matches)
    # flatten list of lists, if needed
    all_jira_tickets = [item for sublist in jira_tickets for item in sublist]

    # read in event data into json for remaining queries
    event_json = json.loads(event)

    # construct payload
    ## extract general metadata
    payload = {}
    payload['repo_org'] = event_json["repository"]["full_name"].split("/")[0]
    payload['repo_name'] = event_json["repository"]["name"]
    payload['repo_url'] = event_json["repository"]["html_url"]
    payload['jira_issues'] = all_jira_tickets
    ## extract event type-specific information
    if "pull_request" in event_json.keys():
        payload['pull_request'] = get_pull_request_info(event_json)
        payload['event_type'] = "pull_request"
    else:
        type_specific_info = {}
        payload['event_type'] = "unknown"

    # send payload
    if collector_token:
        response = requests.post(collector_endpoint, headers = {"token": collector_token}, data = json.dumps(payload))
    else:
        response = requests.post(collector_endpoint, data = json.dumps(payload))
    # check response
    print(f"Response code: {response.status_code}")
    response.raise_for_status()
