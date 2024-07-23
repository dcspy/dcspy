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

Path to Search Criteria file should be passed when getting dcp messages. Search Criteria file can be any text file in
the following format.

```text
# EXAMPLE SEARCH CRITERIA
DRS_SINCE: now - 1 hour
DRS_UNTIL: now
SOURCE: GOES_SELFTIMED
SOURCE: GOES_RANDOM
DCP_ADDRESS: <dcp address>
DCP_ADDRESS: <dcp address>
```

- Lines starting with `#` can be used to add comments
- You can read
  more [here](https://opendcs-env.readthedocs.io/en/stable/lrgs-userguide.html#search-criteria-file-format). NOTE THAT,
  only
  following keywords are supported by `dcspy` at this point:
    - `DRS_SINCE`
    - `DRS_UNTIL`
    - `SOURCE` (can be `GOES_SELFTIMED` or `GOES_RANDOM`, or both)
    - `DCP_ADDRESS` (can add multiple dcp addresses)

## Contributors

- [Manoj Kotteda](https://github.com/orgs/dcspy/people/manojkotteda)
- Darshan Baral
