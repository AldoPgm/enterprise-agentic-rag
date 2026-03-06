import os
import time
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "codigo_civil_ejemplo.txt")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "legal-rag")

def get_vector_store():
    """
    Gestiona la conexión con la base de datos vectorial en la nube (Pinecone).
    Si el índice no existe, lo crea e inserta los fragmentos (chunking) del manual.
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # 1. Inicializar cliente de Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    
    # 2. Verificar si el índice en la nube ya existe
    if INDEX_NAME not in pc.list_indexes().names():
        print(f"⚙️ Creando índice Serverless en Pinecone '{INDEX_NAME}'...")
        # El modelo text-embedding-3-small genera vectores de 1536 dimensiones
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        # Esperar a que el índice esté listo en la nube
        while not pc.describe_index(INDEX_NAME).status['ready']:
            time.sleep(1)
            
        print("📄 Indexando documentos privados (Esto suele hacerse solo una vez)...")
        loader = TextLoader(DATA_FILE, encoding='utf-8')
        docs = loader.load()
        
        # Fragmentación SEMÁNTICA (Chunking Enterprise)
        # Corta primero por párrafos dobles, luego simples, luego oraciones.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=100,
            separators=["\n\n", "\n", r"(?<=\. )", " ", ""]
        )
        splits = text_splitter.split_documents(docs)
        
        # Enriquecemos los metadatos para que el agente sepa CITAR sus fuentes
        for idx, doc in enumerate(splits):
            doc.metadata["chunk_id"] = f"{os.path.basename(DATA_FILE)}_chunk_{idx}"
            doc.metadata["source"] = os.path.basename(DATA_FILE)
        
        # Guardar en la nube (Pinecone)
        vectorstore = PineconeVectorStore.from_documents(
            documents=splits, 
            index_name=INDEX_NAME, 
            embedding=embeddings
        )
        print("✅ Indexación en Pinecone completada con éxito.")
        return vectorstore
    else:
        print("📥 Conectando de forma segura a la Base de Datos Pinecone...")
        # Simplemente instanciamos la conexión a los datos que ya existen
        return PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)

def get_retriever():
    # Buscamos los 2 fragmentos más relevantes de la nube
    return get_vector_store().as_retriever(search_kwargs={"k": 2})

