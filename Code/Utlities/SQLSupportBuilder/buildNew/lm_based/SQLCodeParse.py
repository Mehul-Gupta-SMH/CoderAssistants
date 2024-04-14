"""
Module: code_parse.py

Description:
    This module defines the CodeParse class, which is used to parse SQL queries and extract SQL components.
    It utilizes language model (LM) APIs for text generation to retrieve table metadata from DDL and insert queries.

Classes:
    - CodeParse: Class to parse SQL queries and extract SQL components.

Attributes:
    - service (str): The service to be used for text generation (e.g., "open_ai", "anthropic").
    - LLMApiService (CallLLMApi): Instance of CallLLMApi class for calling LM APIs.

Methods:
    - __init__(self, service): Initializes an instance of CodeParse class.
    - __get_table_name__(self, tableDDL: str) -> str: Extracts the table name from the CREATE TABLE DDL query.
    - __invoke_LM__(self, service, tableDDL, tableInsert) -> str: Invokes the LM API to generate text based on the provided queries.
    - __cleanTableMetadata__(genTM: dict) -> dict: Placeholder method to clean generated table metadata.
    - __flatten__(self, table_name: str, tableMetadata: dict) -> list[dict[str,str]]: Flattens the table metadata dictionary into a list of records.
    - getTableMetadata(self, tableDDL: str, tableInsert: str) -> tuple[str, dict]: Retrieves table metadata using the LM API.

Usage Example:
    >> SQLObj = CodeParse("GOOGLE")
    >> tableDDL = "CREATE TABLE Campaigns (campaign_id INT PRIMARY KEY, campaign_name VARCHAR(100) NOT NULL, start_date DATE NOT NULL, end_date DATE NOT NULL, budget DECIMAL(12, 2) NOT NULL, status VARCHAR(20) NOT NULL, impressions INT, clicks INT, conversions INT, campaign_performance DECIMAL(10, 2), CONSTRAINT check_campaign_performance CHECK (campaign_performance >= 0));"
    >> tableInsert = "INSERT INTO Campaigns (campaign_id, campaign_name, start_date, end_date, budget, status, impressions, clicks, conversions, campaign_performance) SELECT c.campaign_id, c.campaign_name, c.start_date, c.end_date, c.budget, c.status, COALESCE(SUM(i.impressions), 0) AS impressions, COALESCE(SUM(a.clicks), 0) AS clicks, COALESCE(SUM(a.conversions), 0) AS conversions, (COALESCE(SUM(a.clicks), 0) * 0.5 + COALESCE(SUM(a.conversions), 0) * 0.8) / COALESCE(SUM(i.impressions), 1) * 100 AS campaign_performance FROM Campaigns_Table c LEFT JOIN Impressions_Table i ON c.campaign_id = i.campaign_id LEFT JOIN Actions_Table a ON c.campaign_id = a.campaign_id GROUP BY c.campaign_id, c.campaign_name, c.start_date, c.end_date, c.budget, c.status;"
    >> print(SQLObj.getTableMetadata(tableDDL, tableInsert))
"""

from Code.Utlities.base_utils import get_config_val
from Code.Utlities.base_utils import cachefunc
from Code.Utlities.apiSupport.allApi import CallLLMApi

import requests
import json
import yaml
import pickle
import re

memoizer = cachefunc()

