import asyncio
import sys
from typing import Optional
from Assistant.assistant import Assistant

async def process_question(assistant: Assistant, question: str) -> Optional[str]:
    """
    Process a question through the assistant.
    
    Args:
        assistant: Initialized Assistant instance
        question: Question to process
        
    Returns:
        str: Response from the assistant or None if there's an error
    """
    try:
        return await assistant.ask_question(question)
    except Exception as e:
        print(f"\nError al procesar la pregunta: {str(e)}", file=sys.stderr)
        return None

async def interactive_session(assistant: Assistant):
    """
    Run an interactive Q&A session with the assistant.
    
    Args:
        assistant: Initialized Assistant instance
    """
    print("\n¡Asistente inicializado! Escribe tus preguntas.")
    print("Comandos disponibles:")
    print("- 'salir': Terminar la sesión")
    print("- 'recargar': Recargar la base de datos")
    print("- 'ayuda': Mostrar esta ayuda")
    
    while True:
        try:
            # Solicitar pregunta
            question = input("\nTu pregunta: ").strip()
            
            # Procesar comandos especiales
            if question.lower() in ["salir", "exit", "quit"]:
                print("\n¡Hasta luego!")
                break
                
            elif question.lower() == "recargar":
                print("\nRecargando base de datos...")
                assistant.reload_database()
                print("Base de datos recargada exitosamente.")
                continue
                
            elif question.lower() == "ayuda":
                print("\nComandos disponibles:")
                print("- 'salir': Terminar la sesión")
                print("- 'recargar': Recargar la base de datos")
                print("- 'ayuda': Mostrar esta ayuda")
                continue
                
            elif not question:
                print("\nPor favor, escribe una pregunta.")
                continue
            
            # Procesar la pregunta
            print("\nProcesando pregunta...")
            response = await process_question(assistant, question)
            
            if response:
                print(f"\nRespuesta: {response}")
            
        except KeyboardInterrupt:
            print("\n\nSesión interrumpida por el usuario.")
            break
        except Exception as e:
            print(f"\nError inesperado: {str(e)}", file=sys.stderr)
            print("La sesión continuará con la siguiente pregunta.")

def main():
    """Main entry point of the application."""
    try:
        # Inicializar el asistente
        print("Inicializando asistente...")
        assistant = Assistant()
        
        # Ejecutar sesión interactiva
        asyncio.run(interactive_session(assistant))
        
    except KeyboardInterrupt:
        print("\n\nPrograma terminado por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError fatal: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()