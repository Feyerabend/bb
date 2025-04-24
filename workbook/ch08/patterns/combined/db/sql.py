# -*- coding: utf-8 -*-

# This module provides a lightweight SQL-like database that operates in memory
# using Binary Search Trees for efficient data storage and retrieval.

# Design patterns used:
# - Strategy Pattern: For query execution strategies
# - Factory Pattern: For creating query objects
# - Singleton Pattern: For database instance
# - Composite Pattern: For complex condition evaluation 
# - Iterator Pattern: For traversing BST nodes
# - Observer Pattern: For database event notifications

from __future__ import annotations

import re
import operator
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Iterator #Tuple, Callable, Union, Set


class DatabaseEventType(Enum):
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    SELECT = "select"
    ERROR = "error"


@dataclass
class DatabaseEvent:
    event_type: DatabaseEventType
    table_name: str
    data: Any = None
    message: str = ""


class DatabaseObserver(ABC):
    @abstractmethod
    def update(self, event: DatabaseEvent) -> None:
        pass


class DatabaseSubject(ABC):
    def __init__(self) -> None:
        self._observers: List[DatabaseObserver] = []
    
    def attach(self, observer: DatabaseObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: DatabaseObserver) -> None:
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
    
    def notify(self, event: DatabaseEvent) -> None:
        for observer in self._observers:
            observer.update(event)


class ValueType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"


class ValueConverter:
    @staticmethod
    def auto_cast(value: str) -> Any:
        if value.startswith(("'", '"')) and value.endswith(("'", '"')):
            return value[1:-1]
        
        try:
            return int(value)
        except ValueError:
            pass
        
        try:
            return float(value)
        except ValueError:
            pass
        
        return value


class BSTNode:
    def __init__(self, key: Any, row: Dict[str, Any]) -> None:
        self.key = key
        self.row = row
        self.left: Optional[BSTNode] = None
        self.right: Optional[BSTNode] = None


class BSTIterator:
    def __init__(self, root: Optional[BSTNode]) -> None:
        self.stack: List[BSTNode] = []
        self._push_left(root)
    
    def _push_left(self, node: Optional[BSTNode]) -> None:
        while node:
            self.stack.append(node)
            node = node.left
    
    def __iter__(self) -> Iterator[BSTNode]:
        return self
    
    def __next__(self) -> BSTNode:
        if not self.stack:
            raise StopIteration
        
        node = self.stack.pop()
        self._push_left(node.right)
        return node


class BSTTable:
    def __init__(self, key_column: str) -> None:
        self.root: Optional[BSTNode] = None
        self.key_column = key_column
        self.column_types: Dict[str, ValueType] = {}
    
    def insert(self, row: Dict[str, Any]) -> None:
        if self.key_column not in row:
            raise ValueError(f"Key column '{self.key_column}' not found in row")
        
        key = row[self.key_column]
        self.root = self._insert(self.root, key, row)
    
    def _insert(self, node: Optional[BSTNode], key: Any, row: Dict[str, Any]) -> BSTNode:
        if node is None:
            return BSTNode(key, row)
        
        if key < node.key:
            node.left = self._insert(node.left, key, row)
        elif key > node.key:
            node.right = self._insert(node.right, key, row)
        else:
            raise ValueError(f"Duplicate key: {key}")
        
        return node

    def iterator(self) -> BSTIterator:
        return BSTIterator(self.root)
    
    def select(self, condition: Optional[Condition] = None) -> List[Dict[str, Any]]:
        results = []
        
        for node in self.iterator():
            if not condition or condition.evaluate(node.row):
                results.append(node.row.copy())
        
        return results
    
    def update(self, updates: Dict[str, Any], condition: Optional[Condition] = None) -> int:
        updated_count = 0
        
        for node in self.iterator():
            if not condition or condition.evaluate(node.row):
                for k, v in updates.items():
                    node.row[k] = v
                updated_count += 1
        
        return updated_count
    
    def delete(self, condition: Optional[Condition] = None) -> int:
        if not condition:
            count = self.count()
            self.root = None
            return count
        
        keys_to_delete = []
        for node in self.iterator():
            if condition.evaluate(node.row):
                keys_to_delete.append(node.key)
        
        for key in keys_to_delete:
            self.root = self._delete(self.root, key)
        
        return len(keys_to_delete)
    
    def _delete(self, node: Optional[BSTNode], key: Any) -> Optional[BSTNode]:
        if node is None:
            return None
        
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            
            successor = self._find_min(node.right)
            node.key, node.row = successor.key, successor.row.copy()
            node.right = self._delete(node.right, successor.key)
        
        return node
    
    def _find_min(self, node: BSTNode) -> BSTNode:
        current = node
        while current.left:
            current = current.left
        return current
    
    def count(self) -> int:
        count = 0
        for _ in self.iterator():
            count += 1
        return count


