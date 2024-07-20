import faust

app = faust.App(
    'hello_world',
    broker='kafka://localhost:9092',
    store='memory://',
    value_serializer='raw',
)

greetings_topic = app.topic('greetings')

@app.agent(greetings_topic)
async def greet(greetings):
    async for greeting in greetings:
        print(greeting)

@app.task
async def send_greeting():
    await greetings_topic.send(value='Hello, world!')

if __name__ == '__main__':
    app.main()

# // One script calls a function 