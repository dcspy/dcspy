import logging

logger = logging.getLogger(__name__)

possible_delims = ",;|#+!~^&*"
possible_assigns = "=:><`()[]"

def props2string(pr):
    """Return the properties in a comma-separated string."""
    d_idx = 0
    a_idx = 0

    while d_idx < len(possible_delims):
        if any(possible_delims[d_idx] in str(v) for v in pr.values()):
            d_idx += 1
        else:
            break

    while a_idx < len(possible_assigns):
        if any(possible_assigns[a_idx] in str(v) for v in pr.values()):
            a_idx += 1
        else:
            break

    if d_idx == len(possible_delims):
        logger.warning("Cannot encode props because values contain all possible delims %s", possible_delims)
        d_idx = a_idx = 0

    if a_idx == len(possible_assigns):
        logger.warning("Cannot encode props because values contain all possible assignment operators %s", possible_assigns)
        d_idx = a_idx = 0

    delim = possible_delims[d_idx]
    assign = possible_assigns[a_idx]
    ret = []

    if d_idx != 0 or a_idx != 0:
        ret.append(delim)
        ret.append(assign)

    for i, (key, value) in enumerate(pr.items()):
        if i > 0:
            ret.append(delim)
            ret.append(' ')
        ret.append(f"{key}{assign}{value}")

    return ''.join(ret)

def string2props(s):
    """Convert a string containing comma-separated assignments into a Properties set."""
    ret = {}
    if not s:
        return ret

    s = s.strip()
    if len(s) < 3:
        return ret

    delim = ','
    assign = '='
    if not s[0].isalnum():
        delim = s[0]
        assign = s[1]
        s = s[2:]

    for tok in s.split(delim):
        tok = tok.strip()
        ei = tok.find(assign)
        if ei == -1:
            ret[tok] = ""
        else:
            ret[tok[:ei].strip()] = tok[ei+1:].strip()

    return ret

def get_ignore_case(pr, key, default_value=None):
    """Search for a property, ignoring case."""
    for k, v in pr.items():
        if key.strip().lower() == k.strip().lower():
            return v
    return default_value

def rm_ignore_case(pr, key):
    """Search for a property, remove it and return its value, ignoring case."""
    for k in list(pr.keys()):
        if key.lower() == k.lower():
            return pr.pop(k)
    return None

if __name__ == "__main__":
    print("Enter properties encoded as a string. Blank line when done.")
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip():
            break

        p = string2props(line)
        for key, val in p.items():
            print(f"{key} = {val}")

        print("Re-encoded as string: ")
        print(props2string(p))
        print()
