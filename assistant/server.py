import asyncio
from fastapi import FastAPI
from functools import wraps
from assistant.data_model import Item
from assistant.chain import load_prompts, create_assistant


class Counter:
    """
    Source: https://stackoverflow.com/questions/68331493/count-number-of-requests-with-global-variable-using-fastapi
    If there is more than 1 worker that wouldn't work because they do not share the same memory. I think it is ok for now.
    Should be using a cache mechanism or a DB, As explained in
    https://stackoverflow.com/questions/65686318/sharing-python-objects-across-multiple-workers
    """
    def __init__(self):
        self.count = 0
        self.lock = asyncio.Lock()

    def __call__(self, func):
        @wraps(func)
        async def inner(*args, **kwargs):
            async with self.lock:
                self.count += 1
            return func(*args, **kwargs)
        return inner


api = FastAPI()
count_calls = Counter()
assistant = create_assistant()


@api.get("/")
@count_calls
def read_root():
    return {"message": "answer"}


@api.get('/api/prompts')
@count_calls
def prompts():
    return load_prompts()


@api.post("/api/get_answer")
@count_calls
def get_answer(question: Item):
    answer = assistant.invoke(question.text)
    return {"message": answer}


@api.get("/api/calls_count")
def get_api_calls_count():
    return {'calls_count': count_calls.count}
