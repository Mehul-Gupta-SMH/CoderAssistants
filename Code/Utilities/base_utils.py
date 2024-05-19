# --------------------------------------------------------------------
# Import Library
# --------------------------------------------------------------------
import yaml
import os
import functools
import logging
import sqlite3
import time
import inspect
import hashlib

# --------------------------------------------------------------------
def get_config_val(config_type: str, key_list: list, get_all=False) -> str:
    """
    Retrieve a configuration value from a YAML configuration file based on the provided configuration type and keys.

    args:
        - config_type (str): The type of configuration to retrieve.
        - *args (str): Variable length argument list of keys to navigate through the configuration.

    returns:
        - str: The value corresponding to the specified configuration type and keys.

    raises:
        - KeyError: If the provided configuration type is not found in the configuration file.
        - AttributeError: If unable to resolve the configuration value from the list of keys provided.

    """
    with open(
            r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\Code\Utilities\Configs\config_paths.yaml",
            "r") as conf_pths:
        config_map = yaml.load(conf_pths, yaml.FullLoader)

    if config_type not in config_map.keys():
        raise KeyError(f"{config_type} : Config Type not Correct")

    with open(config_map[config_type], 'r') as conf_file:
        config_val = yaml.load(conf_file, yaml.FullLoader)

        for key_val in key_list:
            try:
                config_val = config_val[key_val]
            except:
                raise KeyError(f"Key Value incorrect {key_val}")

    if isinstance(config_val, dict) and get_all == False:
        raise AttributeError("Incomplete Key List : Unable to resolve config value from list of keys provided")

    return config_val

# --------------------------------------------------------------------

