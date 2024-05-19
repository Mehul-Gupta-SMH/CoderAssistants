"""
Module: data_dictionary.py

Description:
    This module defines the DataDictionary class, which is used to generate data dictionaries for tables.
    It utilizes language model (LM) APIs for text generation to create descriptions for columns and tables.

Classes:
    - DataDictionary: Class to generate data dictionaries for tables.

Attributes:
    - service (str): The service to be used for text generation (e.g., "open_ai", "anthropic").
    - info_type (str): The type of information (e.g., "table").
    - dbName (str): The name of the database.
    - tablename (str): The name of the table for column metadata.
    - DBObj (accessDB): Instance of accessDB class for database access.
    - LLMApiService (CallLLMApi): Instance of CallLLMApi class for calling LM APIs.

Methods:
    - __init__(self, service): Initializes an instance of DataDictionary class.
    - __retrieve_existing_dd__(self, table_metadata) -> dict: Retrieves existing data dictionary from storage and updates table metadata.
    - __generate_new_desc__(self, table_metadata_w_d_desc) -> list: Generates descriptions for new columns.
    - __generate_table_desc__(self, tableName, tableMetadata, tableInsertQ="") -> dict: Generates table description using table metadata and column descriptions.
    - Generate(self, tableName, table_metadata, tableInsertQ) -> tuple: Orchestrates the data dictionary generation process.

Usage Example:
    >> dd_obj = DataDictionary("GOOGLE")
    >> table_name = "Campaigns"
    >> table_metadata = [
    >>        {"ColumnName": "campaign_id", "type_of_logic": "direct"},
    >>        {"ColumnName": "campaign_name", "type_of_logic": "derived"},
    >>        {"ColumnName": "start_date", "type_of_logic": "direct"},
    >>        {"ColumnName": "end_date", "type_of_logic": "direct"}
    >>    ]
    >>    table_insert_query = "INSERT INTO Campaigns (campaign_id, campaign_name, start_date, end_date) VALUES (1, 'Campaign 1', '2024-01-01', '2024-12-31');"
    >>    print(dd_obj.Generate(table_name, table_metadata, table_insert_query))
"""

from Code.Utilities.base_utils import get_config_val
from Code.Utilities.base_utils import accessDB
from Code.Utilities.base_utils import cachefunc
from Code.Utilities.apiSupport.allApi import CallLLMApi


memoizer = cachefunc()

