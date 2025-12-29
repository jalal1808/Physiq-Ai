from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from agents.physiq_agent.agent import run_physiq
from agents.memory.conversation_store import load_conversation, save_conversation

class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        message = request.data.get("message")

        # Load conversation history
        history = load_conversation(user.id)

        # Run the agent
        reply = run_physiq(message, history)

        # Save conversation
        save_conversation(user.id, message, reply)

        return Response({
            "reply": reply,
            "history": history + [{"user": message, "assistant": reply}]
        })
