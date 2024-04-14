"""
Module: build_metadata.py

Description:
    This module defines the BuildMD class, which is used to build metadata for tables using different algorithms such as LLM-based and heuristic-based.

Classes:
    - BuildMD: Class to build metadata for tables.

Attributes:
    - valid_values (set): Set of valid algorithm types.

Methods:
    - __init__(self, algo_type: str, algo_control: dict): Initializes an instance of the BuildMD class.
    - createTable(self): Creates tables in the SQL database to store metadata.
    - __Heuristic_based__(self, tableDDL: str, tableInsert: str): Generates metadata based on the heuristic algorithm.
    - __LLM_based__(self, tableDDL: str, tableInsert: str): Generates metadata based on the LLM algorithm.
    - indexinfo(self, tableDDL: str, tableInsert: str): Indexes information and stores metadata in the database.

Usage Example:
    vTableDDL = '''
CREATE TABLE Campaigns (
    campaign_id INT PRIMARY KEY,
campaign_name VARCHAR(100) NOT NULL,
start_date DATE NOT NULL,
end_date DATE NOT NULL,
budget DECIMAL(12, 2) NOT NULL,
status VARCHAR(20) NOT NULL,
impressions INT,
clicks INT,
conversions INT,
campaign_performance DECIMAL(10, 2), -- Campaign Performance column with complex calculation
CONSTRAINT check_campaign_performance CHECK (campaign_performance >= 0)
);
'''

vTableInsert = '''
INSERT INTO Campaigns (campaign_id, campaign_name, start_date, end_date, budget, status, impressions, clicks, conversions, campaign_performance)
SELECT
c.campaign_id,
c.campaign_name,
c.start_date,
c.end_date,
c.budget,
c.status,
COALESCE(SUM(i.impressions), 0) AS impressions,
COALESCE(SUM(a.clicks), 0) AS clicks,
COALESCE(SUM(a.conversions), 0) AS conversions,
(COALESCE(SUM(a.clicks), 0) * 0.5 + COALESCE(SUM(a.conversions), 0) * 0.8) / COALESCE(SUM(i.impressions), 1) * 100 AS campaign_performance
FROM
Campaigns_Table c
LEFT JOIN
Impressions_Table i ON c.campaign_id = i.campaign_id
LEFT JOIN
Actions_Table a ON c.campaign_id = a.campaign_id
GROUP BY
c.campaign_id, c.campaign_name, c.start_date, c.end_date, c.budget, c.status;
'''

BuildMetadataObj = buildMD(algo_type="LLM",algo_control={'model':"GOOGLE"})

print(BuildMetadataObj.indexinfo(vTableDDL, vTableInsert))
"""

# SQL Database to store data
from Code.Utlities.base_utils import accessDB

# Vector database to index table descriptions
# from Code.Utlities.Retrieval_Pipeline.RAGPipeline import ManageInformation

# Heuristic based solutions
from Code.Utlities.SQLSupportBuilder.buildNew.heuristic.SQLCodeParseHeuristic import SQLCodeParse as SQP

# LLM based solutions
from Code.Utlities.SQLSupportBuilder.buildNew.lm_based.SQLCodeParse import CodeParse as CP
from Code.Utlities.SQLSupportBuilder.buildNew.lm_based.GenerateDD import DataDictionary as DD


vdb_metadata = {

}

