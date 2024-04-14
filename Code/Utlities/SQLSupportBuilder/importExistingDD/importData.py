import jsonschema
import json
from Code.Utlities.base_utils import accessDB


# Define the JSON schema
schema = {
    "type": "object",
    "properties": {
        "tableName": {"type": "string"},
        "tableDesc": {"type": "string"},
        "records": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "TableName": {"type": "string"},
                    "ColumnName": {"type": "string"},
                    "DataType": {"type": "string"},
                    "Constraints": {"type": "string"},
                    "logic": {"type": "string"},
                    "type_of_logic": {"type": "string"},
                    "base_table": {"type": "string"},
                    "Desc": {"type": "string"},
                },
                "required": ["TableName", "ColumnName", "DataType", "Constraints", "logic", "type_of_logic", "base_table", "Desc"]
            }
        }
    },
    "required": ["tableName", "tableDesc", "records"]
}

def validate_json(json_data):
    """
    Validate JSON data against a predefined schema.

    Args:
        json_data (dict): JSON data to be validated.

    Raises:
        ValueError: If the JSON data is not valid according to the schema.
    """
    try:
        jsonschema.validate(instance=json_data, schema=schema)
        print("JSON is valid.")
    except jsonschema.exceptions.ValidationError as e:
        raise ValueError("JSON is not valid.")

class importDD:
    """
    Class to import data dictionary information into the database.
    """
    def __init__(self):
        """
        Initializes an instance of importDD class.
        """
        info_type = "table"
        dbName = "tableMetadata"
        self.tableDescName = "tableDesc"
        self.tableColName = "tableColMetadata"

        self.DBObj = accessDB(info_type, dbName)

    def createTable(self):
        """
        Create database tables if they don't exist.
        """
        # Create Table Desc Table
        tableDescSchema = {
            'tableName' : 'tableDesc',
            'columns' : {
                'tableName': ['TEXT', 'PRIMARY KEY'],
                'Desc': ['TEXT', '']
            }
        }
        self.DBObj.create_table(tableDescSchema)

        # Create Table Column Metadata Table
        tableColSchema = {
            'tableName' : 'tableColMetadata',
            'columns' : {
                'TableName': ['TEXT', ''],
                'ColumnName': ['TEXT', ''],
                'DataType': ['TEXT', ''],
                'Constraints': ['TEXT', ''],
                'logic': ['TEXT', ''],
                'type_of_logic': ['TEXT', ''],
                'base_table': ['TEXT', ''],
                'Desc': ['TEXT', '']
            }
        }
        self.DBObj.create_table(tableColSchema)




    def importData(self, jsonFilePath: str):
        """
        Import data dictionary information into the database.

        Args:
            jsonFilePath (str): Path to the JSON file containing data dictionary information.

        """
        # Create table, if not exists
        self.createTable()

        with open(jsonFilePath,"r") as tableJsonFObj:
            importedJsonData = json.load(tableJsonFObj)

        try:
            validate_json(importedJsonData)
        except:
            raise ValueError("JSON is not valid.")

        tableDesc = [{
            "tableName":importedJsonData['tableName'],
            "Desc":importedJsonData['tableDesc']
        },]

        tableCol = importedJsonData['records']

        print(tableDesc)
        print(tableCol)

        try:
            self.DBObj.post_data(self.tableDescName, tableDesc)
            self.DBObj.post_data(self.tableColName, tableCol)
        except Exception as e:
            print(str(e))


# importDataObj = importDD()
#
# importDataObj.importData(r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\sampleFiles\existingDD\Impressions_Table.JSON")
# importDataObj.importData(r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\sampleFiles\existingDD\Campaigns_Table.JSON")
# importDataObj.importData(r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\sampleFiles\existingDD\Actions_Table.JSON")