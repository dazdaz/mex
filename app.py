import os
import logging
import time
from flask import Flask, render_template, request, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel
from google.api_core.exceptions import PermissionDenied, GoogleAPIError, InvalidArgument, NotFound, ResourceExhausted

# --- CONFIGURATION ---
# IMPORTANT: Replace these with your actual Project ID and Location.
PROJECT_ID = os.environ.get("PROJECT_ID", "daev-playground")  # Use environment variable or default
LOCATION = os.environ.get("LOCATION", "us-central1")        # Use environment variable or default

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

# --- VERTEX AI INITIALIZATION ---
try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    logging.info(f"✅ Vertex AI initialized for project '{PROJECT_ID}' in '{LOCATION}'")
except Exception as e:
    logging.error(f"❌ Error initializing Vertex AI: {e}")
    logging.error("Please ensure your Project ID and Location are correct and you've authenticated via 'gcloud auth application-default login'.")


# --- WEB ROUTES ---
@app.route("/")
def index():
    """Renders the main web page."""
    # --- UPDATED & VERIFIED MODEL LIST (As of July 2025) ---
    models = [
        # --- Google Gemini Family ---
        "gemini-1.5-pro-001",      # Most capable 1.5 model
        "gemini-1.5-flash-001",    # Fastest 1.5 model for speed-sensitive tasks
        "gemini-1.0-pro-002",      # Stable 1.0 Pro model

        # --- Anthropic Claude 4 Family ---
        "claude-opus-4@20250514", # Most powerful Claude 4 model
        "claude-sonnet-4@20250514", # Balanced Claude 4 model

        # --- Anthropic Claude 3.x Family ---
        "claude-3-7-sonnet@20250219", # Latest Sonnet 3.7 model
        "claude-3-5-sonnet@20240620", # State-of-the-art balance of intelligence and speed
        "claude-3-opus@20240229",     # Most powerful Claude 3 model for complex tasks
        "claude-3-sonnet@20240229",   # Balanced Claude 3 model
        "claude-3-haiku@20240307",    # Fastest Claude 3 model
        "claude-3-5-haiku@20241022",  # Latest Haiku 3.5 model

    ]
    return render_template("index.html", models=models)


@app.route("/generate", methods=["POST"])
def generate():
    """Handles the API call to Vertex AI."""
    try:
        data = request.get_json()
        model_name = data.get("model")
        prompt = data.get("prompt")

        if not model_name or not prompt:
            logging.warning("Model and prompt are required.")
            return jsonify({"error": "Model and prompt are required."}), 400

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
                if retry == max_retries -1:
                    logging.error(f"❌ Max retries reached for model {model_name}. Error: {e}")
                    return jsonify({"error": f"Resource exhausted for {model_name} after multiple retries: {str(e)}. Please try again later."}), 429
                time.sleep(2 ** retry) # Exponential backoff


    except PermissionDenied as e:
        logging.error(f"❌ Permission error: {e}")
        return jsonify({"error": f"Permission denied to access model {model_name}: {str(e)}. Please check your IAM roles. Make sure that the service account or user account that you are using has the 'roles/aiplatform.user' or 'roles/aiplatform.admin' role."}), 403
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
    app.run(debug=True, port=5001)
