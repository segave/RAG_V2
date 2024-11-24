#Functions that are going to help calculate prime numbers
import re

def clean_text(text):
    # Eliminar saltos de línea innecesarios
    text = re.sub(r'\n+', '\n', text)
    # Eliminar espacios extras
    text = re.sub(r'\s+', ' ', text)
    return text

def dynamic_chunk_size(document):
    length = len(document)
    if length < 1000:
        return 512
    elif length < 5000:
        return 1024
    else:
        return 2048
