
import os
import re
import sys
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

# Enhance console output for Windows with emojis
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Configuration
CHAT_FILE_PATH = r"c:/Users/AmbreenFathima/Downloads/personal/WhatsApp Chat with Fareed❤❤.txt"
INDEX_DIRECTORY = "./faiss_index"

def clean_chat_line(line):
    # Regex for WhatsApp timestamp: "dd/mm/yyyy, h:mm pm - "
    pattern = r"^(\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}[\s\u202f]?[ap]m)\s+-\s+"
    
    match = re.search(pattern, line.lower())
    if not match:
        return None 
    
    timestamp = match.group(1)  # Extract timestamp
    content = line[match.end():]  # Content after timestamp
    
    # System Message Filters
    if content.startswith("Messages and calls are end-to-end encrypted"): return None
    if "Media omitted" in content: return None
    if content.endswith("is a contact"): return None 
    if content.startswith("You updated the message timer"): return None
    if content.startswith("You turned off disappearing messages"): return None
    if content.strip() == "You deleted this message": return None
    if content.startswith("Cards are not supported"): return None

    # Extract sender and message
    if ": " in content:
        sender, message = content.split(": ", 1)
        return {
            "timestamp": timestamp.strip(),
            "sender": sender.strip(),
            "content": message.strip()
        }
    else:
        return None

def ingest_data():
    print(f"Loading chat from {CHAT_FILE_PATH}...")
    
    if not os.path.exists(CHAT_FILE_PATH):
        print(f"Error: File not found at {CHAT_FILE_PATH}")
        return

    with open(CHAT_FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cleaned_messages = []
    
    for line in lines:
        parsed = clean_chat_line(line)
        if parsed:
            cleaned_messages.append(parsed)
    
    print(f"Processed {len(lines)} lines into {len(cleaned_messages)} clean messages.")

    # Create documents with metadata
    documents = []
    texts = []
    metadatas = []
    
    for msg in cleaned_messages:
        text = f"{msg['sender']}: {msg['content']}"
        texts.append(text)
        metadatas.append({
            "timestamp": msg['timestamp'],
            "sender": msg['sender']
        })
    
    # Combine all messages into one text for splitting
    full_text = "\n".join(texts)
    
    # Split text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    # Create documents with metadata preserved
    # Note: When splitting, we'll use the first message's metadata for each chunk
    docs = text_splitter.create_documents([full_text])
    
    # Add generic metadata to chunks (since chunks may span multiple messages)
    for doc in docs:
        doc.metadata = {"source": "whatsapp_chat"}
    
    print(f"Split into {len(docs)} chunks.")

    # Check for API Key
    if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
        print("WARNING: HUGGINGFACEHUB_API_TOKEN not found in .env. Please add it.")
        return

    # Embeddings
    print("Initializing Embeddings (HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Vector Store
    print("Creating FAISS Index...")
    try:
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local(INDEX_DIRECTORY)
        print(f"Ingestion complete! FAISS index saved to {INDEX_DIRECTORY}")
    except Exception as e:
        print(f"Error creating/saving FAISS index: {e}")

if __name__ == "__main__":
    ingest_data()
