from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import numpy as np
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.models.datasource import DataSource, DataSourceType
from app.services.database_connector import DatabaseConnector
from app.services.file_upload import FileUploadService


class AggregationFunction(str, Enum):
    """Supported aggregation functions."""
    SUM = "sum"
    AVG = "avg"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    STD = "std"
    VAR = "var"
    MEDIAN = "median"


class TimeInterval(str, Enum):
    """Time intervals for time-series aggregation."""
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class FilterOperator(str, Enum):
    """Filter operators for WHERE clauses."""
    EQ = "eq"  # equals
    NE = "ne"  # not equals
    GT = "gt"  # greater than
    GTE = "gte"  # greater than or equal
    LT = "lt"  # less than
    LTE = "lte"  # less than or equal
    LIKE = "like"  # like pattern
    IN = "in"  # in list
    NOT_IN = "not_in"  # not in list
    IS_NULL = "is_null"  # is null
    IS_NOT_NULL = "is_not_null"  # is not null
    BETWEEN = "between"  # between two values


class QueryBuilder:
    """SQL query builder for dynamic query construction."""
    
    def __init__(self, table_name: str):
        """Initialize query builder with a table name."""
        self.table_name = table_name
        self.select_fields: List[str] = []
        self.where_conditions: List[str] = []
        self.group_by_fields: List[str] = []
        self.having_conditions: List[str] = []
        self.order_by_fields: List[str] = []
        self.limit_value: Optional[int] = None
        self.offset_value: Optional[int] = None
        self.aggregations: List[Dict[str, Any]] = []
        self.joins: List[Dict[str, Any]] = []
    
    def select(self, *fields: str) -> "QueryBuilder":
        """Add fields to SELECT clause."""
        self.select_fields.extend(fields)
        return self
    
    def where(self, column: str, operator: FilterOperator, value: Any) -> "QueryBuilder":
        """Add WHERE condition."""
        condition = self._build_condition(column, operator, value)
        if condition:
            self.where_conditions.append(condition)
        return self
    
    def where_raw(self, condition: str) -> "QueryBuilder":
        """Add raw WHERE condition."""
        self.where_conditions.append(condition)
        return self
    
    def group_by(self, *fields: str) -> "QueryBuilder":
        """Add fields to GROUP BY clause."""
        self.group_by_fields.extend(fields)
        return self
    
    def having(self, column: str, operator: FilterOperator, value: Any) -> "QueryBuilder":
        """Add HAVING condition (for aggregated results)."""
        condition = self._build_condition(column, operator, value)
        if condition:
            self.having_conditions.append(condition)
        return self
    
    def order_by(self, field: str, ascending: bool = True) -> "QueryBuilder":
        """Add ORDER BY clause."""
        direction = "ASC" if ascending else "DESC"
        self.order_by_fields.append(f"{field} {direction}")
        return self
    
    def limit(self, limit: int) -> "QueryBuilder":
        """Set LIMIT clause."""
        self.limit_value = limit
        return self
    
    def offset(self, offset: int) -> "QueryBuilder":
        """Set OFFSET clause."""
        self.offset_value = offset
        return self
    
    def aggregate(
        self,
        column: str,
        function: AggregationFunction,
        alias: Optional[str] = None
    ) -> "QueryBuilder":
        """Add aggregation function."""
        agg_name = alias or f"{function.value}_{column}"
        self.aggregations.append({
            "column": column,
            "function": function,
            "alias": agg_name
        })
        return self
    
    def join(
        self,
        table: str,
        on: str,
        join_type: str = "INNER"
    ) -> "QueryBuilder":
        """Add JOIN clause."""
        self.joins.append({
            "table": table,
            "on": on,
            "type": join_type
        })
        return self
    
    def _build_condition(self, column: str, operator: FilterOperator, value: Any) -> Optional[str]:
        """Build SQL condition string."""
        column_escaped = f'"{column}"'  # Escape column name
        
        if operator == FilterOperator.EQ:
            return f"{column_escaped} = {self._format_value(value)}"
        elif operator == FilterOperator.NE:
            return f"{column_escaped} != {self._format_value(value)}"
        elif operator == FilterOperator.GT:
            return f"{column_escaped} > {self._format_value(value)}"
        elif operator == FilterOperator.GTE:
            return f"{column_escaped} >= {self._format_value(value)}"
        elif operator == FilterOperator.LT:
            return f"{column_escaped} < {self._format_value(value)}"
        elif operator == FilterOperator.LTE:
            return f"{column_escaped} <= {self._format_value(value)}"
        elif operator == FilterOperator.LIKE:
            return f"{column_escaped} LIKE {self._format_value(value)}"
        elif operator == FilterOperator.IN:
            if isinstance(value, list):
                values_str = ", ".join([self._format_value(v) for v in value])
                return f"{column_escaped} IN ({values_str})"
            return None
        elif operator == FilterOperator.NOT_IN:
            if isinstance(value, list):
                values_str = ", ".join([self._format_value(v) for v in value])
                return f"{column_escaped} NOT IN ({values_str})"
            return None
        elif operator == FilterOperator.IS_NULL:
            return f"{column_escaped} IS NULL"
        elif operator == FilterOperator.IS_NOT_NULL:
            return f"{column_escaped} IS NOT NULL"
        elif operator == FilterOperator.BETWEEN:
            if isinstance(value, (list, tuple)) and len(value) == 2:
                return f"{column_escaped} BETWEEN {self._format_value(value[0])} AND {self._format_value(value[1])}"
            return None
        return None
    
    def _format_value(self, value: Any) -> str:
        """Format value for SQL query."""
        if value is None:
            return "NULL"
        elif isinstance(value, str):
            # Escape single quotes
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, (datetime, pd.Timestamp)):
            return f"'{value.isoformat()}'"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        else:
            return f"'{str(value)}'"
    
    def build(self) -> str:
        """Build the final SQL query."""
        query_parts = []
        
        # SELECT clause
        select_parts = []
        
        # Add regular fields
        if self.select_fields:
            select_parts.extend(self.select_fields)
        
        # Add aggregations
        for agg in self.aggregations:
            func_name = agg["function"].value.upper()
            column = f'"{agg["column"]}"'
            alias = f'"{agg["alias"]}"'
            select_parts.append(f"{func_name}({column}) AS {alias}")
        
        # If no fields specified, select all
        if not select_parts:
            select_parts.append("*")
        
        query_parts.append(f"SELECT {', '.join(select_parts)}")
        
        # FROM clause
        query_parts.append(f'FROM "{self.table_name}"')
        
        # JOIN clauses
        for join in self.joins:
            query_parts.append(f"{join['type']} JOIN {join['table']} ON {join['on']}")
        
        # WHERE clause
        if self.where_conditions:
            query_parts.append(f"WHERE {' AND '.join(self.where_conditions)}")
        
        # GROUP BY clause
        if self.group_by_fields:
            group_fields = [f'"{field}"' for field in self.group_by_fields]
            query_parts.append(f"GROUP BY {', '.join(group_fields)}")
        
        # HAVING clause
        if self.having_conditions:
            query_parts.append(f"HAVING {' AND '.join(self.having_conditions)}")
        
        # ORDER BY clause
        if self.order_by_fields:
            query_parts.append(f"ORDER BY {', '.join(self.order_by_fields)}")
        
        # LIMIT clause
        if self.limit_value is not None:
            query_parts.append(f"LIMIT {self.limit_value}")
        
        # OFFSET clause
        if self.offset_value is not None:
            query_parts.append(f"OFFSET {self.offset_value}")
        
        return " ".join(query_parts)


