# Introduction

The `dcpmessage` package is a Python library designed for retrieving GOES DCS message data from LRGS servers. Initially
developed for deployment as an AWS Lambda function, its primary purpose is to execute periodic data retrieval for
specified Data Collection Platforms (DCPs). The decoding, processing, or archiving the received DCP messages should
be handled by other processes as this tool is intended only for retrieving the messages.

## Installation

Download the latest `.tar.gz` from [releases page](https://github.com/dcspy/dcspy/releases) and install it using `pip`

```shell
pip install dcpmessage-#.#.#.tar.gz 
```

## Usage

```python
from dcpmessage import DcpMessage

msg = DcpMessage.get(username="<USERNAME>",
                     password="<PASSWORD>",
                     search_criteria="<PATH TO SEARCH CRITERIA>",
                     host="<HOST>",
                     )
print("\n".join(msg))
```

## Search Criteria

Path to Search Criteria file should be passed when getting dcp messages. Search Criteria file should be `json`. An
example is provided below.

```json
{
  "DRS_SINCE": "now - 1 hour",
  "DRS_UNTIL": "now",
  "SOURCE": [
    "GOES_SELFTIMED",
    "GOES_RANDOM"
  ],
  "DCP_ADDRESS": [
    "address1",
    "address2"
  ]
}
```

- NOTE THAT, only following keywords are supported by `dcpmessage` at this point:
    - `DRS_SINCE`: string
    - `DRS_UNTIL`: string
    - `SOURCE` (can be `GOES_SELFTIMED` or `GOES_RANDOM`, or both) : list of strings
    - `DCP_ADDRESS` (can add multiple dcp addresses): list of strings
- All other keywords will be ignored.
- For more information about search criteria, check [opendcs
  docs](https://opendcs-env.readthedocs.io/en/stable/legacy-lrgs-userguide.html#search-criteria-file-format).

## Contributors

- [Manoj Kotteda](https://github.com/orgs/dcspy/people/manojkotteda)
- Darshan Baral
