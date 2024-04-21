import os
import jsonschema
import json
from Code.Utlities.base_utils import accessDB
from Code.Utlities.Retrieval_Pipeline.RAGPipeline import ManageInformation

vdb_metadata = {
    "collection_name" : "tableScan",
    "sim_metric" : "cosine",
    "n_chunks" : 100
}

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


            tableMD = {
                "TableName" : importedJsonData['tableName'],
                "ENV" : "PROD",
                "DB" : "NORTHWIND",
                "TType" : "System"
            }

            # tableMD = {**tableMD, **tableAttr}

            # Index table description into VectorDB
            vdbObj = ManageInformation()
            vdbObj.initialize_client()
            vdbObj.add_new_data([importedJsonData['tableDesc']], [tableMD], vdb_metadata)
        except Exception as e:
            print(str(e))


# importDataObj = importDD()

# importDataObj.importData(r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\sampleFiles\existingDD\Impressions_Table.JSON")
# importDataObj.importData(r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\sampleFiles\existingDD\Campaigns_Table.JSON")
# importDataObj.importData(r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\sampleFiles\existingDD\Actions_Table.JSON")


# base_path = r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\sampleFiles\NorthWinds\DD"
#
# for files in os.listdir(base_path):
#     importDataObj.importData(os.path.join(base_path,files))

vdbObj = ManageInformation()
vdbObj.initialize_client()

# query = "Write me a query that calculates all the impressions for all campaigns."

# query = """
# For their annual review of the company pricing strategy, the Product Team wants to look at the products that are currently being offered for a specific price range ($20 to $50). In order to help them they asked you to provide them with a list of products with the following information:
#
# their name
# their unit price
# """

query = """
The Logistics Team wants to do a retrospection of their performances for the year 1998, in order to identify for which countries they didn’t perform well. They asked you to provide them a list of countries with the following information:

their average days between the order date and the shipping date (formatted to have only 2 decimals)

their total number of orders (based on the order date) Filtered on the following conditions:

the year of order date is 1998

their average days between the order date and the shipping date is greater or equal 5 days

their total number of orders is greater than 10 orders

Finally order the results by country name in an ascending order (lowest first).
"""

results = vdbObj.get_data(query, vdb_metadata)

for vals in results.values():
    print(f"Table Name : {vals['metadata']['TableName']}")
    print(vals)
    print()