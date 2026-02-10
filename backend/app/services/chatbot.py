from typing import Dict, Any, Optional, List
from datetime import datetime
import time
import json
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.schema import BaseMessage, HumanMessage, AIMessage

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
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute SQL query via analytics engine."""
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
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "columns": [],
                "row_count": 0,
                "execution_time": 0
            }
    
    def generate_response(
        self,
        query: str,
        query_results: Dict[str, Any]
    ) -> str:
        """Generate natural language response from query results."""
        if not query_results.get("success"):
            error_msg = query_results.get("error", "Unknown error")
            return f"I encountered an error while executing your query: {error_msg}. Please try rephrasing your question or check if the datasource is properly configured."
        
        # Format results for prompt
        data = query_results.get("data", [])
        row_count = query_results.get("row_count", 0)
        
        if row_count == 0:
            return "The query executed successfully but returned no results. You might want to adjust your filters or check if the data exists."
        
        # Limit data shown in prompt (first 10 rows)
        preview_data = json.dumps(data[:10], indent=2, default=str)
        
        results_text = f"Found {row_count} rows.\n\nFirst few rows:\n{preview_data}"
        if row_count > 10:
            results_text += f"\n... and {row_count - 10} more rows"
        
        # Create chain and generate response
        chain = LLMChain(llm=self.llm, prompt=self._response_prompt_template)
        
        response = chain.run(
            query=query,
            query_results=results_text
        )
        
        return response.strip()
    
    def suggest_visualization(
        self,
        query: str,
        query_results: Dict[str, Any]
    ) -> Optional[str]:
        """Suggest appropriate visualization type based on query and results."""
        if not query_results.get("success"):
            return None
        
        data = query_results.get("data", [])
        columns = query_results.get("columns", [])
        
        if not data or not columns:
            return None
        
        # Simple heuristics for visualization suggestions
        num_columns = len(columns)
        num_rows = len(data)
        
        # Check for time-based columns
        time_columns = [col for col in columns if any(keyword in col.lower() for keyword in ["date", "time", "year", "month", "day"])]
        
        # Check for numeric columns
        numeric_columns = []
        if data:
            first_row = data[0]
            for col in columns:
                try:
                    float(first_row.get(col, 0))
                    numeric_columns.append(col)
                except (ValueError, TypeError):
                    pass
        
        # Suggest based on patterns
        if time_columns and numeric_columns:
            return "line_chart"  # Time series
        elif num_columns == 2 and numeric_columns:
            if num_rows <= 10:
                return "pie_chart"
            else:
                return "bar_chart"
        elif num_columns > 2 and numeric_columns:
            return "bar_chart"
        elif num_rows <= 20:
            return "table"
        else:
            return "bar_chart"  # Default
    
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
        
        # Generate response
        if query_result:
            assistant_message_text = self.generate_response(message, query_result)
        else:
            # For non-database queries or when no datasource, provide general response
            assistant_message_text = "I can help you query your data sources. Please specify a database datasource to execute SQL queries, or ask me about your data."
        
        # Suggest visualization
        visualization_suggestion = None
        if query_result and query_result.get("success"):
            visualization_suggestion = self.suggest_visualization(message, query_result)
        
        # Save assistant message
        assistant_message = ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_message_text,
            metadata={
                "sql_query": sql_query,
                "query_result": query_result,
                "visualization_suggestion": visualization_suggestion
            } if sql_query else None
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
            "message_id": assistant_message.id
        }