class buildMD:

    valid_values = {"LLM", "Heuristic"} # Set of valid algorithm type

    def __init__(self,
                 algo_type: str,
                 algo_control: dict):
        """
        Initializes an instance of the BuildMD class.

        Args:
            algo_type (str): The type of algorithm to be used for building metadata.
            algo_control (dict): Additional control parameters for the algorithm.
        """

        if algo_type not in self.valid_values:
            raise ValueError(f"Invalid parameter value : algo_type. Acceptable values : {self.valid_values}")

        self.algo_type = algo_type
        self.algo_control = algo_control

        self.info_type = "table"
        self.dbName = "tableMetadata"
        self.tableDescName = "tableDesc"
        self.tableColName = "tableColMetadata"

        self.DBObj = accessDB(self.info_type, self.dbName)


    def createTable(self):

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

    def __Heuristic_based__(self,
                            tableDDL: str,
                            tableInsert: str):
        """
        Generates metadata based on the Heuristic algorithm.

        Args:
            tableDDL (str): DDL query string.
            tableInsert (str): INSERT query string.

        Returns:
            tuple: Tuple containing table description and generated data dictionary.
        """
        pass

    def __LLM_based__(self,
                      tableDDL: str,
                      tableInsert: str):
        """
        Generates metadata based on the LLM algorithm.

        Args:
            tableDDL (str): DDL query string.
            tableInsert (str): INSERT query string.

        Returns:
            tuple: Tuple containing table description and generated data dictionary.
        """
        self.createTable()

        # Initialize SQLCodeParse object to extract table metadata
        CodeParseObj = CP(self.algo_control.get('model', 'OPEN_AI'))

        # Get table metadata
        TableName, SQLTableMetadata = CodeParseObj.getTableMetadata(tableDDL,tableInsert)

        # print("SQLTableMetadata :",SQLTableMetadata)

        # Initialize DataDictionary object and generate data dictionary
        DDGenObj = DD(self.algo_control.get('model', 'OPEN_AI'))
        TableDesc, TableGenDD = DDGenObj.Generate(TableName, SQLTableMetadata, tableInsert)

        return TableDesc, TableGenDD

    def indexinfo(self, tableDDL: str, tableInsert: str):
        """
        Indexes information and stores metadata in the database.

        Args:
            tableDDL (str): DDL query string.
            tableInsert (str): INSERT query string.
        """

        if self.algo_type == "LLM":
            TableDesc, TableGenDD = self.__LLM_based__(tableDDL, tableInsert)
        else:
            TableDesc, TableGenDD = self.__Heuristic_based__(tableDDL, tableInsert)


        self.DBObj.delete_data(self.tableDescName, {'tableName':TableDesc['TableName']})
        self.DBObj.delete_data(self.tableColName, {'TableName':TableDesc['TableName']})

        print("Table Desc : ", TableDesc)
        print("Table Gen DD : ", "\n -> ".join(map(str,TableGenDD)))
        print("Table Gen DD type :",type(TableGenDD))
        print("Table Gen DD type :",type(TableGenDD[0]))

        # Inserting data for Table Desc in database
        self.DBObj.post_data(self.tableDescName, [TableDesc])

        # Inserting data for Table Column metadata into database
        self.DBObj.post_data(self.tableColName, TableGenDD)

        # Index table description into VectorDB
        # vdbObj = ManageInformation()
        # vdbObj.initialize_client(path = "Path to DB")
        # vdbObj.add_new_data(TableDesc["tableName"], TableDesc, vdb_metadata)

        return "Process Complete"




vTableDDL = """
CREATE TABLE Campaigns (
    campaign_id INT PRIMARY KEY,
    campaign_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    budget DECIMAL(12, 2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    impressions INT,
    clicks INT,
    conversions INT,
    campaign_performance DECIMAL(10, 2), -- Campaign Performance column with complex calculation
    CONSTRAINT check_campaign_performance CHECK (campaign_performance >= 0)
);
"""

vTableInsert = """
INSERT INTO Campaigns (campaign_id, campaign_name, start_date, end_date, budget, status, impressions, clicks, conversions, campaign_performance)
SELECT
    c.campaign_id,
    c.campaign_name,
    c.start_date,
    c.end_date,
    c.budget,
    c.status,
    COALESCE(SUM(i.impressions), 0) AS impressions,
    COALESCE(SUM(a.clicks), 0) AS clicks,
    COALESCE(SUM(a.conversions), 0) AS conversions,
    (COALESCE(SUM(a.clicks), 0) * 0.5 + COALESCE(SUM(a.conversions), 0) * 0.8) / COALESCE(SUM(i.impressions), 1) * 100 AS campaign_performance
FROM
    Campaigns_Table c
LEFT JOIN
    Impressions_Table i ON c.campaign_id = i.campaign_id
LEFT JOIN
    Actions_Table a ON c.campaign_id = a.campaign_id
GROUP BY
    c.campaign_id, c.campaign_name, c.start_date, c.end_date, c.budget, c.status;
"""


BuildMetadataObj = buildMD(algo_type="LLM",algo_control={'model':"GOOGLE"})

print(BuildMetadataObj.indexinfo(vTableDDL, vTableInsert))
