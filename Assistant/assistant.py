from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import os
from dotenv import load_dotenv

from Retriever.retriever import DocumentRetriever, RetrieverConfig
from DB.DB import DBConfig, DocumentDatabase
from langchain_core.vectorstores import VectorStore

@dataclass
class AssistantConfig:
    """Configuration class for the Assistant."""
    google_api_key: str
    langchain_api_key: str
    db_config: DBConfig
    retriever_config: RetrieverConfig

class Assistant:
    """
    Unified interface for document processing and question answering.
    Integrates document database and retriever components.
    """

    @staticmethod
    def load_environment() -> AssistantConfig:
        """
        Load configuration from environment variables.
        
        Returns:
            AssistantConfig with loaded values
        
        Raises:
            ValueError: If required environment variables are missing
        """
        load_dotenv()  # Carga variables de .env si existe
        
        google_api_key = os.getenv("GOOGLE_API_KEY")
        langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
        
        if not google_api_key or not langchain_api_key:
            raise ValueError("Required API keys not found in environment variables")
            
        # Configuración para la base de datos
        '''
        db_config = DBConfig(
            source_data_folder=Path("./data"),
            path_db=Path("./vector_db"),
            chunk_size=1500,
            chunk_overlap=375,
            separators=["\n\n", "\n", ". ", "! ", "? ", ";", ":", "|"],
            model_name="all-MiniLM-L6-v2"
        )
        '''
        #Al inicicializar a None usamos la configuración por defecto de la clase DB
        db_config = None

        #Configuración del Retriever
        '''
        retriever_config = RetrieverConfig(
            api_key=google_api_key,
            model="gemini-pro",
            prompt_form="your-default-prompt-form"
        )
        '''
        
        # Configuración por defecto para el retriever
        retriever_config = RetrieverConfig(
            api_key=google_api_key
        )
        
        return AssistantConfig(
            google_api_key=google_api_key,
            langchain_api_key=langchain_api_key,
            db_config=db_config,
            retriever_config=retriever_config
        )

    def __init__(self, config: Optional[AssistantConfig] = None):
        """
        Initialize the Assistant.
        
        Args:
            config: Optional configuration. If None, loads from environment.
        """
        self.config = config or self.load_environment()
        self.db: Optional[DocumentDatabase] = None
        self.retriever: Optional[DocumentRetriever] = None
        self.vectorstore: Optional[VectorStore] = None
        
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize database and retriever components."""
        try:
            # Inicializar la base de datos
            self.db = DocumentDatabase(config=self.config.db_config)
            self.vectorstore = self.db.initialize_database()
            
            # Inicializar el retriever
            self.retriever = DocumentRetriever(
                vectorstore=self.vectorstore,
                config=self.config.retriever_config
            )
            self.retriever.initialize()
            
        except Exception as e:
            raise RuntimeError(f"Error initializing components: {str(e)}")

    async def ask_question(self, question: str) -> str:
        """
        Process a question through the RAG chain.
        
        Args:
            question: The question to process
            
        Returns:
            str: The answer to the question
            
        Raises:
            RuntimeError: If components are not properly initialized
        """
        if not self.retriever or not self.retriever.rag_chain:
            raise RuntimeError("Retriever not properly initialized")
            
        try:
            return await self.retriever.process_query(question)
        except Exception as e:
            raise RuntimeError(f"Error processing question: {str(e)}")

    def reload_database(self) -> None:
        """Reload the document database and reinitialize the retriever."""
        try:
            if self.db:
                self.vectorstore = self.db.initialize_database()
                
            if self.retriever:
                self.retriever = DocumentRetriever(
                    vectorstore=self.vectorstore,
                    config=self.config.retriever_config
                )
                self.retriever.initialize()
                
        except Exception as e:
            raise RuntimeError(f"Error reloading database: {str(e)}")