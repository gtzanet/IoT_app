from fastapi import FastAPI, BackgroundTasks
from time import sleep

app = FastAPI()

def write_message(message):
	sleep(10)
	f = open("hello.txt", "a")
	f.write(message)
	f.close()
	return

@app.get("/hello")
async def root(background_tasks: BackgroundTasks):
	background_tasks.add_task(write_message, "Hello world!")
	return {"message": "Hello world!"}
