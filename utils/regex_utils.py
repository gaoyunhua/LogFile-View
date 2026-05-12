import re

def apply_regex(log_line: str, regex: str):
    """
    Apply a regular expression to a log line and trim leading and trailing whitespace from the matched data.
    :param log_line: The raw log line.
    :param regex: The regular expression to apply.
    :return: The matched value with leading and trailing whitespace removed, or None if no match is found or the result is empty.
    """
    try:
        match = re.search(regex, log_line)
        if match:
            # Trim leading and trailing whitespace from the matched data
            sReturn = match.group(0).strip()
            if sReturn == "":  # Check if the result is an empty string
                return None
            return sReturn
        return None
    except re.error as e:
        # print(f"Warning: Invalid regular expression '{regex}' - {e}")
        return None