import faust

app = faust.App(
    'logic_pid_controller',
    broker='kafka://localhost:9092',
    store='memory://',
    value_serializer='json',  # Use JSON serializer for structured data
    web_port=6067
)

cstr_topic = app.topic('cstr')
pid_control_topic = app.topic('pid_control')

# Initialize process variables
T0 = 10
T_previous = T0
setpoint = 1
process_count = 0
max_iterations = 10

def compute_u(ca, t_current, t_previous, setpoint):
    """Compute the u value based on Ca and dT."""
    dT = abs(t_current - t_previous) if t_previous is not None else 0
    u = ca + dT / setpoint  # Simple mathematical transformation using dT and setpoint
    return u, dT

@app.agent(cstr_topic)
async def process_cstr_events(events):
    global T_previous, setpoint, process_count
    async for event in events:
        if process_count >= max_iterations:
            await app.stop()
            break
        ca = event.get('Ca')
        t_current = event.get('T')
        if ca is not None and t_current is not None:
            u, dT = compute_u(ca, t_current, T_previous, setpoint)
            control_message = {
                'Ca': ca,
                'T': t_current,
                'u': u,
                'dT': dT,
                'setpoint': setpoint
            }
            print(f"Received Ca: {ca}, T: {t_current}, Computed dT: {dT}, Computed u: {u}, Setpoint: {setpoint}")
            await pid_control_topic.send(value=control_message)
            T_previous = t_current  # Update the previous temperature value

            # Update the iteration count and setpoint
            process_count += 1
            if process_count % 3 == 0:
                setpoint += 2

if __name__ == '__main__':
    app.main()
