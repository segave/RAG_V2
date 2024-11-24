# Document Processing and Vector Database Assistant

Una aplicación de Python que combina procesamiento de documentos PDF con un asistente interactivo basado en RAG (Retrieval-Augmented Generation). La aplicación permite cargar documentos, procesarlos en una base de datos vectorial y realizar consultas inteligentes mediante un modelo de lenguaje.

## Características

### Procesamiento de Documentos
- Carga y procesamiento de documentos PDF
- Base de datos vectorial utilizando embeddings de HuggingFace
- Chunking inteligente de documentos

### Sistema de Recuperación (RAG)
- Integración con Google Generative AI
- Recuperación de documentos relevantes basada en similitud
- Procesamiento asíncrono de consultas
- Patrón Factory para la creación de LLMs
- Prompts personalizables via LangChain Hub

### Interfaz de Usuario
- Asistente interactivo por línea de comandos
- Recarga dinámica de la base de datos
- Sistema de manejo de errores robusto

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/yourusername/doc-processor.git
cd doc-processor
```

2. Instala las dependencias:
```bash
pip install langchain langchain_community langchain_huggingface chromadb google-generativeai
```

3. Configura las variables de entorno:
```bash
export GOOGLE_API_KEY="tu-api-key"
```

## Arquitectura

### Componentes Principales

#### DocumentDatabase
Maneja el procesamiento de documentos y la base de datos vectorial:
- Carga de documentos PDF
- Limpieza y procesamiento de texto
- Creación y gestión de la base de datos vectorial

#### DocumentRetriever
Gestiona la recuperación de documentos y la generación de respuestas:
```python
class DocumentRetriever:
    def __init__(self, vectorstore, config, llm_factory=None):
        """
        Args:
            vectorstore: Base de datos vectorial
            config: Configuración del retriever
            llm_factory: Factory para crear instancias de LLM
        """
```

Características principales:
- Patrón Factory para la creación flexible de LLMs
- Configuración mediante `RetrieverConfig`
- Cadena RAG completa para procesamiento de consultas
- Manejo asíncrono de consultas

#### Assistant
Coordina la interacción entre componentes:
- Integración de DocumentDatabase y DocumentRetriever
- Procesamiento de consultas del usuario
- Gestión de estados y errores

## Configuración

### RetrieverConfig
```python
@dataclass
class RetrieverConfig:
    api_key: str
    model: str = "gemini-pro"  # Modelo por defecto
    prompt_form: str = "rlm/rag-prompt"  # Prompt de LangChain Hub
```

### Uso del Retriever
```python
# Inicialización
config = RetrieverConfig(api_key="tu-api-key")
retriever = DocumentRetriever(vectorstore, config)
retriever.initialize()

# Procesamiento de consultas
response = await retriever.process_query("¿Cuál es el contenido principal?")
```

## Uso del Sistema

### Ejecutar el Asistente
```bash
python main.py
```

### Comandos Disponibles
- `salir` (o `exit`, `quit`): Terminar la sesión
- `recargar`: Recargar la base de datos
- `ayuda`: Mostrar la lista de comandos disponibles

## Manejo de Errores

El sistema incluye manejo robusto de errores en múltiples niveles:
- Inicialización de componentes
- Procesamiento de consultas
- Gestión de API externa
- Recuperación de la base de datos
- Interrupciones de usuario

## Contribuir

1. Fork el repositorio
2. Crea tu rama de características (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

## Notas de Desarrollo

- El sistema utiliza patrones de diseño Factory para facilitar la extensión a otros proveedores de LLM
- La arquitectura es modular y permite fácil integración de nuevos componentes
- El procesamiento asíncrono mejora la eficiencia en consultas largas

## Troubleshooting

### Problemas Comunes
1. Error de API Key
   - Verificar la configuración de variables de entorno
   - Comprobar permisos de la API key

2. Errores de Memoria
   - Ajustar el tamaño de chunk en DBConfig
   - Reducir el número de documentos procesados simultáneamente

3. Problemas de Recuperación
   - Verificar la calidad de los documentos fuente
   - Ajustar los parámetros del retriever