class AnalyticsEngine:
    """Analytics engine for query processing, aggregation, and data analysis."""
    
    def __init__(self):
        """Initialize the analytics engine."""
        self.db_connector = DatabaseConnector()
        self.file_upload_service = FileUploadService()
    
    def get_data(
        self,
        datasource: DataSource,
        password: Optional[str] = None,
        limit: Optional[int] = None,
        table_name: Optional[str] = None
    ) -> pd.DataFrame:
        """Get data from a data source as pandas DataFrame."""
        if datasource.type == DataSourceType.FILE:
            # Load from file
            if not datasource.file_path:
                raise ValueError("File path not found for file data source")
            df, _ = self.file_upload_service.parse_file(datasource.file_path)
            if limit:
                df = df.head(limit)
            return df
        
        elif datasource.type in [DataSourceType.POSTGRESQL, DataSourceType.MYSQL]:
            # Load from database
            if not datasource.database_name:
                raise ValueError("Database name not found for database data source")
            
            # Get table name from parameter, connection config, or raise error
            if not table_name and datasource.connection_config:
                table_name = datasource.connection_config.get("table_name")
            
            if not table_name:
                raise ValueError("Table name must be specified for database data sources")
            
            query = f'SELECT * FROM "{table_name}"'
            df = self.db_connector.execute_query_dataframe(
                datasource=datasource,
                query=query,
                password=password,
                limit=limit
            )
            return df
        
        else:
            raise ValueError(f"Unsupported data source type: {datasource.type}")
    
    def execute_query(
        self,
        datasource: DataSource,
        query: str,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a SQL query on a database data source."""
        if datasource.type not in [DataSourceType.POSTGRESQL, DataSourceType.MYSQL]:
            raise ValueError("SQL queries can only be executed on database data sources")
        
        return self.db_connector.execute_query(
            datasource=datasource,
            query=query,
            password=password
        )
    
    def aggregate_data(
        self,
        df: pd.DataFrame,
        group_by: Optional[List[str]] = None,
        aggregations: Optional[Dict[str, List[AggregationFunction]]] = None
    ) -> pd.DataFrame:
        """Perform data aggregation on a DataFrame."""
        if aggregations is None:
            aggregations = {}
        
        if group_by:
            # Group by specified columns
            grouped = df.groupby(group_by)
            
            # Apply aggregations
            agg_dict = {}
            for column, functions in aggregations.items():
                if column not in df.columns:
                    continue
                
                for func in functions:
                    func_name = func.value
                    if func_name == "sum":
                        agg_dict[column] = "sum"
                    elif func_name == "avg":
                        agg_dict[column] = "mean"
                    elif func_name == "count":
                        agg_dict[column] = "count"
                    elif func_name == "min":
                        agg_dict[column] = "min"
                    elif func_name == "max":
                        agg_dict[column] = "max"
                    elif func_name == "std":
                        agg_dict[column] = "std"
                    elif func_name == "var":
                        agg_dict[column] = "var"
                    elif func_name == "median":
                        agg_dict[column] = "median"
            
            if agg_dict:
                result = grouped.agg(agg_dict)
                result = result.reset_index()
            else:
                result = grouped.size().reset_index(name="count")
        else:
            # No grouping, aggregate entire DataFrame
            result = pd.DataFrame()
            for column, functions in aggregations.items():
                if column not in df.columns:
                    continue
                
                for func in functions:
                    func_name = func.value
                    if func_name == "sum":
                        result[f"{column}_sum"] = [df[column].sum()]
                    elif func_name == "avg":
                        result[f"{column}_avg"] = [df[column].mean()]
                    elif func_name == "count":
                        result[f"{column}_count"] = [df[column].count()]
                    elif func_name == "min":
                        result[f"{column}_min"] = [df[column].min()]
                    elif func_name == "max":
                        result[f"{column}_max"] = [df[column].max()]
                    elif func_name == "std":
                        result[f"{column}_std"] = [df[column].std()]
                    elif func_name == "var":
                        result[f"{column}_var"] = [df[column].var()]
                    elif func_name == "median":
                        result[f"{column}_median"] = [df[column].median()]
        
        return result
    
    def filter_data(
        self,
        df: pd.DataFrame,
        filters: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """Apply filters to a DataFrame."""
        result = df.copy()
        
        for filter_item in filters:
            column = filter_item.get("column")
            operator = filter_item.get("operator")
            value = filter_item.get("value")
            
            if column not in result.columns:
                continue
            
            if operator == FilterOperator.EQ.value:
                result = result[result[column] == value]
            elif operator == FilterOperator.NE.value:
                result = result[result[column] != value]
            elif operator == FilterOperator.GT.value:
                result = result[result[column] > value]
            elif operator == FilterOperator.GTE.value:
                result = result[result[column] >= value]
            elif operator == FilterOperator.LT.value:
                result = result[result[column] < value]
            elif operator == FilterOperator.LTE.value:
                result = result[result[column] <= value]
            elif operator == FilterOperator.LIKE.value:
                result = result[result[column].astype(str).str.contains(value, na=False, regex=False)]
            elif operator == FilterOperator.IN.value:
                if isinstance(value, list):
                    result = result[result[column].isin(value)]
            elif operator == FilterOperator.NOT_IN.value:
                if isinstance(value, list):
                    result = result[~result[column].isin(value)]
            elif operator == FilterOperator.IS_NULL.value:
                result = result[result[column].isna()]
            elif operator == FilterOperator.IS_NOT_NULL.value:
                result = result[result[column].notna()]
            elif operator == FilterOperator.BETWEEN.value:
                if isinstance(value, (list, tuple)) and len(value) == 2:
                    result = result[(result[column] >= value[0]) & (result[column] <= value[1])]
        
        return result
    
    def sort_data(
        self,
        df: pd.DataFrame,
        sort_by: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """Sort DataFrame by specified columns."""
        columns = [item["column"] for item in sort_by]
        ascending = [item.get("ascending", True) for item in sort_by]
        
        # Filter out columns that don't exist
        valid_sort = []
        valid_ascending = []
        for i, col in enumerate(columns):
            if col in df.columns:
                valid_sort.append(col)
                valid_ascending.append(ascending[i])
        
        if valid_sort:
            return df.sort_values(by=valid_sort, ascending=valid_ascending)
        return df
    
    def process_time_series(
        self,
        df: pd.DataFrame,
        time_column: str,
        interval: TimeInterval,
        aggregations: Optional[Dict[str, List[AggregationFunction]]] = None,
        group_by: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Process time-series data with time-based aggregation."""
        if time_column not in df.columns:
            raise ValueError(f"Time column '{time_column}' not found in data")
        
        # Convert time column to datetime if not already
        df[time_column] = pd.to_datetime(df[time_column], errors="coerce")
        
        # Drop rows with invalid time values
        df = df.dropna(subset=[time_column])
        
        # Set time column as index
        df_indexed = df.set_index(time_column)
        
        # Resample based on interval
        if interval == TimeInterval.SECOND:
            freq = "S"
        elif interval == TimeInterval.MINUTE:
            freq = "T"
        elif interval == TimeInterval.HOUR:
            freq = "H"
        elif interval == TimeInterval.DAY:
            freq = "D"
        elif interval == TimeInterval.WEEK:
            freq = "W"
        elif interval == TimeInterval.MONTH:
            freq = "M"
        elif interval == TimeInterval.QUARTER:
            freq = "Q"
        elif interval == TimeInterval.YEAR:
            freq = "Y"
        else:
            freq = "D"
        
        # Group by additional columns if specified
        if group_by:
            # Verify all group_by columns exist
            valid_group_by = [col for col in group_by if col in df_indexed.columns]
            if valid_group_by:
                grouped = df_indexed.groupby([pd.Grouper(freq=freq)] + valid_group_by)
            else:
                grouped = df_indexed.resample(freq)
        else:
            grouped = df_indexed.resample(freq)
        
        # Apply aggregations
        if aggregations:
            agg_dict = {}
            for column, functions in aggregations.items():
                if column not in df_indexed.columns:
                    continue
                
                for func in functions:
                    func_name = func.value
                    alias = f"{column}_{func_name}"
                    if func_name == "sum":
                        agg_dict[column] = "sum"
                    elif func_name == "avg":
                        agg_dict[column] = "mean"
                    elif func_name == "count":
                        agg_dict[column] = "count"
                    elif func_name == "min":
                        agg_dict[column] = "min"
                    elif func_name == "max":
                        agg_dict[column] = "max"
                    elif func_name == "std":
                        agg_dict[column] = "std"
                    elif func_name == "var":
                        agg_dict[column] = "var"
                    elif func_name == "median":
                        agg_dict[column] = "median"
            
            if agg_dict:
                result = grouped.agg(agg_dict)
            else:
                result = grouped.size().to_frame(name="count")
        else:
            # Default: count
            result = grouped.size().to_frame(name="count")
        
        result = result.reset_index()
        return result
    
    def optimize_query(self, query: str) -> str:
        """Optimize SQL query for better performance."""
        # Basic query optimization
        query_upper = query.upper().strip()
        
        # Remove unnecessary whitespace
        query = " ".join(query.split())
        
        # Add LIMIT if SELECT without LIMIT and no aggregation
        if "SELECT" in query_upper and "LIMIT" not in query_upper:
            # Check if it's a simple SELECT (not a subquery or complex query)
            if "GROUP BY" not in query_upper and "UNION" not in query_upper:
                # Add a reasonable default limit for safety
                if "OFFSET" in query_upper:
                    # Insert LIMIT before OFFSET
                    query = query.replace("OFFSET", "LIMIT 1000 OFFSET")
                else:
                    query += " LIMIT 1000"
        
        # Suggest index usage hints (database-specific, would need actual implementation)
        # For now, just return the cleaned query
        
        return query
    
    def analyze_query_plan(
        self,
        datasource: DataSource,
        query: str,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze query execution plan for optimization."""
        if datasource.type not in [DataSourceType.POSTGRESQL, DataSourceType.MYSQL]:
            raise ValueError("Query plan analysis only available for database data sources")
        
        try:
            # Get EXPLAIN query
            if datasource.type == DataSourceType.POSTGRESQL:
                explain_query = f"EXPLAIN ANALYZE {query}"
            else:  # MySQL
                explain_query = f"EXPLAIN {query}"
            
            result = self.db_connector.execute_query(
                datasource=datasource,
                query=explain_query,
                password=password
            )
            
            return {
                "success": True,
                "query_plan": result.get("data", []),
                "original_query": query
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original_query": query
            }
    
    def build_query(
        self,
        table_name: str
    ) -> QueryBuilder:
        """Create a new query builder instance."""
        return QueryBuilder(table_name)