def log_function(func):
    """
    Decorator function to log the inputs, outputs, and exceptions of a function.

    Input:
    - func (callable): The function to be decorated.

    Output:
    - callable: The decorated function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Log function inputs
        logging.info(f"'{func.__name__}'|{time.time()}|Start||")

        try:
            # Execute the function
            result = func(*args, **kwargs)

            # Log function output
            logging.info(f"'{func.__name__}'|{time.time()}|Sucess||")
            return result

        except Exception as e:
            # Log exceptions
            logging.error(f"'{func.__name__}'|{time.time()}|Error|ErrorMessage{str(e)}|Args:{args} , Kwargs:{kwargs}")

    return wrapper

# --------------------------------------------------------------------
class accessDB:
    def __init__(self, info_type: str, db_name: str):
        """
        Initializes an instance of AccessDB class.

        Args:
            info_type (str): Type of information (e.g., 'cache', 'table metadata').
            db_name (str): Name of the SQLite database.
        """
        # Construct database file path
        base_path = "C:/Users/mehul/Documents/Projects - GIT/Agents/Decompose KG from Code/pythonProject/CoderAssistants/DBinst/"
        directory = os.path.join(base_path,info_type)
        if not os.path.exists(directory):
            os.makedirs(directory)

        dbconnection = os.path.join(directory,f"{db_name}.db")

        # Connect to the SQLite database
        self.connection = sqlite3.connect(dbconnection)
        self.cursor = self.connection.cursor()

    def create_table(self, tableSchema: dict):
        """
        Create a table in the SQLite database.

        Args:
            table_schema (dict): Dictionary containing table schema information.
        """
        tableName = tableSchema['tableName']

        # Construct column definitions
        collist = []
        for col, md in tableSchema['columns'].items():
            collist.append(col + " " + " ".join(md))

        # Construct table creation query
        tableCreateQuery = f'''
            CREATE TABLE IF NOT EXISTS {tableName} (
                {", ".join(collist)}
            )
        '''


        # Execute the table creation query
        self.cursor.execute(tableCreateQuery)
        self.connection.commit()


    def get_data(self, tableName: str, lookupDict: dict, lookupVal: list, fetchtype = "one"):
        """
        Retrieve data from the SQLite database.

        Args:
            table_name (str): Name of the table.
            lookup_dict (dict): Dictionary containing lookup column-value pairs for filtering data (default: None).
            lookup_val (list): List of column names to retrieve (default: None).
            fetch_type (str): Type of fetch operation, 'one' or 'all' (default: 'one').

        Returns:
            tuple or list: Retrieved data.
        """
        if not len(lookupVal):
            lookupVal = ["*",]

        if not len(lookupDict):
            self.cursor.execute(f'SELECT {", ".join(lookupVal)} FROM {tableName}')

        else:
            lookupkeyslist = []
            for colname, colval in lookupDict.items():
                lookupkeyslist.append(f"lower({colname}) = '{str(colval).lower()}'")

            lookupQuery = f'''SELECT { ", ".join(lookupVal) } FROM { tableName } WHERE { " AND ".join(lookupkeyslist) }'''

            self.cursor.execute(lookupQuery)

        if fetchtype == "one":
            return self.cursor.fetchone()
        else:
            return self.cursor.fetchall()

    def post_data(self, tableName: str, insertlist: list[dict[str,str]]) -> None:
        """
        Insert data into the SQLite database.

        Args:
            table_name (str): Name of the table.
            insert_list (list): List of dictionaries containing data to insert.
        """
        for records_dict in insertlist:
            colList = records_dict.keys()
            placehldr = ",".join(["?"]*len(records_dict.keys()))
            colval = tuple(map(str,records_dict.values()))
            self.cursor.execute(f'Insert into {tableName}(`{"`, `".join(colList)}`) values ({placehldr})', colval)

        self.connection.commit()


    def update_data(self, tableName: str, matchVal: dict[str,str], updateVal: dict[str,str]) -> None:
        """
        Update data in the SQLite database.

        Args:
            tableName (str): Name of the table to update.
            matchVal (dict): Dictionary containing column-value pairs for matching rows.
            updateVal (dict): Dictionary containing column-value pairs to update.

        Raises:
            ValueError: If update values are not provided.
        """
        if not len(updateVal):
            raise "Update values not provided"

        updateList = []
        for col, vals in updateVal.items():
            updateList.append(f"{col} = {vals}")

        updateQuery = f'''
        UPDATE {tableName}
        SET {", ".join(updateList)}
        '''

        if len(matchVal):
            matchList = []
            for col, vals in matchVal.items():
                matchList.append(f"{col} = {vals}")

            updateQuery = f'''
            {updateQuery}
            WHERE {" AND ".join(matchList)}
            '''

        self.cursor.execute(updateQuery)
        self.connection.commit()


    def delete_data(self, tableName: str, lookupDict: dict):
        """
        Placeholder method for deleting data from the SQLite database.
        """
        deleteQuery = f'''
        DELETE 
        FROM {tableName}
        '''

        if len(lookupDict):
            lookupList = []
            for col, vals in lookupDict.items():
                lookupList.append(f"{col} = '{vals}'")

            deleteQuery = f'''
            {deleteQuery}
            WHERE {" AND ".join(lookupList)}
            '''

        self.cursor.execute(deleteQuery)
        self.connection.commit()


# --------------------------------------------------------------------

class cachefunc:
    def __init__(self):
        """
        Initializes an instance of cachefunc class.
        """
        # Establish connection to the SQLite database
        self.info_type = "cache"
        self.dbName = "memoize"
        self.DBObj = accessDB(self.info_type, self.dbName)
        self.table_schema = {
            'tableName' : 'cache',
            'columns' : {
                'key': ['TEXT', 'PRIMARY KEY'],
                'value': ['TEXT', '']
            }
        }

    def create_cache_table(self):
        """
        Creates the cache table if it doesn't already exist.
        """
        self.DBObj.create_table(self.table_schema)

    def memoize(self, func):
        """
        Memoization decorator function.

        Args:
            func (function): The function to be memoized.

        Returns:
            function: The wrapper function for memoization.
        """

        def wrapper(*args, **kwargs):
            # Create cache table of not exists
            self.create_cache_table()
            # Get module and file path of the function
            module = inspect.getmodule(func)
            file_path = module.__file__ if module else ''
            # Create a unique key based on file path, function name, arguments, and keyword arguments
            key = (file_path, func.__qualname__, args[1:], str(kwargs))
            key = str(key).encode('utf-8')

            hasher = hashlib.sha256()
            hasher.update(key)
            key = hasher.hexdigest()

            # Check if the key exists in the cache table
            result = self.DBObj.get_data(self.table_schema["tableName"], {"key": str(key)}, ["value"])

            if result is not None:
                # Return the cached result if found
                try:
                    return eval(result[0])
                except:
                    return result[0]
            else:
                # Call the original function if the result is not in the cache
                result = func(*args, **kwargs)
                # Insert the result into the cache table

                vals_list = [
                    {
                        "key": str(key),
                        "value": str(result)
                    }
                ]
                self.DBObj.post_data(self.table_schema["tableName"], vals_list)

                return result

        return wrapper

    def close(self):
        """
        Closes the database connection.
        """
        self.connection.close()

# --------------------------------------------------------------------