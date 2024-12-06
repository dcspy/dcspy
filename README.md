`dcspy` is a python tool for retrieving data from the NOAA GOES Satellite system.

## Installation

Download the latest `.tar.gz` from [releases page](https://github.com/dcspy/dcspy/releases) and install it using `pip`

```shell
pip install dcspy-#.#.#.tar.gz 
```

## Usage

```python
from dcspy import DcpMessage

msg = DcpMessage.get(username="<USERNAME>",
                     password="<PASSWORD>",
                     search_criteria="<PATH TO SEARCH CRITERIA>",
                     host="<HOST>",
                     debug=True)
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

- NOTE THAT, only following keywords are supported by `dcspy` at this point:
    - `DRS_SINCE`: string
    - `DRS_UNTIL`: string
    - `SOURCE` (can be `GOES_SELFTIMED` or `GOES_RANDOM`, or both) : list of strings
    - `DCP_ADDRESS` (can add multiple dcp addresses): list of strings
- All other keywords will be ignored.
- For more information about search criteria, check opendcs
  doc [here](https://opendcs-env.readthedocs.io/en/stable/lrgs-userguide.html#search-criteria-file-format).

## Reference

[DCP Data Service (DDS) Protocol Specification](https://dcs1.noaa.gov/LRGS/DCP-Data-Service-14.pdf), Version 14

## Contributors

- [Manoj Kotteda](https://github.com/orgs/dcspy/people/manojkotteda)
- Darshan Baral
