
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableBranch
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

INDEX_DIRECTORY = "./faiss_index"

def get_rag_chain():
    # Embeddings (Multilingual)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    # Vector Store (FAISS)
    if not os.path.exists(INDEX_DIRECTORY):
        raise FileNotFoundError(f"FAISS index not found at {INDEX_DIRECTORY}. Please run ingest.py first.")
        
    vectorstore = FAISS.load_local(
        INDEX_DIRECTORY, 
        embeddings, 
        allow_dangerous_deserialization=True 
    )
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    # LLM
    google_key = os.getenv("GOOGLE_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if groq_key:
        llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0.7)
    elif google_key:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    else:
        raise ValueError("No API Key found. Please set GOOGLE_API_KEY or GROQ_API_KEY in .env")

    # Reformulate query based on history and expand with Thanglish keywords
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. \n\n"
        "IMPORTANT: The chat history contains messages in 'Thanglish' (Colloquial Tamil written in English script). "
        "Please expand the standalone question to include both English and relevant Thanglish/Tamil keywords "
        "to improve the accuracy of the search in the chat logs. \n"
        "Do NOT answer the question, just reformulate it or return it as is."
    )
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    history_aware_retriever = RunnableBranch(
        (
            lambda x: not x.get("chat_history", False),
            (lambda x: x["input"]) | retriever,
        ),
        (
            contextualize_q_prompt 
            | llm 
            | StrOutputParser() 
            | retriever
        ),
    )
    
    # --- Answer Chain ---
    system_prompt = (
        "You are a romantic, helpful AI assistant built for a Valentine's Day gift. "
        "You have access to the chat history of a couple. "
        "The context provided below contains excerpts from their WhatsApp chat history. "
        "The messages are often in Thanglish (Tamil written in English script). "
        "Use the retrieved context to answer the question about their relationship or history. "
        "Interpret colloquial Tamil phrases naturally in the context of their love story. "
        "If the answer is not in the context, say that you don't see it in the chat history provided. "
        "Keep the tone warm and friendly. "
        "Use three sentences maximum and keep the answer concise.\n\n"
        "{context}"
    )
    
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        RunnablePassthrough.assign(
            context=history_aware_retriever | format_docs
        )
        | qa_prompt
        | llm
        | StrOutputParser()
    )
    
    # Wrap to match expected output format dict with 'answer' key for app compatibility
    # Or modify app.py to expect string output. 
    # Let's keep it consistent: returns a dict-like runnable or change return type.
    # The original create_retrieval_chain returned a dict with input, context, and answer.
    # My simplified LCEL returns just the answer string.
    # I will stick to returning a dictionary to match app.py expectation: response["answer"]
    
    final_chain = (
        RunnablePassthrough.assign(
            context=history_aware_retriever | format_docs
        )
        | RunnablePassthrough.assign(
            answer=qa_prompt | llm | StrOutputParser()
        )
    )
    
    return final_chain
