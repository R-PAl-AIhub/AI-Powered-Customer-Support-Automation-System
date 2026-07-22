from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

embedding = OllamaEmbeddings(model="nomic-embed-text")

vector_db = FAISS.load_local(
    "knowldgeBase/ai_support_vector_db",embedding,allow_dangerous_deserialization = True)

retriver = vector_db.as_retriever(
    search_kwargs = {"k":3}
)