class DataDictionary:
    def __init__(self, service: str):
        """
        Initializes an instance of DataDictionary class.

        Args:
            service (str): The service to be used for text generation (e.g., "open_ai", "anthropic").
        """
        self.service = service
        self.info_type = "table"
        self.dbName = "tableMetadata"
        self.tablename = "tableColMetadata"

        self.DBObj = accessDB(self.info_type, self.dbName)

        self.LLMApiService = CallLLMApi(service)

    def __retrieve_existing_dd__(self, table_metadata):
        """
        Retrieve existing data dictionary from a storage (e.g., database).

        Args:
            table_metadata (dict): Metadata of the tables.

        Returns:
            dict: Updated table metadata with descriptions filled from the existing data dictionary.
        """

        # table_list from table_metadata
        table_list = list(set([table  for records in table_metadata for table, _ in records['base_table'].items()]))

        # print("Table List :", table_list)

        # Implement logic to retrieve existing data dictionary
        for tablename in table_list:
            tableColMetadata = self.DBObj.get_data(tableName=self.tablename,
                                                   lookupDict={"TableName":tablename},
                                                   lookupVal={},
                                                   fetchtype="all")
            # print("Table NM :", tablename)
            # print("Table MD :", tableColMetadata)

            if len(tableColMetadata):

                for ind, colMD in enumerate(table_metadata):

                    # print("Column : ",colMD['columnName'])

                    if colMD["type_of_logic"] == "direct":
                        # print(" ".join([item[1] for item in tableColMetadata if item[1].lower().strip() == colMD['columnName'].lower().strip()]))
                        # print(" ".join([item[7] for item in tableColMetadata if item[1].lower().strip() == colMD['columnName'].lower().strip()]))
                        table_metadata[ind]["Desc"] = " ".join([item[7] for item in tableColMetadata if item[1].lower().strip() == colMD['columnName'].lower().strip()])
                    else:
                        table_metadata[ind]["Desc"] = table_metadata[ind].get("Desc","\n -> ") + "\n -> ".join([item[1] + " : " + item[7] for item in tableColMetadata if item[1].lower() in colMD['columnName'].lower().split(",")])

        return table_metadata

    @memoizer.memoize
    def __generate_new_desc__(self, table_metadata_w_d_desc):
        """
        Generates descriptions for new columns.

        Args:
            table_metadata_w_d_desc (list): List of table metadata with existing descriptions.

        Returns:
            list: List of table metadata with updated descriptions.
        """

        newTableMetadata = []

        for ind, colMD in enumerate(table_metadata_w_d_desc):
            newTableMetadata.append(colMD)

            if colMD["type_of_logic"] == "direct":
                continue
            else:
                print("----------------------------------------------")
                print("Column : ",colMD['columnName'])
                print("Column Desc : Gonna Cost : Invoking LLM")
                print("----------------------------------------------")
                # Setting up prompt
                with open(r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\Code\Utlities\Configs\apiTemplates\taskGenerateColumnDesc.txt","r") as promptTmplt_fobj:
                    prompt_template = promptTmplt_fobj.read()

                InterColMetadata = {}
                InterColMetadata[colMD['columnName']] = colMD
                prompt = prompt_template.replace("<<ColumnMetadata>>",str(InterColMetadata))

                newTableMetadata[ind]["Desc"] = self.LLMApiService.CallService(prompt)

        return newTableMetadata

    @memoizer.memoize
    def __generate_table_desc__(self, tableName, tableMetadata, tableInsertQ=""):
        """
        Generate table description using table metadata and column descriptions.
        {
            tableName : Table Name,
            tableDesc : Table Desc,
            tablePopDesc : Table Population Desc,
            tableColDesc :
                ColName : Description of how column is derived and what that metric mean (business description)
        }

        Args:
            tableName (str): The name of the table.
            tableMetadata (dict): Dictionary containing metadata for each column in the table.
            tableInsertQ (str, optional): INSERT query string. Defaults to "".

        Returns:
            str: Generated table description.
        """
        print("----------------------------------------------")
        print("Table Desc : Gonna Cost : Invoking LLM")
        print("----------------------------------------------")

        # Setting up prompt
        with open(r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\Code\Utlities\Configs\apiTemplates\taskGenerateTableSummary.txt","r") as promptTmplt_fobj:
            prompt_template = promptTmplt_fobj.read()

        prompt = prompt_template.replace("<<Table Data Dictionary>>",str(tableMetadata))
        prompt = prompt.replace("<<Table Insert Query>>",str(tableInsertQ))

        table_desc_dict = {
            "TableName" : tableName,
            "Desc" : self.LLMApiService.CallService(prompt)
        }

        return table_desc_dict

    def Generate(self, tableName, table_metadata, tableInsertQ):
        """
        Generates the data dictionary.

        This method orchestrates the data dictionary generation process by calling
        individual methods for retrieving existing data dictionary, generating
        descriptions for new columns, and generating table descriptions.

        Args:
            tableName (str): The name of the table.
            table_metadata (list): List of table metadata.
            tableInsertQ (str): INSERT query string.

        Returns:
            tuple: Generated table description and updated table metadata.
        """

        # Fill in column description from existing DD
        table_metadata_w_directs = self.__retrieve_existing_dd__(table_metadata)

        # Generate column description for derived columns
        table_metadata_w_coldesc = self.__generate_new_desc__(table_metadata_w_directs)

        # Generate table description using table metadata and column descriptions
        table_desc = self.__generate_table_desc__(tableName, table_metadata_w_coldesc, tableInsertQ)

        return table_desc, table_metadata_w_coldesc
