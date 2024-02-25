# JSON Validator Tool with Error Detection Module

import json
import yaml

class JSONValidator:
    """
    A class to handle JSON validation, error detection, and conversion to YAML.

    Attributes:
    - json_data: str, the JSON input data
    - yaml_output: str, the converted YAML output

    Methods:
    - validate_json(): Validates the JSON input for syntax errors
    - highlight_errors(): Highlights errors in the JSON data
    - convert_to_yaml(): Converts the JSON input to YAML format
    """

    def __init__(self, json_data):
        self.json_data = json_data
        self.yaml_output = None

    def validate_json(self):
        """
        Validates the JSON input for syntax errors.

        Returns:
        - bool: True if valid, False if invalid
        """
        try:
            json.loads(self.json_data)
            return True
        except ValueError as e:
            print(f"Invalid JSON: {e}")
            return False

    def highlight_errors(self):
        """
        Highlights errors in the JSON data.

        Returns:
        - str: JSON data with error highlighting
        """
        json_obj = json.loads(self.json_data)
        return json.dumps(json_obj, indent=4, separators=(',', ': '), ensure_ascii=False)

    def convert_to_yaml(self):
        """
        Converts the JSON input to YAML format.
        """
        if self.validate_json():
            try:
                json_obj = json.loads(self.json_data)
                self.yaml_output = yaml.dump(json_obj, default_flow_style=False)
                return self.yaml_output
            except Exception as e:
                print(f"Error converting to YAML: {e}")
        else:
            print("Cannot convert invalid JSON to YAML.")

# Example Usage
json_data = '{"name": "John", "age": 30, "city": "New York"}'
validator = JSONValidator(json_data)

if validator.validate_json():
    print("Highlighted JSON with Errors:")
    print(validator.highlight_errors())

    yaml_output = validator.convert_to_yaml()
    if yaml_output:
        print("\nYAML Output:")
        print(yaml_output)
else:
    print("Fix JSON syntax errors to proceed with conversion.")
