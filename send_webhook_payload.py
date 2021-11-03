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


if __name__ == '__main__':
    # read in env vars
    collector_endpoint = os.environ['INPUT_COLLECTOR_ENDPOINT']
    collector_token = os.environ['INPUT_COLLECTOR_TOKEN']
    jira_keys = os.environ['INPUT_JIRA_KEYS']
    event = os.environ['INPUT_EVENT']
    if collector_endpoint == "" or jira_keys == "" or event == "":
        if collector_endpoint == "":
            print("collector_endpoint input is null-valued.")
        if jira_keys == "":
            print("jira_keys input is null-valued.")
        if event == "":
            print("event input is null-valued.")
        raise ValueError("Because one or more inputs is null-valued, this program is termiating.")

    # extract all JIRA tickets
    print(f"event: {event}")
    jira_tickets = []
    for key in jira_keys.split(","):
        regex_string = r"\b{}-\d+".format(key)
        print(f"regex: {regex_string}")
        matches = re.findall(regex_string, event)
        if matches:
            jira_tickets.append(matches)
    # flatten lists and deduplicate entries, if needed
    all_jira_tickets = [item for sublist in jira_tickets for item in sublist]
    all_jira_tickets = list(set(all_jira_tickets))

    # read in event data into json for remaining queries
    event_json = json.loads(event)

    # construct payload
    #  extract general metadata
    payload = {}
    payload['repo_org'] = event_json["repository"]["full_name"].split("/")[0]
    payload['repo_name'] = event_json["repository"]["name"]
    payload['repo_url'] = event_json["repository"]["html_url"]
    payload['jira_tickets'] = all_jira_tickets
    #  extract event type-specific information
    if "pull_request" in event_json.keys():
        payload['pull_request'] = get_pull_request_info(event_json)
        payload['event_type'] = "pull_request"
        payload['event_action'] = event_json["action"]
    else:
        type_specific_info = {}
        payload['event_type'] = "unsupported"

    # send payload
    print(f"Payload: {json.dumps(payload, indent=4)}")
    headers = {}
    headers['user-agent'] = "cloudposse/github-action-telemetry"
    if collector_token:
        headers['token'] = collector_token
        response = requests.post(collector_endpoint, headers=headers, json=payload)
    else:
        response = requests.post(collector_endpoint, headers=headers, json=payload)
    # check response
    print(f"Response code: {response.status_code}")
    response.raise_for_status()
