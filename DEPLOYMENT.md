# Deployment Guide for Streamlit Cloud

## 📋 Pre-Deployment Checklist

### Files to Include in GitHub
- ✅ `app.py` - Main Streamlit application
- ✅ `rag_engine.py` - RAG logic
- ✅ `requirements.txt` - Dependencies
- ✅ `faiss_index/` - Vector database (your chat memory)
- ✅ `.gitignore` - Excludes sensitive files

### Files to EXCLUDE (already in .gitignore)
- ❌ `.env` - Contains API keys
- ❌ `WhatsApp Chat with Fareed❤❤.txt` - Private chat data
- ❌ Debug/test scripts

## 🚀 Deployment Steps

### 1. Create GitHub Repository
1. Go to [github.com](https://github.com) and create a new repository
2. Name it something like `valentine-chatbot`
3. Choose **Private** if you want to keep the code private
4. Don't initialize with README (we already have files)

### 2. Push Code to GitHub
Open terminal in the project folder and run:

```bash
git init
git add .
git commit -m "Initial commit: Valentine's chatbot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/valentine-chatbot.git
git push -u origin main
```

### 3. Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Click "Sign in with GitHub"
3. Click "New app"
4. Fill in:
   - **Repository**: `YOUR_USERNAME/valentine-chatbot`
   - **Branch**: `main`
   - **Main file path**: `app.py`

### 4. Configure Secrets (IMPORTANT!)
1. Click "Advanced settings" before deploying
2. In the "Secrets" section, paste:

```toml
GROQ_API_KEY = "your_actual_groq_key_here"
GOOGLE_API_KEY = "your_actual_google_key_here"
HUGGINGFACEHUB_API_TOKEN = "your_actual_hf_token_here"
```

3. Replace the placeholder values with your actual API keys from `.env`

### 5. Deploy!
1. Click "Deploy"
2. Wait 2-3 minutes for deployment
3. Your app will be live at `https://YOUR_APP_NAME.streamlit.app`

## 🔒 Security Notes
- The GitHub repo can be private (recommended)
- API keys are stored securely in Streamlit Cloud secrets
- The deployed app will be publicly accessible (anyone with the URL can use it)
- To restrict access, you can add authentication or keep the URL private

## 🛠️ Updating the App
After deployment, to update:
```bash
git add .
git commit -m "Update message"
git push
```
Streamlit Cloud will auto-redeploy!

## ❤️ Enjoy!
Your Valentine's chatbot is now live and accessible from anywhere!
