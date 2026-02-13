
# 💖 Valentine's Day Chatbot

A personalized RAG (Retrieval Augmented Generation) chatbot built with Love, Streamlit, and LangChain.

## 🛠️ Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure API Keys**:
    - Open the `.env` file.
    - Add your **Google Gemini API Key** (`GOOGLE_API_KEY`) OR **Groq API Key** (`GROQ_API_KEY`).
    - Add your **HuggingFace Token** (`HUGGINGFACEHUB_API_TOKEN`) for embeddings.

3.  **Prepare Data (Ingestion)**:
    - This step reads your WhatsApp chat, splits it into chunks, and saves it to a local vector database (`chroma_db`).
    - Run the following command:
    ```bash
    python ingest.py
    ```
    - *Note:* Ensure your chat file is at `c:/Users/AmbreenFathima/Downloads/personal/WhatsApp Chat with Fareed❤❤.txt` or update the path in `ingest.py`.

## 🚀 Running the App

Once ingestion is complete, launch the chatbot:

```bash
streamlit run app.py
```

## 💌 Features
- **History Aware**: Remembers the context of the conversation (last 5 messages).
- **Personalized**: Answers based *only* on your chat history.
- **Valentine's Theme**: Custom pink/red aesthetics.
- **Reset**: Button to clear conversation in the sidebar.

## ⚠️ Notes
## ☁️ Deployment (Streamlit Cloud)

1.  **Push to GitHub**:
    - Create a new repository on GitHub.
    - Push all files to the repository.
    - *Note:* Make sure `faiss_index` folder is included (or generated during build, but since it's local ingestion, better to commit it if it's small, or run `ingest.py` as part of startup if you commit the chat txt).
    - **Better Approach**: Commit the `faiss_index` folder directly so the cloud app doesn't need to rebuild it.

2.  **Deploy**:
    - Go to [share.streamlit.io](https://share.streamlit.io/).
    - Connect your GitHub account.
    - Select your repository and `app.py`.
    - **Advanced Settings**:
        - Copy the contents of your `.env` file into the "Secrets" section on Streamlit Cloud.
        - `GOOGLE_API_KEY = "..."`
        - `HUGGINGFACEHUB_API_TOKEN = "..."`

3.  **Launch**: Click Deploy and share the link with your Valentine! ❤️
