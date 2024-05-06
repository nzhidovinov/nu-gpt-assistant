from fastapi import FastAPI
from assistant.data_model import Item
from assistant.chain import load_prompts, create_assistant


api = FastAPI()
assistant = create_assistant()


@api.get("/")
def read_root():
    return {"message": "answer"}


@api.get('/api/prompts')
def prompts():
    return load_prompts()


@api.post("/api/get_answer")
def get_answer(question: Item):
    answer = assistant.invoke(question.text)
    return {"message": answer}
