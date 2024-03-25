"""
Module for parsing SQL queries. This module contains classes and methods
to parse SQL queries, extract SQL components such as tables, aliases, join conditions, and metadata

Class:
    - SQLCodeParse: Class to parse SQL queries and extract SQL components.
"""

import re
from typing import Tuple


class SQLCodeParse:
    """
    Class to parse SQL queries and extract SQL components.
    """
    def __init__(self):
        """
        Initializes an instance of SQLCodeParse class.
        """
        pass

    def __get_table_and_aliases__(self, query: str):
        """
        Extracts the main table name and its alias from the SQL query.

        Args:
            query (str): The SQL query string.

        Returns:
            tuple: A tuple containing the main table name and its alias (if available).

        Example:
            >>> generator = GenerateDD()
            >>> table_name, alias = generator.__get_table_and_aliases__(query)
        """
        # Regular expression pattern to match main table and its alias
        table_pattern = r'\bFROM\s+(\w+)(?:\s+AS\s+(\w+))?'

        # Find the main table and its alias
        table_match = re.search(table_pattern, query, re.IGNORECASE)

        if table_match:
            table_name, alias = table_match.groups()
            if alias is None:
                alias = table_name
            return table_name, alias
        else:
            return None, None

    def __get_join_keys_with_aliases__(self, query: str):
        """
        Extracts the table names, aliases, and join keys from the join conditions in the SQL query.

        Args:
            query (str): The SQL query string.

        Returns:
            list: A list of tuples, each containing the table name, alias, and join key pairs.

        Example:
            >>> generator = GenerateDD()
            >>> join_keys_with_aliases = generator.__get_join_keys_with_aliases__(query)
        """
        # Regular expression pattern to match join conditions with aliases and extract table names and their aliases
        join_pattern = r'\b(?:LEFT\s+)?(?:INNER\s+)?(?:OUTER\s+)?(?:LEFT\s+OUTER\s+)?(?:RIGHT\s+OUTER\s+)?JOIN\s+(\w+)(?:\s+AS\s+(\w+))?\s+ON\s+((?:\w+(?:\.\w+)?\s*=\s*\w+(?:\.\w+)?\s*(?:AND\s+)?)+)'

        # Find all matches of join conditions in the SQL code
        join_matches = re.findall(join_pattern, query, re.IGNORECASE)

        # Initialize list to store join keys with aliases
        join_keys_with_aliases = []

        # Extract table names, aliases, and join keys from the matches
        for match in join_matches:
            table_name, alias, key_pairs = match
            if alias is None:
                alias = table_name
            # Extract key pairs
            key_pairs = re.findall(r'(\w+(?:\.\w+)?)\s*=\s*(\w+(?:\.\w+)?)', key_pairs, re.IGNORECASE)
            join_keys_with_aliases.append((table_name, alias, key_pairs))

        return join_keys_with_aliases

    def __convert_join_conditions__(self, table_aliases, join_conditions):
        """
        Converts join conditions from aliases to actual table names.

        Args:
            table_aliases (dict): A dictionary mapping table aliases to their actual names.
            join_conditions (list): A list of tuples containing join conditions.

        Returns:
            list: A list of lists, each containing the table names, their aliases, and join key pairs.

        Example:
            >>> table_aliases = {'t1': 'table1', 't2': 'table2'}
            >>> join_conditions = [('t1.column1', 't2.column2')]
            >>> converted_conditions = convert_join_conditions(table_aliases, join_conditions)
        """
        tables = {v: k for k, v in table_aliases.items()}  # Reverse the alias mapping
        result = []
        for join_cond in join_conditions:
            if isinstance(join_cond, tuple):  # If join condition is a tuple
                table1_alias, table2_alias = join_cond[0].split('.')[0], join_cond[1].split('.')[0]
                table1_name = table_aliases.get(table1_alias, table1_alias)
                table2_name = table_aliases.get(table2_alias, table2_alias)
                result.append([table1_name, table2_name, [(join_cond[0], join_cond[1])]])

            elif isinstance(join_cond, str):  # If join condition is a string
                table_alias, column_alias = join_cond.split('.')[0], join_cond.split('.')[1]
                table_name = table_aliases.get(table_alias, table_alias)
                result.append([table_name, tables[table_name], [(join_cond, join_cond)]])

        return result

    def get_sql_components(self, query: str) -> Tuple(dict[str,str],list):
        """
        Extracts SQL components including tables, aliases, and refined join conditions from the SQL query.

        Args:
            query (str): The SQL query string.

        Returns:
            tuple: A tuple containing the following SQL components:
                - Table names with their aliases
                - Refined join conditions

        Example:
            >>> generator = SQLCodeParse()
            >>> tables, join_conditions = generator.get_sql_components(query)
        """

        ## Getting Joining conditions
        # Extract table names and aliases
        table_w_aliases = self.__get_table_and_aliases__(query)
        # Extract raw join conditions
        join_conditions = self.__get_join_keys_with_aliases__(query)
        # Convert and refine join conditions
        refined_join_conditions = self.__convert_join_conditions__(table_w_aliases, join_conditions)

        return table_w_aliases, refined_join_conditions

# ------------------------------------------------------------------------------------------
