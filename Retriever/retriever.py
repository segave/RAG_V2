from dataclasses import dataclass
from typing import Any, Optional
from abc import ABC, abstractmethod

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.vectorstores import VectorStore
from langchain_core.prompts import BasePromptTemplate

from Retriever import constants as c
from Retriever.helpers import format_docs

@dataclass
class RetrieverConfig:
    """Configuration class for Retriever parameters."""
    api_key: str
    model: str = c.model
    prompt_form: str = c.promptForm

class LLMFactory(ABC):
    """Abstract factory for creating LLM instances."""
    
    @abstractmethod
    def create_llm(self, model: str, api_key: str) -> BaseChatModel:
        """Create and return an LLM instance."""
        pass

class GoogleLLMFactory(LLMFactory):
    """Factory for creating Google's Generative AI instances."""
    
    def create_llm(self, model: str, api_key: str) -> BaseChatModel:
        return ChatGoogleGenerativeAI(model=model, google_api_key=api_key)

class DocumentRetriever:
    """Manages document retrieval and RAG chain configuration."""

    def __init__(
        self,
        vectorstore: VectorStore,
        config: RetrieverConfig,
        llm_factory: Optional[LLMFactory] = None
    ):
        """
        Initialize the DocumentRetriever.

        Args:
            vectorstore: Vector store containing document embeddings
            config: Configuration parameters
            llm_factory: Factory for creating LLM instances
        """
        self.vectorstore = vectorstore
        self.config = config
        self.llm_factory = llm_factory or GoogleLLMFactory()
        
        self.llm: Optional[BaseChatModel] = None
        self.retriever: Any = None  # Type depends on vectorstore implementation
        self.prompt: Optional[BasePromptTemplate] = None
        self.rag_chain: Optional[Any] = None
        
    def configure_llm(self) -> None:
        """Configure the Language Model."""
        try:
            self.llm = self.llm_factory.create_llm(
                model=self.config.model,
                api_key=self.config.api_key
            )
        except Exception as e:
            raise RuntimeError(f"Error configuring LLM: {str(e)}")

    def configure_retriever(self) -> None:
        """Configure the document retriever."""
        try:
            self.retriever = self.vectorstore.as_retriever()
        except Exception as e:
            raise RuntimeError(f"Error configuring retriever: {str(e)}")

    def load_prompt(self) -> None:
        """Load the prompt template from hub."""
        try:
            self.prompt = hub.pull(self.config.prompt_form)
        except Exception as e:
            raise RuntimeError(f"Error loading prompt: {str(e)}")

    def build_chain(self) -> None:
        """Build the RAG processing chain."""
        if not all([self.llm, self.retriever, self.prompt]):
            raise ValueError("LLM, retriever, and prompt must be configured before building chain")
        
        try:
            self.rag_chain = (
                {
                    "context": self.retriever | format_docs,
                    "question": RunnablePassthrough()
                }
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
        except Exception as e:
            raise RuntimeError(f"Error building chain: {str(e)}")

    def initialize(self) -> None:
        """Initialize all components of the retriever."""
        self.configure_llm()
        self.configure_retriever()
        self.load_prompt()
        self.build_chain()

    async def process_query(self, query: str) -> str:
        """
        Process a query through the RAG chain.

        Args:
            query: The question or query to process

        Returns:
            The processed response as a string
        """
        if not self.rag_chain:
            raise RuntimeError("Retriever not initialized. Call initialize() first")
        
        try:
            return await self.rag_chain.ainvoke(query)
        except Exception as e:
            raise RuntimeError(f"Error processing query: {str(e)}")