class Condition(ABC):
    @abstractmethod
    def evaluate(self, row: Dict[str, Any]) -> bool:
        pass


class ComparisonCondition(Condition):
    OPERATORS = {
        '==': operator.eq,
        '!=': operator.ne,
        '>=': operator.ge,
        '<=': operator.le,
        '>': operator.gt,
        '<': operator.lt,
        'LIKE': lambda a, b: b.lower() in str(a).lower() if a and b else False,
    }
    
    def __init__(self, column: str, op_str: str, value: Any) -> None:
        if op_str not in self.OPERATORS:
            raise ValueError(f"Unsupported operator: {op_str}")
        
        self.column = column
        self.op_func = self.OPERATORS[op_str]
        self.value = value
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        if self.column not in row:
            return False
        return self.op_func(row[self.column], self.value)


class AndCondition(Condition):
    def __init__(self, left: Condition, right: Condition) -> None:
        self.left = left
        self.right = right
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        return self.left.evaluate(row) and self.right.evaluate(row)


class OrCondition(Condition):
    def __init__(self, left: Condition, right: Condition) -> None:
        self.left = left
        self.right = right
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        return self.left.evaluate(row) or self.right.evaluate(row)


class NotCondition(Condition):
    def __init__(self, condition: Condition) -> None:
        self.condition = condition
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        return not self.condition.evaluate(row)


class ConditionParser:
    def parse(self, condition_str: str) -> Optional[Condition]:
        if not condition_str or condition_str.strip() == "":
            return None

        if " AND " in condition_str.upper():
            parts = condition_str.split(" AND ", 1)
            left_str, right_str = parts[0], parts[1]
            left = self.parse(left_str)
            right = self.parse(right_str)
            return AndCondition(left, right)
        
        if " OR " in condition_str.upper():
            parts = condition_str.split(" OR ", 1)
            left_str, right_str = parts[0], parts[1]
            left = self.parse(left_str)
            right = self.parse(right_str)
            return OrCondition(left, right)
        
        if condition_str.upper().strip().startswith("NOT "):
            inner_str = condition_str[4:].strip()
            inner = self.parse(inner_str)
            return NotCondition(inner)
        
        if condition_str.strip().startswith("(") and condition_str.strip().endswith(")"):
            inner_str = condition_str.strip()[1:-1].strip()
            return self.parse(inner_str)
        
        for op_str in ComparisonCondition.OPERATORS:
            if op_str == "LIKE":
                match = re.search(r"(\w+)\s+LIKE\s+['\"](.+)['\"]", condition_str, re.IGNORECASE)
                if match:
                    column = match.group(1)
                    value = match.group(2)
                    return ComparisonCondition(column, "LIKE", value)
            elif op_str in condition_str:
                parts = condition_str.split(op_str, 1)
                if len(parts) == 2:
                    column = parts[0].strip()
                    value_str = parts[1].strip()
                    value = ValueConverter.auto_cast(value_str)
                    return ComparisonCondition(column, op_str, value)
        
        raise ValueError(f"Unsupported condition format: {condition_str}")


