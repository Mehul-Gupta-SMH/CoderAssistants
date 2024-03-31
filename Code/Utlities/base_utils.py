import yaml
import os
import functools
import logging
import sqlite3
import time
import inspect


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
            r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\Code\Utlities\Configs\config_paths.yaml",
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


class cachefunc:
    def __init__(self):
        """
        Initializes an instance of cachefunc class.
        """
        # Establish connection to the SQLite database
        self.connection = sqlite3.connect(
            r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\cache\memoize.db")
        self.cursor = self.connection.cursor()

    def create_cache_table(self):
        """
        Creates the cache table if it doesn't already exist.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value DOUBLE
            )
        ''')
        self.connection.commit()

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
            key = (file_path, func.__qualname__, args[1:], kwargs)
            # Check if the key exists in the cache table
            self.cursor.execute('SELECT value FROM cache WHERE key = ?', (str(key),))
            result = self.cursor.fetchone()

            if result is not None:
                # Return the cached result if found
                return result[0]
            else:
                # Call the original function if the result is not in the cache
                result = func(*args, **kwargs)
                # Insert the result into the cache table
                self.cursor.execute('Insert into cache(key, value) values (?,?)', (str(key), str(result)))
                # Commit changes to the database
                self.connection.commit()
                return result

        return wrapper

    def close(self):
        """
        Closes the database connection.
        """
        self.connection.close()
