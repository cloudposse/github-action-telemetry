# GitHub Action for Telemetry

**Name:** `cloudposse/github-action-telemetry`

When triggered by a GitHub API event, this action will scrape the event for all JIRA tickets mentioned and an assortment of relevant metadata.

## Usage instructions

Create a workflow file (e.g. `.github/workflows/github-telemetry.yml`) that contains a step that `uses: cloudposse/github-action-telemetry@v1.0.0`. Here's an example workflow file:

```yaml
name: GitHub Telemetry
on: pull_request

jobs:
  telemetry:
    runs-on: ubuntu-latest
    steps:
    - uses: cloudposse/github-action-telemetry@v1.0.0
      with:
        collector_endpoint: "https://awesome-endpoint.net"
        collector_token: ${{ secrets.token }}
        jira_keys: "DEV,OPS,SECOPS,IT"

```

## Inputs

- `collector_endpoint`: This is the HTTP(S) address of a webhook that is expecting POST payloads that conform to the specifications in the next section.
- `collector_token`: This is an optional token the will be passed in a `token=` header attached to the HTTP POST payload sent to the `collector_endpoint`.
- `jira_keys`: This is a comma-separated, (space-free) list of JIRA codes to look for in the GitHub event JSON. For example, if `jira_keys: "INTERNAL"`, then `cloudposse/github-action-telemetry` will extract all strings matching the regular expression `\bINTERNAL-\d+` from the GitHub event JSON.

## Payload Specification

```

{
  repo_org: // e.g. cloudposse
  repo_name: // e.g. infra
  repo_url: // full URL to repo
  event_type: // github event type
  jira_tickets: [] // extracted from event payload
  pull_request { // if the event is a pull_request
    created_at:
    number:
    url:
    title:
    author:
    description:
  }
}

```

## Why?

This event could facilitate automatic annotation of JIRA tickets based on the contents of GitHub pull requests, to improve task tracking between these two platforms. Other integration routes certainly exist.