class Query(ABC):
    @abstractmethod
    def execute(self, tables: Dict[str, BSTTable]) -> Any:
        pass


class SelectQuery(Query):
    def __init__(self, table_name: str, columns: List[str], condition: Optional[Condition] = None) -> None:
        self.table_name = table_name
        self.columns = columns
        self.condition = condition
    
    def execute(self, tables: Dict[str, BSTTable]) -> List[Dict[str, Any]]:
        if self.table_name not in tables:
            raise ValueError(f"Table '{self.table_name}' not found")
        
        table = tables[self.table_name]
        results = table.select(self.condition)
        
        if '*' in self.columns:
            return results
        else:
            return [{k: row.get(k) for k in self.columns} for row in results]


class InsertQuery(Query):
    def __init__(self, table_name: str, row: Dict[str, Any]) -> None:
        self.table_name = table_name
        self.row = row
    
    def execute(self, tables: Dict[str, BSTTable]) -> int:
        if self.table_name not in tables:
            raise ValueError(f"Table '{self.table_name}' not found")
        
        table = tables[self.table_name]
        table.insert(self.row)
        return 1


class UpdateQuery(Query):
    def __init__(self, table_name: str, updates: Dict[str, Any], condition: Optional[Condition] = None) -> None:
        self.table_name = table_name
        self.updates = updates
        self.condition = condition
    
    def execute(self, tables: Dict[str, BSTTable]) -> int:
        if self.table_name not in tables:
            raise ValueError(f"Table '{self.table_name}' not found")
        
        table = tables[self.table_name]
        return table.update(self.updates, self.condition)


class DeleteQuery(Query):
    def __init__(self, table_name: str, condition: Optional[Condition] = None) -> None:
        self.table_name = table_name
        self.condition = condition
    
    def execute(self, tables: Dict[str, BSTTable]) -> int:
        if self.table_name not in tables:
            raise ValueError(f"Table '{self.table_name}' not found")
        
        table = tables[self.table_name]
        return table.delete(self.condition)


class CreateTableQuery(Query):
    def __init__(self, table_name: str, columns: Dict[str, ValueType], primary_key: str) -> None:
        self.table_name = table_name
        self.columns = columns
        self.primary_key = primary_key
    
    def execute(self, tables: Dict[str, BSTTable]) -> str:
        if self.table_name in tables:
            raise ValueError(f"Table '{self.table_name}' already exists")
            
        if self.primary_key not in self.columns:
            raise ValueError(f"Primary key '{self.primary_key}' not found in columns")
            
        table = BSTTable(self.primary_key)
        table.column_types = self.columns.copy()
        tables[self.table_name] = table
        return f"Table '{self.table_name}' created"


