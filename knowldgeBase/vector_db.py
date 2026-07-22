import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

document = []
for files in os.listdir("knowldgeBase"):
    path = os.path.join("knowldgeBase", files)
    loader = TextLoader(path, encoding="utf-8")
    docs = loader.load()
    document.extend(docs)

splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap = 50
)

chunk = splitter.split_documents(
    document
)

print(f"Created {len(chunk)}chunks")

embedding = OllamaEmbeddings(model="nomic-embed-text")

vector_db = FAISS.from_documents(
    chunk,embedding
)

vector_db.save_local("knowldgeBase/ai_support_vector_db")
print("Vector database is created")