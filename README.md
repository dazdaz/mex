# 🚀 MEX - Model EXplorer

Summary: MEX (Model EXplorer) is a desktop interface for Google Cloud's Vertex AI, providing an easy-to-use application to interact with and compare various AI models.

# AI Model Interaction Application

This application provides a user interface for interacting with various **Google Cloud Vertex AI models**, including **Claude 3.7 Sonnet, Claude 4.1 Opus, Gemini 2.5 Pro, and Gemini 2.5 Flash**.

## Key Features

* **Multi-Model Support**: Easily switch between different AI models from Vertex AI.
* **Tabbed Interface**: Manage multiple queries simultaneously with a convenient tabbed layout.
* **Real-time Metrics**: View character and token counts for both your input prompts and the model's responses.
* **User-Friendly UI**:
    * **Split-Panel Layout**: Resize the input and response sections to suit your workflow.
    * **Customization**: Toggle between dark and light modes, and adjust the application's font size.
    * **Progress Indicators**: See the status of API calls with a progress bar and temporary status messages.
* **Data Handling**:
    * **API Integration**: Authenticates with Google Cloud using `google.auth` for secure API calls.
    * **Response Options**: View responses as parsed text or the raw JSON output.
    * **Export**: Save either the raw JSON or parsed text to a local file.
    * **Logging**: A local log file helps with debugging and troubleshooting.
* **Convenience & Shortcuts**:
    * **Query Synchronization**: An optional feature to apply the same prompt to all open tabs for easy model comparison.
    * **Clipboard Functions**: Quickly copy query text or model responses with dedicated buttons.
    * **Keyboard Shortcuts**: Use `Ctrl+Enter` to execute a query, `Ctrl+T` to open a new tab, and `Ctrl+W` to close the current tab.
* **Fictional Pricing**: Get an estimated cost for each query based on a predefined, fictional pricing structure.

<img width="3024" height="1728" alt="image" src="https://github.com/user-attachments/assets/5ca4983c-82f5-4c7a-a83f-dda44e9ebff9" />

***

## ⚠️ Disclaimer

This application is **not an official Google product**. It is a personal project for demonstration purposes only.
The fictional pricing shown within the app is for illustrative purposes and does not reflect actual costs.
Use at your own risk.

***

## 🛠️ Setup and Installation

### 1. Google Cloud Configuration

Before running the application, you need to configure your Google Cloud project and authenticate the `gcloud` CLI.

1.  **Authenticate your user account.** This command will open a web browser to grant permissions.

    ```bash
    gcloud auth application-default login
    ```

2.  **Set your Google Cloud Project ID.** You can either set this as an environment variable or set it as the default for your `gcloud` configuration. Replace `YOUR_PROJECT_ID` with your actual project ID.

    ```bash
    export PROJECT_ID="YOUR_PROJECT_ID"
    # Or, set it for your gcloud CLI
    gcloud config set project YOUR_PROJECT_ID
    ```

3.  **Enable the required Google Cloud APIs.**

    ```bash
    gcloud services enable aiplatform.googleapis.com
    gcloud services enable iamcredentials.googleapis.com
    ```

4.  **Grant necessary IAM permissions.** The user account needs the `Vertex AI User` role to access the models. Replace `YOUR_ACCOUNT` with your authenticated user account (e.g., `user@example.com`).

    ```bash
    gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
        --member="user:YOUR_ACCOUNT" \
        --role="roles/aiplatform.user"
    ```

5.  **Enable models in the Vertex AI Model Garden.** Navigate to the **Model Garden** in your Vertex AI console and enable the specific models you wish to use (e.g., Claude).

***

## ⚙️ Helper Scripts

This repository includes two helper scripts to assist with Vertex AI management.

-   `query_vertex_predictive.sh`: A shell script to query the public Vertex AI endpoints using BASH.
-   `show_vertex_endpoints.sh`: A script to display the private endpoints where models have been deployed in your project.