class SQLParser:
    def __init__(self) -> None:
        self.condition_parser = ConditionParser()
    
    def parse(self, query_str: str) -> Query:
        query_str = query_str.strip().rstrip(';')
        
        if query_str.upper().startswith("SELECT"):
            return self._parse_select(query_str)
        elif query_str.upper().startswith("INSERT"):
            return self._parse_insert(query_str)
        elif query_str.upper().startswith("UPDATE"):
            return self._parse_update(query_str)
        elif query_str.upper().startswith("DELETE"):
            return self._parse_delete(query_str)
        elif query_str.upper().startswith("CREATE TABLE"):
            return self._parse_create_table(query_str)
        else:
            raise ValueError(f"Unsupported SQL query: {query_str}")
    
    def _parse_select(self, query_str: str) -> SelectQuery:
        pattern = re.compile(
            r'^SELECT\s+(?P<columns>[\w\*,\s]+)\s+FROM\s+(?P<table>\w+)(\s+WHERE\s+(?P<where>.+))?$',
            re.IGNORECASE
        )
        match = pattern.match(query_str)
        if not match:
            raise ValueError(f"Invalid SELECT query: {query_str}")
        
        columns = [col.strip() for col in match.group('columns').split(',')]
        table_name = match.group('table')
        where_str = match.group('where')
        
        condition = self.condition_parser.parse(where_str) if where_str else None
        
        return SelectQuery(table_name, columns, condition)
    
    def _parse_insert(self, query_str: str) -> InsertQuery:
        pattern = re.compile(
            r"^INSERT\s+INTO\s+(?P<table>\w+)\s*\((?P<columns>[\w\s,]+)\)\s*VALUES\s*\((?P<values>.+)\)$",
            re.IGNORECASE
        )
        match = pattern.match(query_str)
        if not match:
            raise ValueError(f"Invalid INSERT query: {query_str}")
        
        table_name = match.group('table')
        columns = [c.strip() for c in match.group('columns').split(',')]
        
        value_str = match.group('values')
        values = []
        in_quotes = False
        quote_char = None
        current_value = ""
        
        for char in value_str:
            if char in ("'", '"') and (not in_quotes or char == quote_char):
                in_quotes = not in_quotes
                if in_quotes:
                    quote_char = char
                else:
                    quote_char = None
                current_value += char
            elif char == ',' and not in_quotes:
                values.append(current_value.strip())
                current_value = ""
            else:
                current_value += char
        
        if current_value:
            values.append(current_value.strip())
        
        if len(columns) != len(values):
            raise ValueError("Column count doesn't match value count")
        
        row = {}
        for i, col in enumerate(columns):
            row[col] = ValueConverter.auto_cast(values[i])
        
        return InsertQuery(table_name, row)
    
    def _parse_update(self, query_str: str) -> UpdateQuery:
        pattern = re.compile(
            r"^UPDATE\s+(?P<table>\w+)\s+SET\s+(?P<set>.+?)(\s+WHERE\s+(?P<where>.+))?$",
            re.IGNORECASE
        )
        match = pattern.match(query_str)
        if not match:
            raise ValueError(f"Invalid UPDATE query: {query_str}")
        
        table_name = match.group('table')
        set_str = match.group('set').strip()
        where_str = match.group('where')
        
        updates = {}
        for kv_str in self._split_not_in_quotes(set_str, ','):
            if '=' not in kv_str:
                raise ValueError(f"Invalid SET clause: {kv_str}")
            
            k, v = kv_str.split('=', 1)
            updates[k.strip()] = ValueConverter.auto_cast(v.strip())
        
        condition = self.condition_parser.parse(where_str) if where_str else None
        
        return UpdateQuery(table_name, updates, condition)
    
    def _parse_delete(self, query_str: str) -> DeleteQuery:
        pattern = re.compile(
            r"^DELETE\s+FROM\s+(?P<table>\w+)(\s+WHERE\s+(?P<where>.+))?$",
            re.IGNORECASE
        )
        match = pattern.match(query_str)
        if not match:
            raise ValueError(f"Invalid DELETE query: {query_str}")
        
        table_name = match.group('table')
        where_str = match.group('where')
        
        condition = self.condition_parser.parse(where_str) if where_str else None
        
        return DeleteQuery(table_name, condition)
    
    def _parse_create_table(self, query_str: str) -> CreateTableQuery:
        query_str = re.sub(r'\s+', ' ', query_str).strip()
        
        pattern = re.compile(
            r"^CREATE\s+TABLE\s+(?P<table>\w+)\s*\(\s*(?P<columns>.+)\s*\)$",
            re.IGNORECASE
        )
        match = pattern.match(query_str)
        if not match:
            raise ValueError(f"Invalid CREATE TABLE query: {query_str}")
        
        table_name = match.group('table')
        columns_str = match.group('columns')
        
        columns = {}
        primary_key = None
        
        for col_def in self._split_not_in_quotes(columns_str, ','):
            col_def = col_def.strip()
            if not col_def:
                continue
                
            col_parts = col_def.split()
            if len(col_parts) < 2:
                raise ValueError(f"Invalid column definition: {col_def}")
            
            col_name = col_parts[0]
            col_type_str = col_parts[1].upper()
            
            if col_type_str in ('INT', 'INTEGER'):
                col_type = ValueType.INTEGER
            elif col_type_str in ('FLOAT', 'REAL', 'DOUBLE'):
                col_type = ValueType.FLOAT
            else:
                col_type = ValueType.STRING
            
            columns[col_name] = col_type
            
            if 'PRIMARY' in [p.upper() for p in col_parts] and 'KEY' in [p.upper() for p in col_parts]:
                if primary_key is not None:
                    raise ValueError("Multiple primary keys are not supported")
                primary_key = col_name
        
        if not primary_key:
            primary_key = next(iter(columns))
        
        return CreateTableQuery(table_name, columns, primary_key)
    
    def _split_not_in_quotes(self, text: str, delimiter: str) -> List[str]:
        result = []
        current = ""
        in_quotes = False
        quote_char = None
        
        for char in text:
            if char in ("'", '"') and (not in_quotes or char == quote_char):
                in_quotes = not in_quotes
                if in_quotes:
                    quote_char = char
                else:
                    quote_char = None
                current += char
            elif char == delimiter and not in_quotes:
                result.append(current.strip())
                current = ""
            else:
                current += char
        
        if current:
            result.append(current.strip())
        
        return result


