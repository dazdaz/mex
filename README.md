gcloud auth application-default login

gcloud services enable aiplatform.googleapis.com

gcloud iam service-accounts create vertex-app-runner \
    --display-name="Service Account for Vertex AI App" \
    --project=daev-playground

gcloud projects add-iam-policy-binding daev-playground \
    --member="serviceAccount:vertex-app-runner@daev-playground.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

>>> remove this
gcloud projects add-iam-policy-binding your-gcp-project-id \
    --member="user:your-email@example.com" \
    --role="roles/aiplatform.user"
# daev@daev-playground.iam.gserviceaccount.com

# Client-based APIs, like Vertex AI, need a quota project to handle billing and resource usage
gcloud auth application-default set-quota-project daev-playground
gcloud config set billing/quota_project daev-playground

# If you have any issues with the above binding, then you can double check by listing all bindings and searching for aiplatform
gcloud projects get-iam-policy myproject --flatten="bindings[].members"

# Running the app
export GOOGLE_APPLICATION_CREDENTIALS=/Users/daev/.config/gcloud/application_default_credentials.json
uv run flask run --host=127.0.0.1 --port=5001

# Troubleshooting
FLASK_DEBUG=True uv run flask run --host=127.0.0.1 --port=5001

Open your browser and go to the URL provided:

URL: http://127.0.0.1:5001
