from typing import Dict, TypedDict, List, Annotated
import operator
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from backend.core.memory import get_retriever
from langgraph.checkpoint.memory import MemorySaver
import os
from backend.core.resilience import retry, CircuitBreaker

# --- SISTEMA DE RESILIENCIA CORPORATIVA (Cortafuegos HTTP) ---
# Evita quemar memoria/dinero si OpenAI o Pinecone están lentos o caídos
llm_breaker = CircuitBreaker(name="API OpenAI (GPT-4o)", failure_threshold=3)
vector_breaker = CircuitBreaker(name="Pinecone Base Vectorial", failure_threshold=3)

# Protegemos las llamadas críticas con Exponencial Backoff (1s -> 2s -> 4s de espera)
@retry(max_attempts=3, backoff_factor=2.0, exceptions=(Exception,))
def safe_llm_invoke(messages):
    return llm_breaker.call(lambda: llm.invoke(messages))

@retry(max_attempts=3, backoff_factor=2.0, exceptions=(Exception,))
def safe_retrieve(query):
    return vector_breaker.call(lambda: retriever.invoke(query))

# Definimos el "Estado" de la conversación.
class GraphState(TypedDict):
    question: str
    # LA MAGIA: operator.add le dice a LangGraph que en cada turno, debe SUMAR (appender) los mensajes, en vez de sobreescribirlos.
    history: Annotated[List[Dict[str, str]], operator.add]
    contextualized_question: str
    documents: List[Dict[str, str]]  # Array de diccionarios con content y metadata
    generation: str

# Configuración de los "Motores"
# Usamos GPT-4o con temperatura 0 para máxima precisión y cero creatividad/alucinación.
llm = ChatOpenAI(model="gpt-4o", temperature=0)
retriever = get_retriever()

# --- NODOS DEL GRAFO ---

def contextualize(state: GraphState):
    """Reescribe la pregunta del usuario considerando el historial de la base de datos interna."""
    print("🧠 [NODO 1] Contextualizando pregunta con la Memoria del Servidor (Thread)...")
    question = state["question"]
    history = state.get("history", [])
    
    if not history:
        print("   -> Primer mensaje del hilo, no hay contexto previo.")
        return {"contextualized_question": question}
        
    # Formateamos los últimos 6 mensajes reales para contexto
    hist_text = ""
    for msg in history[-6:]:
        rol = "Cliente" if msg["role"] == "user" else "Asistente"
        hist_text += f"\n{rol}: {msg['content']}"

    prompt = f"""Dada la siguiente historia de conversación y la 'Pregunta Actual' del cliente, tu tarea es reformular la pregunta actual para que sea una 'Pregunta Independiente' que pueda entenderse completamente sin necesidad de leer la historia.
    
    Historia reciente de la conversación:
    {hist_text}
    
    Pregunta Actual: {question}
    
    Escribe únicamente la pregunta independiente reformulada, sin explicaciones adicionales:"""
    
    # [PATRÓN DE SISTEMA EXPERTO] Usamos la llamada segura anti-caídas
    response = safe_llm_invoke([HumanMessage(content=prompt)])
    rephrased = response.content.strip()
    print(f"   -> Pregunta reformulada: '{rephrased}'")
    return {"contextualized_question": rephrased}


def retrieve(state: GraphState):
    """Busca en el manual de la empresa (Base de Conocimiento Local)."""
    print("🔍 [NODO 2] Recuperando información en la Vector DB Pinecone...")
    search_query = state.get("contextualized_question", state["question"])
    
    # [PATRÓN DE SISTEMA EXPERTO] Usamos llamada segura
    docs = safe_retrieve(search_query)
    
    # Extraemos el texto y su fuente (Añadiendo trazabilidad)
    doc_info = []
    for d in docs:
        fuente = d.metadata.get("source", "manual_interno")
        doc_info.append({
            "content": d.page_content,
            "metadata": f"Fuente: {fuente}"
        })
        
    return {"documents": doc_info}


def generate(state: GraphState):
    """Redacta la respuesta final usando todo el contexto recolectado y el historial persistido."""
    import datetime
    print("✍️ [NODO 3] Generando respuesta ejecutiva final...")
    question = state["question"]
    docs = state.get("documents", [])
    history = state.get("history", [])
    
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
    context = ""
    for idx, doc in enumerate(docs):
        context += f"\n--- Fragmento {idx+1} ({doc['metadata']}) ---\n"
        context += f"{doc['content']}\n"
    
    # Preparamos el historial para el LLM
    hist_text = ""
    for msg in history[-6:]:
        rol = "Cliente" if msg["role"] == "user" else "Tú (Asistente)"
        hist_text += f"\n{rol}: {msg['content']}"

    prompt = f"""Eres el Asistente Corporativo Premium de GlobalTech.
    Hoy es {fecha_actual}. 
    Tu tarea es responder la pregunta actual del cliente utilizando ÚNICAMENTE la información provista en el 'Contexto de la Base de Datos'.
    
    Historial reciente de la conversación (como referencia para mantener el hilo):
    {hist_text}
    
    Contexto de la Base de Datos (Políticas de la empresa):
    {context}
    
    Pregunta Actual: {question}
    
    Instrucciones críticas de tono y comportamiento:
    1. Si se te pregunta algo sobre la conversación pasada ("¿cuál fue mi último mensaje?") puedes responderlo basándote en el Historial reciente.
    2. Si el usuario hace preguntas en primera persona, NO digas que no tienes acceso a su información personal. Resuelve dándoles la regla general estipulada en el contexto.
    3. NUNCA comiences una frase disculpándote o dudando. Ve directo al grano.
    4. NUNCA inventes información que no esté en el contexto. Si no está en tus fragmentos, di amablemente que no posees esa directriz.
    """
    
    # [PATRÓN DE SISTEMA EXPERTO] Invocación LLM Protegida
    response = safe_llm_invoke([HumanMessage(content=prompt)])
    
    # MAGIA LEVEL 3: Insertamos la interacción a la Lista 'history'. 
    # Gracias a 'operator.add' en GraphState, esto no sobreescribe la memoria, sino que la acumula permanentemente.
    new_memory = [
        {"role": "user", "content": question},
        {"role": "ai", "content": response.content}
    ]
    
    return {"generation": response.content, "history": new_memory}

# --- CONSTRUCCIÓN DEL GRAFO (LangGraph) ---

def build_graph():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("contextualize", contextualize)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)
    
    workflow.set_entry_point("contextualize")
    workflow.add_edge("contextualize", "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    
    # CREAMOS EL DISCO DURO DEL CEREBRO
    memory_saver = MemorySaver()
    
    # Compilamos el grafo adjuntando la memoria a nivel base de datos (checkpointer)
    return workflow.compile(checkpointer=memory_saver)

# Instanciamos el agente "vivo"
rag_app = build_graph()
