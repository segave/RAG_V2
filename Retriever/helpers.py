#Functions that are going to help
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)