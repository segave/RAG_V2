from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import logging
import DB.constants as c
from DB.helpers import clean_text, dynamic_chunk_size

@dataclass
class DBConfig:
    """Configuration class for database parameters"""
    source_data_folder: Path
    path_db: Path
    chunk_size: int
    chunk_overlap: int
    separators: List[str]
    model_name: str

class DocumentDatabase:
    """Manages document loading, processing and vector storage operations."""

    def __init__(self, config: Optional[DBConfig] = None):
        """Initialize database with configuration parameters."""
        if config is None:
            config = DBConfig(
                source_data_folder=Path(c.source_data_folder),
                path_db=Path(c.path_db),
                chunk_size=c.chunk_size,
                chunk_overlap=c.chunk_overlap,
                separators=c.separators,
                model_name=c.model_name
            )
        
        self.config = config
        self.documents: List[Document] = []
        self.splits: List[Document] = []
        self.vectorstore: Optional[Chroma] = None
        self.logger = logging.getLogger(__name__)

    def load_documents(self) -> None:
        """Load PDF documents from the configured directory."""
        if not self.config.source_data_folder.is_dir():
            raise FileNotFoundError(
                f"La ruta '{self.config.source_data_folder}' no existe o no es un directorio válido."
            )
        
        loader = PyPDFDirectoryLoader(str(self.config.source_data_folder))
        self.documents = loader.load()
        self.logger.info(f"Documentos cargados: {len(self.documents)}")

    def process_documents(self) -> None:
        """Clean and split documents into chunks."""
        if not self.documents:
            self.logger.warning("No hay documentos cargados para procesar.")
            return

        # Limpiar documentos
        cleaned_documents = [
            Document(
                page_content=clean_text(doc.page_content),
                metadata=doc.metadata
            ) for doc in self.documents
        ]

        # Configurar splitter
        text_splitter = RecursiveCharacterTextSplitter(
            separators=self.config.separators,
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap
        )

        # Procesar documentos
        self.splits = []
        for doc in cleaned_documents:
            chunk_size = dynamic_chunk_size(doc.page_content)
            text_splitter.chunk_size = chunk_size
            doc_splits = text_splitter.split_documents([doc])
            self.splits.extend(doc_splits)

        self.logger.info(f"Chunks generados: {len(self.splits)}")

    def create_vector_store(self) -> Chroma:
        """Create and populate vector store with processed documents."""
        embeddings_model = HuggingFaceEmbeddings(
            model_name=self.config.model_name
        )
        
        self.vectorstore = Chroma.from_documents(
            documents=self.splits,
            embedding=embeddings_model,
            persist_directory=str(self.config.path_db)
        )

        return self.vectorstore

    def initialize_database(self) -> Chroma:
        """Complete database initialization process."""
        self.load_documents()
        self.process_documents()
        return self.create_vector_store()