from physiq_agent.agent import run_physiq
from memory.conversation_store import save_conversation, load_conversation

USER_ID = "local_user"
history = load_conversation(USER_ID)

print("PHYSIQ AI (type 'exit' to quit)")

while True:
    msg = input("\nYou: ")
    if msg.lower() == "exit":
        break

    reply = run_physiq(msg, history)
    history.append({"user": msg, "assistant": reply})

    save_conversation(USER_ID, msg, reply)

    print("\nPHYSIQ:\n", reply)
