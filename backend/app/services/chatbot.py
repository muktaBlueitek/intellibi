from typing import Dict, Any, Optional, List
from datetime import datetime
import time
import json
import statistics
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.schema import BaseMessage, HumanMessage, AIMessage
import pandas as pd
import numpy as np

from app.core.config import settings
from app.models.chatbot import Conversation, ChatMessage, QueryHistory
from app.models.datasource import DataSource, DataSourceType
from app.models.user import User
from app.services.analytics import AnalyticsEngine


class ChatbotService:
    """Service for AI-powered chatbot functionality."""
    
    def __init__(self):
        """Initialize the chatbot service."""
        self.llm = self._initialize_llm()
        self.analytics_engine = AnalyticsEngine()
        self._sql_prompt_template = self._create_sql_prompt_template()
        self._response_prompt_template = self._create_response_prompt_template()
    
    def _initialize_llm(self):
        """Initialize LLM based on configuration."""
        provider = settings.LLM_PROVIDER.lower()
        
        if provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
            return ChatOpenAI(
                model=settings.LLM_MODEL,
                temperature=settings.CHATBOT_TEMPERATURE,
                api_key=settings.OPENAI_API_KEY
            )
        elif provider == "ollama":
            base_url = settings.LLM_BASE_URL or "http://localhost:11434"
            return Ollama(
                model=settings.LLM_MODEL,
                base_url=base_url,
                temperature=settings.CHATBOT_TEMPERATURE
            )
        else:
            # Default to OpenAI
            return ChatOpenAI(
                model=settings.LLM_MODEL or "gpt-3.5-turbo",
                temperature=settings.CHATBOT_TEMPERATURE
            )
    
    def _create_sql_prompt_template(self) -> ChatPromptTemplate:
        """Create prompt template for SQL query generation."""
        system_template = """You are a SQL query expert. Your task is to convert natural language questions into SQL queries.

Available database information:
{schema_info}

SQL Dialect: {sql_dialect}

Rules:
1. Only generate valid SQL SELECT queries
2. Use proper table and column names from the schema
3. Include appropriate WHERE, GROUP BY, ORDER BY clauses as needed
4. Do not use INSERT, UPDATE, DELETE, or DROP statements
5. If the question is ambiguous or unclear, ask for clarification
6. Return ONLY the SQL query, no explanations

Examples:
- "Show me all users" -> SELECT * FROM users
- "Count orders by status" -> SELECT status, COUNT(*) as count FROM orders GROUP BY status
- "Top 10 products by sales" -> SELECT * FROM products ORDER BY sales DESC LIMIT 10
"""

        human_template = """Question: {question}

Conversation history:
{conversation_history}

Generate the SQL query:"""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    def _create_response_prompt_template(self) -> ChatPromptTemplate:
        """Create prompt template for generating natural language responses."""
        system_template = """You are a helpful data analyst assistant. Your task is to explain query results in a clear, natural language format.

Guidelines:
1. Summarize the key findings from the data
2. Highlight important numbers or trends
3. Keep responses concise but informative
4. If there are errors, explain them clearly
5. Suggest what visualizations might be helpful
"""

        human_template = """Query: {query}

Query Results:
{query_results}

Generate a helpful response explaining these results:"""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    def _get_schema_info(self, datasource: DataSource, db: Session) -> str:
        """Get schema information for a datasource."""
        schema_info = []
        
        if datasource.type == DataSourceType.FILE:
            # For file datasources, get metadata from connection_config
            if datasource.connection_config:
                metadata = datasource.connection_config.get("metadata", {})
                columns = metadata.get("columns", [])
                if columns:
                    schema_info.append(f"Table: {datasource.name or 'data'}")
                    schema_info.append(f"Columns: {', '.join(columns)}")
        elif datasource.type in [DataSourceType.POSTGRESQL, DataSourceType.MYSQL]:
            # For database datasources, try to get table schema
            try:
                from app.services.database_connector import DatabaseConnector
                connector = DatabaseConnector()
                engine = connector.create_engine(datasource)
                
                # Get table name from connection_config or use a default
                table_name = None
                if datasource.connection_config:
                    table_name = datasource.connection_config.get("table_name")
                
                if table_name:
                    from sqlalchemy import inspect
                    inspector = inspect(engine)
                    columns = inspector.get_columns(table_name)
                    column_names = [col["name"] for col in columns]
                    schema_info.append(f"Table: {table_name}")
                    schema_info.append(f"Columns: {', '.join(column_names)}")
            except Exception as e:
                schema_info.append(f"Database: {datasource.database_name}")
                schema_info.append(f"Note: Could not retrieve schema details - {str(e)}")
        
        return "\n".join(schema_info) if schema_info else "No schema information available"
    
    def _get_sql_dialect(self, datasource: Optional[DataSource]) -> str:
        """Get SQL dialect for datasource."""
        if not datasource:
            return "PostgreSQL"
        
        if datasource.type == DataSourceType.POSTGRESQL:
            return "PostgreSQL"
        elif datasource.type == DataSourceType.MYSQL:
            return "MySQL"
        else:
            return "PostgreSQL"  # Default
    
    def get_conversation_context(
        self,
        conversation_id: int,
        db: Session,
        limit: Optional[int] = None
    ) -> List[BaseMessage]:
        """Retrieve conversation context (message history)."""
        limit = limit or settings.CHATBOT_MAX_CONTEXT_MESSAGES
        
        messages = db.query(ChatMessage)\
            .filter(ChatMessage.conversation_id == conversation_id)\
            .order_by(ChatMessage.created_at.desc())\
            .limit(limit)\
            .all()
        
        # Reverse to get chronological order
        messages = list(reversed(messages))
        
        context = []
        for msg in messages:
            if msg.role == "user":
                context.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                context.append(AIMessage(content=msg.content))
        
        return context
    
    def convert_query_to_sql(
        self,
        question: str,
        datasource: Optional[DataSource],
        conversation_history: List[BaseMessage],
        db: Session
    ) -> str:
        """Convert natural language query to SQL."""
        schema_info = self._get_schema_info(datasource, db) if datasource else "No datasource specified"
        sql_dialect = self._get_sql_dialect(datasource)
        
        # Format conversation history
        history_text = ""
        if conversation_history:
            history_parts = []
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                if isinstance(msg, HumanMessage):
                    history_parts.append(f"User: {msg.content}")
                elif isinstance(msg, AIMessage):
                    history_parts.append(f"Assistant: {msg.content}")
            history_text = "\n".join(history_parts)
        
        # Create chain and generate SQL
        chain = LLMChain(llm=self.llm, prompt=self._sql_prompt_template)
        
        result = chain.run(
            question=question,
            schema_info=schema_info,
            sql_dialect=sql_dialect,
            conversation_history=history_text or "No previous conversation"
        )
        
        # Clean up SQL query (remove markdown code blocks if present)
        sql_query = result.strip()
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        sql_query = sql_query.strip()
        
        return sql_query
    
    def execute_query(
        self,
        sql_query: str,
        datasource: DataSource,
        password: Optional[str] = None,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """Execute SQL query via analytics engine with retry logic."""
        # Validate SQL query before execution
        sql_upper = sql_query.upper().strip()
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT", "UPDATE"]
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return {
                    "success": False,
                    "error": f"Query contains dangerous keyword '{keyword}'. Only SELECT queries are allowed.",
                    "data": [],
                    "columns": [],
                    "row_count": 0,
                    "execution_time": 0
                }
        
        # Ensure it's a SELECT query
        if not sql_upper.startswith("SELECT"):
            return {
                "success": False,
                "error": "Only SELECT queries are allowed.",
                "data": [],
                "columns": [],
                "row_count": 0,
                "execution_time": 0
            }
        
        # Retry logic
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                result = self.analytics_engine.execute_query(
                    datasource=datasource,
                    query=sql_query,
                    password=password
                )
                execution_time = time.time() - start_time
                
                return {
                    "success": True,
                    "data": result.get("data", []),
                    "columns": result.get("columns", []),
                    "row_count": len(result.get("data", [])),
                    "execution_time": execution_time
                }
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries:
                    time.sleep(0.5)  # Brief delay before retry
                    continue
                else:
                    # Provide helpful error message
                    error_msg = self._format_error_message(last_error, sql_query)
                    return {
                        "success": False,
                        "error": error_msg,
                        "data": [],
                        "columns": [],
                        "row_count": 0,
                        "execution_time": 0
                    }
        
        return {
            "success": False,
            "error": str(last_error) if last_error else "Unknown error",
            "data": [],
            "columns": [],
            "row_count": 0,
            "execution_time": 0
        }
    
    def _format_error_message(self, error: str, sql_query: str) -> str:
        """Format error message with helpful suggestions."""
        error_lower = error.lower()
        
        if "syntax error" in error_lower or "invalid" in error_lower:
            return f"SQL syntax error: {error}. Please check your query syntax."
        elif "does not exist" in error_lower or "relation" in error_lower:
            return f"Table or column not found: {error}. Please verify the table and column names exist in the datasource."
        elif "permission" in error_lower or "access" in error_lower:
            return f"Permission denied: {error}. Please check datasource connection credentials."
        elif "timeout" in error_lower:
            return f"Query timeout: {error}. The query may be too complex or the datasource may be slow. Try simplifying your query."
        else:
            return f"Query execution error: {error}. Please try rephrasing your question or check the datasource configuration."
    
    def generate_response(
        self,
        query: str,
        query_results: Dict[str, Any],
        stats: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Generate natural language response from query results with enhanced interpretation."""
        if not query_results.get("success"):
            error_msg = query_results.get("error", "Unknown error")
            return f"I encountered an error while executing your query: {error_msg}. Please try rephrasing your question or check if the datasource is properly configured."
        
        # Format results for prompt
        data = query_results.get("data", [])
        row_count = query_results.get("row_count", 0)
        columns = query_results.get("columns", [])
        
        if row_count == 0:
            return "The query executed successfully but returned no results. You might want to adjust your filters or check if the data exists."
        
        # Include statistical summary if available
        stats_text = ""
        if stats:
            stats_text = "\n\nStatistical Summary:\n"
            for stat in stats[:5]:  # Limit to 5 columns
                stats_text += f"- {stat['column']}: mean={stat.get('mean', 'N/A'):.2f}, min={stat.get('min', 'N/A')}, max={stat.get('max', 'N/A')}\n"
        
        # Limit data shown in prompt (first 10 rows)
        preview_data = json.dumps(data[:10], indent=2, default=str)
        
        results_text = f"Found {row_count} rows with {len(columns)} columns.\n\nColumns: {', '.join(columns)}{stats_text}\n\nFirst few rows:\n{preview_data}"
        if row_count > 10:
            results_text += f"\n... and {row_count - 10} more rows"
        
        # Create chain and generate response
        chain = LLMChain(llm=self.llm, prompt=self._response_prompt_template)
        
        response = chain.run(
            query=query,
            query_results=results_text
        )
        
        return response.strip()
    
    def _generate_suggested_queries(self, query: str, query_results: Dict[str, Any], columns: List[str]) -> List[str]:
        """Generate suggested follow-up queries."""
        if not query_results.get("success") or not columns:
            return []
        
        suggestions = []
        
        # Generate suggestions based on query and columns
        try:
            suggestion_prompt = f"""Based on this query and available columns, suggest 3-5 useful follow-up questions:

Original query: {query}
Available columns: {', '.join(columns)}

Suggest follow-up questions that would provide additional insights. Return as a JSON array of strings."""

            response = self.llm.invoke(suggestion_prompt)
            if hasattr(response, 'content'):
                suggestion_text = response.content
            else:
                suggestion_text = str(response)
            
            # Parse JSON array
            if "[" in suggestion_text:
                if "```json" in suggestion_text:
                    suggestion_text = suggestion_text.split("```json")[1].split("```")[0].strip()
                elif "```" in suggestion_text:
                    suggestion_text = suggestion_text.split("```")[1].split("```")[0].strip()
                
                suggestions = json.loads(suggestion_text)
                if isinstance(suggestions, list):
                    return suggestions[:5]  # Limit to 5 suggestions
        except Exception:
            pass
        
        # Fallback suggestions
        if len(columns) > 1:
            suggestions = [
                f"What is the average of {columns[0]}?",
                f"Show me the top 10 by {columns[0]}",
                f"Group the data by {columns[0]}"
            ]
        
        return suggestions[:5]
    
    def _calculate_statistics(self, data: List[Dict[str, Any]], columns: List[str]) -> List[Dict[str, Any]]:
        """Calculate statistical summary for numeric columns."""
        if not data:
            return []
        
        df = pd.DataFrame(data)
        stats = []
        
        for col in columns:
            try:
                numeric_data = pd.to_numeric(df[col], errors='coerce').dropna()
                if len(numeric_data) > 0:
                    stats.append({
                        "column": col,
                        "mean": float(numeric_data.mean()),
                        "median": float(numeric_data.median()),
                        "min": float(numeric_data.min()),
                        "max": float(numeric_data.max()),
                        "std_dev": float(numeric_data.std()) if len(numeric_data) > 1 else 0.0,
                        "count": int(len(numeric_data))
                    })
            except Exception:
                continue
        
        return stats
    
    def _generate_insights(self, query: str, query_results: Dict[str, Any], stats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights from query results using LLM."""
        if not query_results.get("success") or not stats:
            return {}
        
        data = query_results.get("data", [])
        row_count = query_results.get("row_count", 0)
        
        insights_prompt = f"""Analyze the following query results and provide insights:

Query: {query}
Rows returned: {row_count}
Statistical Summary: {json.dumps(stats, indent=2)}

Provide insights in JSON format with:
- summary: Brief summary of key findings
- trends: List of trends observed (if any)
- anomalies: List of anomalies or outliers (if any)
- correlations: List of correlations between columns (if any)

Return only valid JSON."""

        try:
            response = self.llm.invoke(insights_prompt)
            if hasattr(response, 'content'):
                insights_text = response.content
            else:
                insights_text = str(response)
            
            # Try to parse JSON from response
            if "```json" in insights_text:
                insights_text = insights_text.split("```json")[1].split("```")[0].strip()
            elif "```" in insights_text:
                insights_text = insights_text.split("```")[1].split("```")[0].strip()
            
            insights = json.loads(insights_text)
            return insights
        except Exception as e:
            # Fallback to simple insights
            return {
                "summary": f"Query returned {row_count} rows with {len(stats)} numeric columns analyzed.",
                "trends": [],
                "anomalies": [],
                "correlations": []
            }
    
    def suggest_visualization(
        self,
        query: str,
        query_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Suggest appropriate visualization type using LLM and heuristics."""
        if not query_results.get("success"):
            return None
        
        data = query_results.get("data", [])
        columns = query_results.get("columns", [])
        
        if not data or not columns:
            return None
        
        # First try LLM-based suggestion
        try:
            viz_prompt = f"""Based on this query and data structure, suggest the best visualization:

Query: {query}
Columns: {', '.join(columns)}
Number of rows: {len(data)}
Sample data: {json.dumps(data[:3], default=str)}

Suggest the best chart type (line_chart, bar_chart, pie_chart, area_chart, scatter_chart, heatmap, table) and provide reasoning.
Return JSON with: {{"chart_type": "...", "reasoning": "..."}}"""

            response = self.llm.invoke(viz_prompt)
            if hasattr(response, 'content'):
                viz_text = response.content
            else:
                viz_text = str(response)
            
            # Parse JSON from response
            if "```json" in viz_text:
                viz_text = viz_text.split("```json")[1].split("```")[0].strip()
            elif "```" in viz_text:
                viz_text = viz_text.split("```")[1].split("```")[0].strip()
            
            llm_suggestion = json.loads(viz_text)
            
            # Add configuration suggestions
            config = {}
            if llm_suggestion.get("chart_type") == "line_chart":
                config = {"x_axis": columns[0] if columns else None, "y_axis": columns[1] if len(columns) > 1 else None}
            elif llm_suggestion.get("chart_type") == "bar_chart":
                config = {"x_axis": columns[0] if columns else None, "y_axis": columns[1] if len(columns) > 1 else None}
            elif llm_suggestion.get("chart_type") == "pie_chart":
                config = {"label": columns[0] if columns else None, "value": columns[1] if len(columns) > 1 else None}
            
            return {
                "chart_type": llm_suggestion.get("chart_type", "bar_chart"),
                "config": config,
                "reasoning": llm_suggestion.get("reasoning", "LLM suggested visualization")
            }
        except Exception:
            # Fallback to heuristics
            num_columns = len(columns)
            num_rows = len(data)
            
            time_columns = [col for col in columns if any(keyword in col.lower() for keyword in ["date", "time", "year", "month", "day"])]
            
            numeric_columns = []
            if data:
                first_row = data[0]
                for col in columns:
                    try:
                        float(first_row.get(col, 0))
                        numeric_columns.append(col)
                    except (ValueError, TypeError):
                        pass
            
            if time_columns and numeric_columns:
                return {"chart_type": "line_chart", "config": {"x_axis": time_columns[0], "y_axis": numeric_columns[0]}, "reasoning": "Time series data detected"}
            elif num_columns == 2 and numeric_columns:
                if num_rows <= 10:
                    return {"chart_type": "pie_chart", "config": {"label": columns[0], "value": columns[1]}, "reasoning": "Small dataset with 2 columns"}
                else:
                    return {"chart_type": "bar_chart", "config": {"x_axis": columns[0], "y_axis": columns[1]}, "reasoning": "Categorical data with values"}
            elif num_columns > 2 and numeric_columns:
                return {"chart_type": "bar_chart", "config": {"x_axis": columns[0], "y_axis": columns[1]}, "reasoning": "Multiple columns with numeric data"}
            elif num_rows <= 20:
                return {"chart_type": "table", "config": {}, "reasoning": "Small dataset suitable for table view"}
            else:
                return {"chart_type": "bar_chart", "config": {}, "reasoning": "Default visualization"}
    
    def process_message(
        self,
        user: User,
        message: str,
        conversation_id: Optional[int],
        datasource_id: Optional[int],
        db: Session,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a user message and generate response."""
        # Get or create conversation
        if conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id
            ).first()
            if not conversation:
                raise ValueError("Conversation not found or access denied")
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=user.id,
                title=message[:50] if len(message) > 50 else message
            )
            db.add(conversation)
            db.flush()
        
        # Get datasource if specified
        datasource = None
        if datasource_id:
            datasource = db.query(DataSource).filter(
                DataSource.id == datasource_id,
                DataSource.owner_id == user.id,
                DataSource.is_active == True
            ).first()
        
        # Get conversation context
        conversation_history = self.get_conversation_context(conversation.id, db)
        
        # Save user message
        user_message = ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content=message
        )
        db.add(user_message)
        db.flush()
        
        # Convert to SQL (if datasource is database type)
        sql_query = None
        query_result = None
        
        if datasource and datasource.type in [DataSourceType.POSTGRESQL, DataSourceType.MYSQL]:
            try:
                sql_query = self.convert_query_to_sql(
                    question=message,
                    datasource=datasource,
                    conversation_history=conversation_history,
                    db=db
                )
                
                # Execute query
                query_result = self.execute_query(sql_query, datasource, password)
                
                # Save to query history
                query_history = QueryHistory(
                    user_id=user.id,
                    query_text=message,
                    sql_query=sql_query,
                    datasource_id=datasource.id,
                    execution_time=query_result.get("execution_time"),
                    result_count=query_result.get("row_count"),
                    success="true" if query_result.get("success") else "false",
                    error_message=query_result.get("error")
                )
                db.add(query_history)
                
            except Exception as e:
                query_result = {
                    "success": False,
                    "error": str(e),
                    "data": [],
                    "columns": [],
                    "row_count": 0
                }
                sql_query = None
        
        # Calculate statistics and generate insights
        stats = None
        insights = None
        suggested_queries = None
        
        if query_result and query_result.get("success"):
            data = query_result.get("data", [])
            columns = query_result.get("columns", [])
            
            # Calculate statistics
            if data and columns:
                stats = self._calculate_statistics(data, columns)
                # Generate insights
                insights = self._generate_insights(message, query_result, stats)
                # Generate suggested queries
                suggested_queries = self._generate_suggested_queries(message, query_result, columns)
        
        # Generate response with enhanced interpretation
        if query_result:
            assistant_message_text = self.generate_response(message, query_result, stats)
        else:
            # Handle file-based datasources
            if datasource and datasource.type == DataSourceType.FILE:
                assistant_message_text = self._process_file_query(user, message, datasource, db)
            else:
                # For non-database queries or when no datasource, provide general response
                assistant_message_text = "I can help you query your data sources. Please specify a database datasource to execute SQL queries, or ask me about your data."
        
        # Suggest visualization with enhanced metadata
        visualization_suggestion = None
        if query_result and query_result.get("success"):
            visualization_suggestion = self.suggest_visualization(message, query_result)
        
        # Save assistant message with enhanced metadata
        assistant_message = ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_message_text,
            metadata={
                "sql_query": sql_query,
                "query_result": query_result,
                "visualization_suggestion": visualization_suggestion,
                "statistical_summary": stats,
                "insights": insights,
                "suggested_queries": suggested_queries
            } if sql_query or stats else None
        )
        db.add(assistant_message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(assistant_message)
        
        return {
            "message": assistant_message_text,
            "conversation_id": conversation.id,
            "sql_query": sql_query,
            "execution_result": query_result,
            "visualization_suggestion": visualization_suggestion,
            "statistical_summary": stats,
            "insights": insights,
            "suggested_queries": suggested_queries,
            "message_id": assistant_message.id
        }
    
    def _process_file_query(
        self,
        user: User,
        message: str,
        datasource: DataSource,
        db: Session
    ) -> str:
        """Process natural language queries for file-based datasources."""
        try:
            # Get data from file
            df = self.analytics_engine.get_data(datasource, limit=1000)
            
            if df.empty:
                return "The file datasource is empty or could not be loaded."
            
            # Use LLM to interpret the query and generate pandas operations
            file_query_prompt = f"""The user wants to query a CSV/Excel file with the following question:
"{message}"

Available columns: {', '.join(df.columns.tolist())}
Number of rows: {len(df)}

Based on the question, suggest what pandas operations would answer it. Provide a brief explanation of what the data shows.

Sample data:
{df.head(5).to_string()}

Provide a helpful response explaining what the user can do with this data."""

            response = self.llm.invoke(file_query_prompt)
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
        except Exception as e:
            return f"I encountered an error processing your file query: {str(e)}. Please try rephrasing your question."