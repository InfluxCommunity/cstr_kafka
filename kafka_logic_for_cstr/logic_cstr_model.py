import faust

app = faust.App(
    'logic_cstr_model',
    broker='kafka://localhost:9092',
    store='memory://',
    value_serializer='json',
    web_port=6066
)

cstr_topic = app.topic('cstr')
pid_control_topic = app.topic('pid_control')


process_count = 0
max_iterations = 10

def compute_new_values(ca, t, u):
    """Compute the new Ca and T values based on the u value."""
    new_ca = ca + u 
    new_t = t + u
    return new_ca, new_t

@app.agent(cstr_topic)
async def cstr(cstr):
    global process_count
    async for ca_t_values in cstr:
        ca = ca_t_values.get('Ca')
        t = ca_t_values.get('T')
        print(f"Received Ca: {ca}, T: {t}")

@app.agent(pid_control_topic)
async def consume_u(events):
    global process_count
    async for event in events:
        if process_count >= max_iterations:
            await app.stop()
            break
        u = event.get('u')
        ca = event.get('Ca')
        t = event.get('T')
        if u is not None and ca is not None and t is not None:
            new_ca, new_t = compute_new_values(ca, t, u)
            new_values = {
                'Ca': new_ca,
                'T': new_t,
            }
            print(f"Received u: {u}, Computed new Ca: {new_ca}, new T: {new_t}")
            await cstr_topic.send(value=new_values)
            process_count += 1

@app.task
async def send_ca_t_values():
    ca, t = 1, 2 # Initial Ca and T values
    message = {
        'Ca': ca,
        'T': t,
    }
    await cstr_topic.send(value=message)

@app.command()
async def send_cstr_value(self, ca: float, t: float):
    message = {'Ca': ca, 'T': t}
    await cstr_topic.send(value=message)
    print(f"Sent Ca: {ca}, T: {t}")

if __name__ == '__main__':
    app.main()
