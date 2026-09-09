from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    Response,
    stream_with_context
)

from app.llm.rag_pipeline import RAGPipeline
from app.voice.voice_routes import voice_api

api = Blueprint("api", __name__)

# Initialize RAG Pipeline
rag = RAGPipeline()
api.register_blueprint(voice_api)


# -----------------------------
# Home Page
# -----------------------------
@api.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# Health Check
# -----------------------------
@api.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


# -----------------------------
# Chat API
# -----------------------------
@api.route("/chat", methods=["GET", "POST"])
def chat():

    if request.method == "GET":
        return jsonify({
            "message": "Use POST request with JSON body.",
            "example": {
                "message": "What is PM-KISAN?"
            }
        })

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No JSON data received."
            }), 400

        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({
                "error": "Message is required."
            }), 400

        result = rag.ask(user_message)

        return jsonify({
            "message": user_message,
            "answer": result["answer"],
            "confidence": result["confidence"],
            "confidence_level": result["confidence_level"],
            "sources": result["sources"]
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# -----------------------------
# Streaming Chat API
# -----------------------------
@api.route("/chat-stream", methods=["POST"])
def chat_stream():

    try:

        data = request.get_json()

        if not data:
            return Response(
                "No JSON data received.",
                status=400,
                mimetype="text/plain"
            )

        user_message = data.get("message", "").strip()

        if not user_message:
            return Response(
                "Message is required.",
                status=400,
                mimetype="text/plain"
            )

        def generate():

            # Temporary version
            # This still waits for rag.ask() to finish.
            for chunk in rag.stream_answer(user_message):
              yield chunk

        return Response(
            stream_with_context(generate()),
            mimetype="text/plain"
        )

    except Exception as e:
        return Response(
            str(e),
            status=500,
            mimetype="text/plain"
        )