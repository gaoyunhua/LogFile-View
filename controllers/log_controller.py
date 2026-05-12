import os
import re
from models.log_model import LogModel
from utils.regex_utils import apply_regex


class LogController:
    def __init__(self, log_model: LogModel):
        self.log_model = log_model

    def load_log_file(self, file_path: str):
        """
        Load a log file and parse its content.
        :param file_path: Path to the log file.
        :return: True if the file was loaded successfully, False otherwise.
        """
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            return False

        if not os.path.isfile(file_path):
            print(f"Error: '{file_path}' is not a valid file.")
            return False

        try:
            self.log_model.load_logs(file_path)
            return True
        except Exception as e:
            print(f"Error loading log file: {e}")
            return False

    def get_logs(self, fields):
        """
        Retrieve logs with field data extracted using regular expressions.
        :param fields: Dictionary of all field definitions.
        :return: List of logs with extracted field data.
        """
        # Filter visible fields
        visible_fields = {name: data for name, data in fields.items() if data.get("visibility", False)}

        # Retrieve sorted fields
        sorted_fields = [name for name, data in fields.items() if data.get("sorted", False)]

        # Calculate visible_fields - sorted_fields
        additional_fields = {name: data for name, data in visible_fields.items() if name not in sorted_fields}

        # Extract data for sorted fields
        extracted_logs = []
        for log in self.log_model.log_data:
            extracted_log = {"raw": log["raw"]}  # Always include the raw log line

            # Extract data for sorted fields
            has_sorted_data=False
            sLog = log["raw"]
            for field_name in sorted_fields:
                regex = fields[field_name].get("regex", "")
                result = apply_regex(sLog, regex)
                extracted_log[field_name] = result
                if result:
                    has_sorted_data=True

            if has_sorted_data:
                for field_name, field_data in additional_fields.items():
                    regex = field_data.get("regex", "")
                    result = apply_regex(sLog, regex)
                    extracted_log[field_name] = result    
                extracted_logs.append(extracted_log)

        return extracted_logs

    def filter_logs(self, log_item, filter_fields):
        """
        Filter logs to exclude entries where all fields marked as 'sorted' (except 'raw') are empty.
        :param fields: Dictionary of all field definitions.
        :return: List of filtered log entries.
        """
        # Identify fields marked as 'sorted'
        has_non_empty_sorted_field = any(
            log_item.get(field_name) for field_name in filter_fields
        )
        return has_non_empty_sorted_field

    def sort_logs(self, field_name: str, reverse: bool = False):
        """
        Sort logs based on a specific field.
        :param field_name: The field to sort by (e.g., 'time').
        :param reverse: Whether to sort in descending order.
        :return: List of sorted log entries.
        """
        try:
            self.log_model.log_data.sort(
                key=lambda log: log.get(field_name, ""),
                reverse=reverse
            )
            print(f"Logs sorted by '{field_name}' (reverse={reverse}).")
        except Exception as e:
            print(f"Error sorting logs: {e}")

    def save_logs_to_file(self, output_path: str):
        """
        Save the current logs to a file.
        :param output_path: Path to the output file.
        :return: True if the logs were saved successfully, False otherwise.
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for log in self.log_model.log_data:
                    f.write(f"{log}\n")
            print(f"Logs saved to '{output_path}'.")
            return True
        except Exception as e:
            print(f"Error saving logs to file: {e}")
            return False

    def test_regex(self, log_line: str, regex: str):
        """
        Test a regular expression on a single log line.
        :param log_line: The raw log line.
        :param regex: The regular expression to test.
        :return: The matched value or None if no match is found.
        """
        return apply_regex(log_line, regex)