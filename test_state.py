from app.ingestion.state_manager import load_state, save_state

state = load_state()

state["current_source"] = 5

save_state(state)

print(load_state())