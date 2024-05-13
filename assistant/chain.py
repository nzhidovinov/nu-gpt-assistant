from pathlib import Path
from itertools import batched
from operator import itemgetter
from dotenv import find_dotenv, load_dotenv

from langchain.docstore.document import Document
from langchain.vectorstores.faiss import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import MessagesPlaceholder
from langchain.prompts import SystemMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import SystemMessage, HumanMessage, AIMessage


load_dotenv(find_dotenv())


def load_db(db_path: Path):
    return FAISS.load_local(
        str(db_path),
        embeddings=OpenAIEmbeddings(),
        allow_dangerous_deserialization=True
    )


def format_docs(docs: list[Document]) -> str:
    return '\n'.join(
        f'\nОтрывок документа №{i+1}:\n {doc.page_content}'
        for i, doc in enumerate(docs)
    )


def load_prompts():
    prompts = {}
    prompts_dir = Path('assistant/prompts')
    for prompt in prompts_dir.glob('*'):
        with prompt.open() as f:
            prompts[prompt.name] = f.read()
    return prompts


def prepare_chat_history(chat_history: list[str]):
    chain_chat_history = []
    for question, answer in batched(chat_history, 2):
        chain_chat_history.extend(
            [HumanMessage(content=question), AIMessage(content=answer)]
        )
    return chain_chat_history


def create_assistant(db_path: Path = Path('db')):
    # Load db
    db = load_db(db_path)
    retriever = db.as_retriever(
        search_type='similarity_score_threshold',
        search_kwargs=dict(score_threshold=0.25, k=5)
    )

    # Load prompts
    prompts = load_prompts()
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(prompts['system']),
        MessagesPlaceholder(variable_name="chat_history"),
        ChatPromptTemplate.from_template(prompts['instruction'])
    ])

    # Create model
    model = ChatOpenAI(
        model="gpt-3.5-turbo-1106",
        temperature=0
    )
    chain = (
        RunnablePassthrough().assign(
            context=itemgetter('question') | retriever | format_docs
        )
        | prompt
        | model
        | StrOutputParser()
    )

    return chain
