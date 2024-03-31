

# Heuristic based solutions
from Code.Utlities.SQLSupportBuilder.heuristic.SQLCodeParseHeuristic import SQLCodeParse as SQP

# LLM based solutions
from Code.Utlities.SQLSupportBuilder.lm_based.SQLCodeParse import CodeParse as CP
from Code.Utlities.SQLSupportBuilder.lm_based.GenerateDD import DataDictionary as DD


class buildMD:

    valid_values = set("LLM", "Heuristic") # Set of valid algorithm type

    def __init__(self,
                 algo_type: str,
                 algo_control: dict):
        """
        Initializes an instance of BuildMD class.

        Args:
            algo_type (str): The type of algorithm to be used for building metadata.
            algo_control (dict): Additional control parameters for the algorithm.
        """
        if algo_type not in self.valid_values:
            raise ValueError(f"Invalid parameter value : algo_type. Acceptable values : {self.valid_values}")

        self.algo_type = algo_type
        self.algo_control = algo_control


    def __Heuristic_based__(self):
        """
        Placeholder method for LLM-based metadata generation.
        """
        pass

    def __LLM_based__(self,
                      algo_control: dict,
                      tableDDL: str,
                      tableInsert: str):
        """
        Generates metadata based on the Heuristic algorithm.

        Args:
            tableDDL (str): DDL query string.
            tableInsert (str): INSERT query string.

        Returns:
            DataDictionary: Generated data dictionary.
        """
        # Initialize SQLCodeParse object to extract table metadata
        CodeParseObj = CP(algo_control.get('model','OPEN_AI'))

        # Get table metadata
        SQLTableMetadata = CodeParseObj.getTableMetadata(tableDDL,tableInsert)

        # Initialize DataDictionary object and generate data dictionary
        DDGenObj = DD()
        GenDD = DDGenObj.DataDictionary(SQLTableMetadata)

        return GenDD

    def indexinfo(self):
        """
        Placeholder method for indexing information.
        """
        pass