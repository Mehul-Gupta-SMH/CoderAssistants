"""
Module for providing support for SQL query building. This module contains classes and methods
to provide necessary components for building SQL queries.

Class:
    - SQLBuilderSupport: Class to support SQL query building by providing necessary components.
"""


import json
from Code.Utilities.base_utils import get_config_val, accessDB
from Code.Utilities.Retrieval_Pipeline import RAGPipeline, ManageRelations




class SQLBuilderSupport:
    """
    Class to support SQL query building by providing necessary components.

    Attributes:
        user_query (str): The user's SQL query.
        table_list (dict): A dictionary containing relevant tables, both direct and intermediate.
        join_keys (dict): A dictionary containing table relations and associated join keys.
        table_metadata (dict): A dictionary containing metadata information for tables.
    """
    def __init__(self):
        """
        Initializes an instance of SQLBuilderSupport class.

        sample format of the table_list
        table_list:
            direct:
                tablename:
                    desc:
                    columns:
                        name:
                        dtype:
                        desc:
            intermediate:
        """
        self.user_query = None
        self.table_list = {
            "direct" : {},
            "intermediate" : {}
        }
        self.join_keys = None
        self.table_metadata = {}

        self.vdb_config = get_config_val("retrieval_config",["vectordb"],True)
        self.tmddb_config = get_config_val("retrieval_config",["tableMDdb"],True)

        self.DBObj = accessDB(self.tmddb_config['info_type'], self.tmddb_config['dbName'])

    def __filterRelevantResults__(self, results_w_scores):

        filtered_results_dict = {}
        for vals in results_w_scores.values():
            filtered_results_dict[vals['metadata']['TableName']] = {
                "description": vals['data'],
                "columns": {}
            }

        return filtered_results_dict

    def __getRelevantTables__(self):
        """
        Retrieve relevant tables based on the user's query.

        Returns:
            list: A list of relevant tables.
        """

        # Initializing a ManageInformation object for data retrieval
        RetrievalObj = RAGPipeline.ManageInformation()

        # Initializing the client
        RetrievalObj.initialize_client()

        # Retrieving data based on the user query
        results_scored = RetrievalObj.get_data(self.user_query, self.vdb_config["metadata"])

        # Performing filtering on the retrieved results
        filtered_results = self.__filterRelevantResults__(results_scored)

        # Updating the 'direct' table list attribute with the filtered results
        self.table_list["direct"] = filtered_results


    def __getTableRelations__(self):
        """
        Retrieve relations between tables.

        Returns:
            dict: A dictionary containing table relations and associated join keys.
        """
        # Initializing a Relations object for managing table relations
        RelationsObj = ManageRelations.Relations(strgType = "networkx")

        # Retrieving table relations and associated join keys
        self.join_keys = RelationsObj.getRelation(list(self.table_list["direct"].keys()))

        # Updating the 'intermediate' table list attribute with tables not in the 'direct' table list
        for tables in self.join_keys:
            sourceTable = tables['source']
            targetTable = tables['target']

            if sourceTable not in self.table_list["direct"].keys() and sourceTable not in self.table_list["intermediate"].keys():
                self.table_list["intermediate"] = {sourceTable : { "description": "", "columns": {} } }

            if targetTable not in self.table_list["direct"].keys() and targetTable not in self.table_list["intermediate"].keys():
                self.table_list["intermediate"] = {targetTable : { "description": "", "columns": {} } }


    def __getInterTablesDesc__(self):
        """
        Get descriptions for intermediate tables.

        Returns:
            dict: A dictionary containing descriptions for intermediate tables.
        """
        # Updating descriptions for intermediate tables
        for table,_ in self.table_list["intermediate"].items():
            self.table_list["intermediate"][table]["description"] = self.DBObj.get_data( tableName=self.tmddb_config['tableDescName'], lookupDict={'tableName':table}, lookupVal=['Desc',] )

    def __filterAdditionalColumns__(self, tableColDict: dict):
        """
        Placeholder method to filter additional columns from the user's query.

        Args:
            user_query (str): The user's SQL query.
            table_w_metadata: Additional table metadata.

        Returns:
            dict: Filtered table metadata.
        """
        return tableColDict

    def __getTablesColList__(self):
        """
        Placeholder method to get the list of columns for each table.

        Args:
            table_list (list): A list of tables.

        Returns:
            dict: A dictionary containing the list of columns for each table.
        """
        # Iterating over table types and their corresponding dictionaries

        for ttype, table_dict in self.table_list.items():
            for table, tablemd in table_dict.items():
                # Extracting column metadata for the current table
                fullColMetadata = self.DBObj.get_data( tableName=self.tmddb_config['tableColName'], lookupDict={'TableName':table}, lookupVal=['ColumnName','DataType','Constraints','Desc'] )
                # Updating the 'columns' attribute for the current table after filtering additional columns
                self.table_list[ttype][table]['columns'] = self.__filterAdditionalColumns__(fullColMetadata)


    def getBuildComponents(self, user_query: str) -> dict:
        """
        Get components necessary for building the SQL query.

        Args:
            user_query (str): The user's SQL query.

        Returns:
            dict: A dictionary containing the following components:
                - user_query: The user's SQL query.
                - table_list: Relevant tables, both direct and intermediate.
                - join_keys: Table relations and associated join keys.
                - table_metadata: Metadata information for tables.
        """

        self.user_query = user_query

        # Get relevant tables
        self.__getRelevantTables__()

        print("Scanned Relevant Table")
        print(self.table_list)

        # Get relations between tables
        self.__getTableRelations__()

        print("Scanned Relations between tables")
        print(self.join_keys)

        # Get info for intermediate tables
        self.__getInterTablesDesc__()

        print("Scanned intermediate tables required for joins")
        print(self.table_list)

        # Get relevant column list
        self.__getTablesColList__()

        print("Scanned all tables metadata")
        print(self.table_metadata)

        return {
            "user_query" : self.user_query,
            "table_list" : self.table_list,
            "join_keys" : self.join_keys,
        }