class Database(DatabaseSubject):
    _instance = None
    
    def __new__(cls) -> Database:
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if self._initialized:
            return
        
        super().__init__()
        self.tables: Dict[str, BSTTable] = {}
        self.parser = SQLParser()
        self._initialized = True
    
    def execute(self, query_str: str) -> Any:
        try:
            query = self.parser.parse(query_str)
            result = query.execute(self.tables)
            
            event_type = DatabaseEventType.SELECT
            if isinstance(query, InsertQuery):
                event_type = DatabaseEventType.INSERT
            elif isinstance(query, UpdateQuery):
                event_type = DatabaseEventType.UPDATE
            elif isinstance(query, DeleteQuery):
                event_type = DatabaseEventType.DELETE
            
            self.notify(DatabaseEvent(
                event_type=event_type,
                table_name=query.table_name,
                data=result
            ))
            
            return result
            
        except Exception as e:
            self.notify(DatabaseEvent(
                event_type=DatabaseEventType.ERROR,
                table_name="",
                message=str(e)
            ))
            
            raise


class DatabaseLogger(DatabaseObserver):
    def update(self, event: DatabaseEvent) -> None:
        if event.event_type == DatabaseEventType.ERROR:
            print(f"ERROR: {event.message}")
        else:
            print(f"{event.event_type.value.upper()}: {event.table_name} - {event.data}")


def main() -> None:
    db = Database()
    
    logger = DatabaseLogger()
    db.attach(logger)
    
    try:
        db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR, age INTEGER)")
        
        db.execute("INSERT INTO users (id, name, age) VALUES (1, 'Alice', 25)")
        db.execute("INSERT INTO users (id, name, age) VALUES (2, 'Bob', 30)")
        
        db.execute("UPDATE users SET age = 31 WHERE name == 'Bob'")
        
        result1 = db.execute("SELECT * FROM users")
        print("All users:", result1)
        
        result2 = db.execute("SELECT name FROM users WHERE age > 25")
        print("Users older than 25:", result2)
        
        db.execute("DELETE FROM users WHERE id == 1")
        
        result3 = db.execute("SELECT * FROM users")
        print("After delete:", result3)
        
        db.execute("INSERT INTO users (id, name, age) VALUES (3, 'Charlie', 35)")
        db.execute("INSERT INTO users (id, name, age) VALUES (4, 'Diana', 28)")
        
        result4 = db.execute("SELECT * FROM users WHERE age > 25 AND age < 35")
        print("Users between 25 and 35:", result4)
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

