import re

from Code.Utilities.SQLSupportBuilder.GetColData import extract_ddl_info

class TableMetadata:

    def __init__(self, TableDDL, TableQuery):

        self.TableName = None
        self.TableDDL = TableDDL
        self.TableQuery = TableQuery
        self.TableColMetadata = None

    def getTableName(self):
        # Regular expression pattern to match CREATE TABLE statement and extract table name
        table_pattern = re.compile(r'CREATE\s+TABLE\s+(\w+)\s*', re.IGNORECASE)

        # Search for table name in the SQL DDL
        match = table_pattern.search(self.TableDDL)
        if match:
            self.TableName = match.group(1)
        else:
            raise LookupError("Can't extract Table Name")

    def getColumnMetadata(self):
        self.TableColMetadata = extract_ddl_info(self.TableDDL)

    def getTableDesc(self):
        pass

    def getColumnDesc(self):
        pass