class CodeParse:
    """
    Class to parse SQL queries and extract SQL components.
    """
    def __init__(self, service):
        """
        Initializes an instance of SQLCodeParse class.

        Args:
            service (str): The service to be used for text generation (e.g., "open_ai", "anthropic").
        """
        self.service = service
        self.LLMApiService = CallLLMApi(service)

    def __get_table_name__(self, tableDDL: str):
        """
        Extracts the table name from the CREATE TABLE DDL query.

        Args:
            tableDDL (str): The CREATE TABLE DDL query string.

        Returns:
            str: The extracted table name.

        Raises:
            ValueError: If the table name cannot be extracted from the DDL.
        """
        # Use regular expression to find the table name in the DDL
        table_name_match = re.search(r'CREATE\s+TABLE\s+(\w+)\s+', tableDDL)

        if table_name_match:
            # Extract the table name from the regex match
            table_name = table_name_match.group(1)
            return table_name
        else:
            # Raise an error if the table name cannot be extracted
            raise ValueError("Can't extract table name. Table DDL is invalid!")

    @memoizer.memoize
    def __invoke_LM__(self, service, tableDDL, tableInsert):
        """
        Invokes the language model API to generate text based on the provided queries.

        Returns:
            str: Generated text.

        Raises:
            ValueError: If the API call fails.
        """
        print("Gonna Cost : Invoking LLM")
        # Setting up prompt
        with open(r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\Code\Utlities\Configs\apiTemplates\taskTemplate.txt","r") as promptTmplt_fobj:
            prompt_template = promptTmplt_fobj.read()

        prompt = prompt_template.replace("<<DDLQUERY>>",tableDDL)
        prompt = prompt.replace("<<INSERETQUERY>>",tableInsert)

        return self.LLMApiService.CallService(prompt)

    @staticmethod
    def __cleanTableMetadata__(genTM: dict):
        """
        Placeholder method to clean generated table metadata.

        Args:
            genTM (dict): Generated table metadata.

        Returns:
            dict: Cleaned table metadata.
        """
        cleanedTM = genTM

        try:
            cleanedTM = yaml.load(cleanedTM.strip(),yaml.FullLoader)

            clean_rule_list = [
                # ('metadata key', 'string to replace', 'alternative value')
                ('logic', 'Select ', ''),
            ]

            for col, inf in cleanedTM.items():
                for clean_rule in clean_rule_list:
                    cleanedTM[col][clean_rule[0]] = cleanedTM[col][clean_rule[0]].replace(clean_rule[1], clean_rule[2])
        except:
            print("Failed!")

        return cleanedTM


    def __flatten__(self, table_name: str, tableMetadata: dict) -> list[dict[str,str]]:
        """
        Flatten the table metadata dictionary into a list of records.

        Args:
            table_name (str): The name of the table.
            tableMetadata (dict): Dictionary containing metadata for each column in the table.

        Returns:
            list: List of dictionaries, each representing a flattened record.
        """
        output_data = []

        # Iterate over each column in the table metadata
        for column_name, values in tableMetadata.items():
            # Create a record dictionary with table name and column name
            record = {"tableName": table_name, "columnName": column_name}
            # Update the record with column metadata
            record.update(values)
            # Append the record to the output data list
            output_data.append(record)

        return output_data

    def getTableMetadata(self, tableDDL: str, tableInsert: str):
        """
        Retrieves table metadata using the language model API.

        Returns:
            dict: Table metadata.
            tableDDL (str): The DDL query string.
            tableInsert (str): The INSERT query string.
        """

        tableName = self.__get_table_name__(tableDDL)

        tableMetadata = self.__invoke_LM__(self.service, tableDDL, tableInsert)

        tableMetadata = CodeParse.__cleanTableMetadata__(tableMetadata)

        # print("Original : ", tableMetadata)

        tableMetadata = self.__flatten__(tableName, tableMetadata)

        return tableName, tableMetadata


# vTableDDL = """
# CREATE TABLE Campaigns (
#     campaign_id INT PRIMARY KEY,
#     campaign_name VARCHAR(100) NOT NULL,
#     start_date DATE NOT NULL,
#     end_date DATE NOT NULL,
#     budget DECIMAL(12, 2) NOT NULL,
#     status VARCHAR(20) NOT NULL,
#     impressions INT,
#     clicks INT,
#     conversions INT,
#     campaign_performance DECIMAL(10, 2), -- Campaign Performance column with complex calculation
#     CONSTRAINT check_campaign_performance CHECK (campaign_performance >= 0)
# );
# """
#
# vTableInsert = """
# INSERT INTO Campaigns (campaign_id, campaign_name, start_date, end_date, budget, status, impressions, clicks, conversions, campaign_performance)
# SELECT
#     c.campaign_id,
#     c.campaign_name,
#     c.start_date,
#     c.end_date,
#     c.budget,
#     c.status,
#     COALESCE(SUM(i.impressions), 0) AS impressions,
#     COALESCE(SUM(a.clicks), 0) AS clicks,
#     COALESCE(SUM(a.conversions), 0) AS conversions,
#     (COALESCE(SUM(a.clicks), 0) * 0.5 + COALESCE(SUM(a.conversions), 0) * 0.8) / COALESCE(SUM(i.impressions), 1) * 100 AS campaign_performance
# FROM
#     Campaigns_Table c
# LEFT JOIN
#     Impressions_Table i ON c.campaign_id = i.campaign_id
# LEFT JOIN
#     Actions_Table a ON c.campaign_id = a.campaign_id
# GROUP BY
#     c.campaign_id, c.campaign_name, c.start_date, c.end_date, c.budget, c.status;
# """
#
# vservice = "GOOGLE"
#
# if __name__ == "__main__":
#     SQLObj = CodeParse(vservice)
#     print(SQLObj.getTableMetadata(vTableDDL,vTableInsert))
#     print("Calling again")
#     SQLObj.getTableMetadata(vTableDDL,vTableInsert)