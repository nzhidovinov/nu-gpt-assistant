import re
import tiktoken
import requests
from dotenv import find_dotenv, load_dotenv

from langchain.docstore.document import Document
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores.faiss import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings


load_dotenv(find_dotenv())


def load_document_text(url: str) -> str:
    """
    Loads google document as plain text.

    Examples:
        document_url = 'https://docs.google.com/document/d/...'
        document = load_document_text(document_url)
    """
    # Extract the document ID from the URL
    match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', url)
    if match_ is None:
        raise ValueError('Invalid Google Docs URL')
    doc_id = match_.group(1)

    # Download the document as plain text
    response = requests.get(f'https://docs.google.com/document/d/{doc_id}/export?format=txt')
    response.raise_for_status()
    text = response.text

    return text


def count_tokens(string: str | Document, encoding_name: str='cl100k_base') -> int:
    """
    Counts tokens in string.

    Examples:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=lambda x: count_tokens(x)
        )
    """
    if isinstance(string, Document):
        string = string.page_content
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def clear_markdown(text: str, level: int = 3) -> str:
    """Clear markdown"""
    text = text.replace('\ufeff', '')
    text = text.replace('\r', '')
    text = re.sub(r'^([А-Я ]+) \n', r'# \1\n\1\n', text)
    text = re.sub(r'(\d\.| ) ([А-Я ]+) \n', r'## \2\n\2\n', text)
    text = re.sub(r' +', r' ', text)
    text = re.sub(r' ([А-Я ]+) \n', r'## \1\n\1\n', text)
    text = text.strip()
    return text


if __name__ == '__main__':
    # Load document
    url = 'https://docs.google.com/document/d/11MU3SnVbwL_rM-5fIC14Lc3XnbAV4rY1Zd_kpcMuH4Y'
    text = load_document_text(url)
    text = clear_markdown(text)

    # Split document
    headers_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[('#', 'H1'), ('##', 'H2')]
    )
    documents = headers_splitter.split_text(text)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=0,
        length_function=lambda x: count_tokens(x)
    )
    chunks = [
        Document(page_content=chunk, metadata=document.metadata)
        for document in documents
        for chunk in splitter.split_text(document.page_content)
    ]

    # Create DB
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(
        documents=chunks, embedding=embeddings
    )
    db.save_local('db')
