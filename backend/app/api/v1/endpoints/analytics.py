from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.datasource import DataSource
from app.models.user import User
from app.api.v1.deps import get_current_active_user
from app.services.analytics import (
    AnalyticsEngine,
    AggregationFunction,
    FilterOperator,
    TimeInterval
)


router = APIRouter()
analytics_engine = AnalyticsEngine()


# Request/Response Models
class FilterRequest(BaseModel):
    column: str
    operator: str  # FilterOperator value
    value: Any


class SortRequest(BaseModel):
    column: str
    ascending: bool = True


class AggregationRequest(BaseModel):
    column: str
    functions: List[str]  # List of AggregationFunction values


class QueryRequest(BaseModel):
    datasource_id: int
    table_name: Optional[str] = None
    filters: Optional[List[FilterRequest]] = None
    group_by: Optional[List[str]] = None
    aggregations: Optional[Dict[str, List[str]]] = None
    sort_by: Optional[List[SortRequest]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class TimeSeriesRequest(BaseModel):
    datasource_id: int
    time_column: str
    interval: str  # TimeInterval value
    table_name: Optional[str] = None
    group_by: Optional[List[str]] = None
    aggregations: Optional[Dict[str, List[str]]] = None
    filters: Optional[List[FilterRequest]] = None
    limit: Optional[int] = None


class SQLQueryRequest(BaseModel):
    datasource_id: int
    query: str
    password: Optional[str] = None


class QueryOptimizeRequest(BaseModel):
    query: str


@router.post("/query", summary="Execute analytics query")
def execute_analytics_query(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Execute an analytics query on a data source."""
    # Get data source
    datasource = db.query(DataSource).filter(
        DataSource.id == request.datasource_id,
        DataSource.owner_id == current_user.id
    ).first()
    
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )
    
    try:
        # Get data
        df = analytics_engine.get_data(datasource, limit=request.limit, table_name=request.table_name)
        
        # Apply filters
        if request.filters:
            filter_dicts = [f.model_dump() for f in request.filters]
            df = analytics_engine.filter_data(df, filter_dicts)
        
        # Apply aggregations
        if request.aggregations or request.group_by:
            # Convert string function names to AggregationFunction enum
            agg_dict = {}
            if request.aggregations:
                for col, func_names in request.aggregations.items():
                    agg_dict[col] = [AggregationFunction(f) for f in func_names]
            
            df = analytics_engine.aggregate_data(
                df,
                group_by=request.group_by,
                aggregations=agg_dict if agg_dict else None
            )
        
        # Apply sorting
        if request.sort_by:
            sort_dicts = [s.model_dump() for s in request.sort_by]
            df = analytics_engine.sort_data(df, sort_dicts)
        
        # Apply limit and offset
        if request.offset:
            df = df.iloc[request.offset:]
        if request.limit:
            df = df.head(request.limit)
        
        # Convert to response format
        return {
            "success": True,
            "columns": df.columns.tolist(),
            "data": df.to_dict(orient="records"),
            "row_count": len(df),
            "total_rows": len(df)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query execution failed: {str(e)}"
        )


@router.post("/timeseries", summary="Process time-series data")
def process_time_series(
    request: TimeSeriesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Process time-series data with time-based aggregation."""
    # Get data source
    datasource = db.query(DataSource).filter(
        DataSource.id == request.datasource_id,
        DataSource.owner_id == current_user.id
    ).first()
    
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )
    
    try:
        # Get data
        df = analytics_engine.get_data(datasource, limit=request.limit, table_name=request.table_name)
        
        # Apply filters first
        if request.filters:
            filter_dicts = [f.model_dump() for f in request.filters]
            df = analytics_engine.filter_data(df, filter_dicts)
        
        # Convert aggregations
        agg_dict = None
        if request.aggregations:
            agg_dict = {}
            for col, func_names in request.aggregations.items():
                agg_dict[col] = [AggregationFunction(f) for f in func_names]
        
        # Process time series
        interval = TimeInterval(request.interval)
        df_result = analytics_engine.process_time_series(
            df=df,
            time_column=request.time_column,
            interval=interval,
            aggregations=agg_dict,
            group_by=request.group_by
        )
        
        # Apply limit
        if request.limit:
            df_result = df_result.head(request.limit)
        
        return {
            "success": True,
            "columns": df_result.columns.tolist(),
            "data": df_result.to_dict(orient="records"),
            "row_count": len(df_result),
            "interval": request.interval
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Time-series processing failed: {str(e)}"
        )


@router.post("/sql", summary="Execute SQL query")
def execute_sql_query(
    request: SQLQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Execute a raw SQL query on a database data source."""
    # Get data source
    datasource = db.query(DataSource).filter(
        DataSource.id == request.datasource_id,
        DataSource.owner_id == current_user.id
    ).first()
    
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )
    
    if datasource.type.value not in ["postgresql", "mysql"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SQL queries can only be executed on database data sources"
        )
    
    try:
        result = analytics_engine.execute_query(
            datasource=datasource,
            query=request.query,
            password=request.password
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SQL query execution failed: {str(e)}"
        )


@router.post("/optimize", summary="Optimize SQL query")
def optimize_query(
    request: QueryOptimizeRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Optimize a SQL query for better performance."""
    try:
        optimized_query = analytics_engine.optimize_query(request.query)
        return {
            "success": True,
            "original_query": request.query,
            "optimized_query": optimized_query
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query optimization failed: {str(e)}"
        )


@router.post("/query-plan", summary="Analyze query execution plan")
def analyze_query_plan(
    request: SQLQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Analyze the execution plan for a SQL query."""
    # Get data source
    datasource = db.query(DataSource).filter(
        DataSource.id == request.datasource_id,
        DataSource.owner_id == current_user.id
    ).first()
    
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )
    
    if datasource.type.value not in ["postgresql", "mysql"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query plan analysis only available for database data sources"
        )
    
    try:
        result = analytics_engine.analyze_query_plan(
            datasource=datasource,
            query=request.query,
            password=request.password
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query plan analysis failed: {str(e)}"
        )


@router.get("/aggregations", summary="Get available aggregation functions")
def get_aggregation_functions(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of available aggregation functions."""
    return {
        "functions": [func.value for func in AggregationFunction],
        "descriptions": {
            "sum": "Sum of values",
            "avg": "Average of values",
            "count": "Count of non-null values",
            "min": "Minimum value",
            "max": "Maximum value",
            "std": "Standard deviation",
            "var": "Variance",
            "median": "Median value"
        }
    }


@router.get("/filters", summary="Get available filter operators")
def get_filter_operators(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of available filter operators."""
    return {
        "operators": [op.value for op in FilterOperator],
        "descriptions": {
            "eq": "Equals",
            "ne": "Not equals",
            "gt": "Greater than",
            "gte": "Greater than or equal",
            "lt": "Less than",
            "lte": "Less than or equal",
            "like": "Like pattern (use % for wildcards)",
            "in": "In list",
            "not_in": "Not in list",
            "is_null": "Is null",
            "is_not_null": "Is not null",
            "between": "Between two values"
        }
    }


@router.get("/intervals", summary="Get available time intervals")
def get_time_intervals(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of available time intervals for time-series processing."""
    return {
        "intervals": [interval.value for interval in TimeInterval],
        "descriptions": {
            "second": "Aggregate by second",
            "minute": "Aggregate by minute",
            "hour": "Aggregate by hour",
            "day": "Aggregate by day",
            "week": "Aggregate by week",
            "month": "Aggregate by month",
            "quarter": "Aggregate by quarter",
            "year": "Aggregate by year"
        }
    }
