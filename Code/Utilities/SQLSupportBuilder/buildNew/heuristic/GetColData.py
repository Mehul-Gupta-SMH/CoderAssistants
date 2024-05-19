import re

def extract_ddl_info(sql_ddl):
    columns = []
    primary_key = None
    foreign_keys = []

    # Regular expressions for extracting column name, data type, primary key, and foreign key
    column_pattern = re.compile(r'(\w+)\s+(\w+(?:\(\d+(?:,\d+)?\))?)\s*(?:(NOT\s+NULL)|(NULL))?\s*(?:DEFAULT\s*(\w+))?\s*(?:(PRIMARY KEY)|(FOREIGN KEY\s*\((\w+)\)\s*REFERENCES\s*(\w+)\s*\((\w+)\)))?', re.IGNORECASE)

    # Extract information for each column
    for match in column_pattern.finditer(sql_ddl):
        column_name = match.group(1)
        data_type = match.group(2)
        is_primary_key = match.group(6) is not None
        is_null_allowed = match.group(3) is not None
        default_value = match.group(5)
        referenced_table = match.group(8)
        referenced_column = match.group(9)

        columns.append({
            'name': column_name,
            'data_type': data_type,
            'primary_key': is_primary_key,
            'foreign_key': (referenced_table, referenced_column) if referenced_table else None,
            'is_null_allowed': is_null_allowed,
            'default_value': default_value
        })

        if is_primary_key:
            primary_key = column_name
        elif referenced_table:
            foreign_keys.append((column_name, referenced_table, referenced_column))

    return columns

# # Example SQL DDL statement
# sql_ddl = """
# CREATE TABLE Product (
#     ProductID INT PRIMARY KEY,
#     Name VARCHAR(100) NOT NULL DEFAULT 'Unknown',
#     Category VARCHAR(50),
#     Price DECIMAL(10, 2) CHECK (Price >= 0),
#     StockQuantity INT DEFAULT 0 CHECK (StockQuantity >= 0),
#     ExpiryDate DATE DEFAULT CURRENT_DATE,
#     CONSTRAINT CHK_Category CHECK (Category IN ('Electronics', 'Clothing', 'Food', 'Books')),
#     CONSTRAINT CHK_ExpiryDate CHECK (ExpiryDate > CURRENT_DATE),
#     CONSTRAINT CHK_Product UNIQUE (Name, Category),
#     CONSTRAINT FK_SupplierID FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID) ON DELETE SET NULL
# );
# """
#
# columns = extract_ddl_info(sql_ddl)
#
# print("Columns:")
# for column in columns:
#     print(column)
