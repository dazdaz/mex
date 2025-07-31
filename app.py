import os
import logging
import time
from flask import Flask, render_template, request, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel
from google.api_core.exceptions import PermissionDenied, GoogleAPIError, InvalidArgument, NotFound, ResourceExhausted
from google.auth import default

# --- CONFIGURATION ---
PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION", "us-central1")  # Default to us-central1 if not set
MAX_PROMPT_LENGTH = 1000  # Maximum prompt length for input validation

# Ensure required environment variables are set
if not PROJECT_ID:
    logging.error("PROJECT_ID environment variable is required.")
    exit(1)

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# --- FLASK APP INITIALIZATION ---
app = Flask(__name__)

# --- AUTHENTICATION CHECK ---
try:
    credentials, project = default()
    logging.info(f"✅ Authenticated with credentials for project: {project}")
except Exception as e:
    logging.error(f"❌ Authentication failed: {e}")
    exit(1)

# --- VERTEX AI INITIALIZATION ---
try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    logging.info(f"✅ Vertex AI initialized for project '{PROJECT_ID}' in '{LOCATION}'")
except Exception as e:
    logging.error(f"❌ Error initializing Vertex AI: {e}")
    logging.error("Please ensure your Project ID and Location are correct and you've authenticated via 'gcloud auth application-default login'.")
    exit(1)

# --- DYNAMIC MODEL LIST ---
def get_available_models():
    """Return list of available models on Vertex AI as of July 2025."""
    try:
        # Models available on Vertex AI (Gemini 2.5 and Anthropic Claude)
        return [
            # Google Gemini 2.5 Family (Generally Available)
            "publishers/google/models/gemini-2.5-pro",          # Most advanced reasoning model
            "publishers/google/models/gemini-2.5-flash",        # Workhorse model for low latency
            "publishers/google/models/gemini-2.5-flash-lite",   # Cost-efficient, high-throughput model

            # Anthropic Claude Family (assumed available on Vertex AI)
            "publishers/anthropic/models/claude-opus-4@20250522",     # Claude 4 Opus model
            "publishers/anthropic/models/claude-sonnet-4@20250522",   # Claude 4 Sonnet model
            "publishers/anthropic/models/claude-3-7-sonnet@20250219", # Claude 3.7 Sonnet model
            "publishers/anthropic/models/claude-3-5-sonnet-v2@20241022", # Claude 3.5 Sonnet v2 model
            "publishers/anthropic/models/claude-3-5-sonnet@20240620", # Balanced Claude 3.5 model
            "publishers/anthropic/models/claude-3-opus@20240229",     # Most powerful Claude 3 model
            "publishers/anthropic/models/claude-3-sonnet@20240229",   # Balanced Claude 3 model
            "publishers/anthropic/models/claude-3-haiku@20240307",    # Fastest Claude 3 model
            "publishers/anthropic/models/claude-3-5-haiku@20241022",  # Latest Haiku 3.5 model
        ]
    except Exception as e:
        logging.error(f"❌ Failed to fetch available models: {e}")
        return []

# --- WEB ROUTES ---
@app.route("/")
def index():
    """Renders the main web page with available models."""
    models = get_available_models()
    if not models:
        logging.warning("No models available, rendering empty model list.")
    return render_template("index.html", models=models)

@app.route("/generate", methods=["POST"])
def generate():
    """Handles the API call to Vertex AI."""
    try:
        data = request.get_json()
        model_name = data.get("model")
        prompt = data.get("prompt")

        # Input validation
        if not model_name or not prompt:
            logging.warning("Model and prompt are required.")
            return jsonify({"error": "Model and prompt are required."}), 400

        if len(prompt) > MAX_PROMPT_LENGTH:
            logging.warning(f"Prompt too long: {len(prompt)} characters")
            return jsonify({"error": f"Prompt exceeds maximum length of {MAX_PROMPT_LENGTH} characters."}), 400

        # Verify model is in available list
        if model_name not in get_available_models():
            logging.warning(f"Invalid model name: {model_name}")
            return jsonify({"error": f"Model {model_name} is not available."}), 400

        logging.info(f"Generating content with model: {model_name}")

        # Retry mechanism for ResourceExhausted
        max_retries = 3
        for retry in range(max_retries):
            try:
                model = GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return jsonify({"response": response.text})
            except ResourceExhausted as e:
                logging.warning(f"⚠️ Resource exhausted for model {model_name}, retry {retry+1}/{max_retries}. Error: {e}")
                if retry == max_retries - 1:
                    logging.error(f"❌ Max retries reached for model {model_name}. Error: {e}")
                    return jsonify({"error": f"Resource exhausted for {model_name} after multiple retries: {str(e)}. Please try again later."}), 429
                time.sleep(2 ** retry)  # Exponential backoff

    except PermissionDenied as e:
        logging.error(f"❌ Permission error: {e}")
        return jsonify({"error": f"Permission denied to access model {model_name}: {str(e)}. Please check your IAM roles."}), 403
    except InvalidArgument as e:
        logging.error(f"❌ Invalid argument error: {e}")
        return jsonify({"error": f"Invalid argument for model {model_name}: {str(e)}. Please check your request."}), 400
    except NotFound as e:
        logging.error(f"❌ Not found error: {e}")
        return jsonify({"error": f"Model {model_name} not found: {str(e)}. Please check the model name."}), 404
    except GoogleAPIError as e:
        logging.error(f"❌ Google API error: {e}")
        return jsonify({"error": f"A Google API error occurred for model {model_name}: {str(e)}"}), 500
    except Exception as e:
        logging.exception(f"❌ An unexpected error occurred: {e}")
        return jsonify({"error": f"An internal error occurred for model {model_name}: {str(e)}"}), 500

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
