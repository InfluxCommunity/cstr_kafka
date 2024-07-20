import faust

app = faust.App(
    'hello_world2',
    broker='kafka://localhost:9092',
    store='memory://',
    value_serializer='raw',
    web_port=6067
)

greetings_topic = app.topic('greetings')
extended_greetings_topic = app.topic('extended_greetings')

@app.agent(greetings_topic)
async def extend_greeting(greetings):
    async for greeting in greetings:
        new_greeting = f"{greeting} and welcome!"
        print(new_greeting)
        await extended_greetings_topic.send(value=new_greeting)

if __name__ == '__main__':
    app.main()