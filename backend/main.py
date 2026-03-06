from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Importar nuestro Cerebro Agentic (LangGraph)
from backend.agents.graph import rag_app

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="Enterprise Agentic RAG API",
    description="API para el Pilar 1: Agente RAG Corporativo con búsqueda web",
    version="1.0.0"
)

# Configurar CORS (Permitir que el Frontend Premium hable con este Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción, limitar al dominio de tu agencia
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de datos de entrada/salida
class UserQuery(BaseModel):
    query: str
    thread_id: str = "default_thread_123"

class AgentResponse(BaseModel):
    response: str
    sources: list[str]

@app.get("/")
async def root():
    return {"message": "El motor de Agentic RAG está en línea y seguro."}

@app.post("/chat", response_model=AgentResponse)
async def chat_endpoint(request: UserQuery):
    """
    Este endpoint recibe la pregunta desde el Frontend (sólo la pregunta y el ID de sesión)
    y ejecuta el grafo dejando que LangGraph gestione toda su memoria interna.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía.")
    
    print(f"\n--- [Thread ID: {request.thread_id}] Petición Recibida: '{request.query}' ---")
    
    # Invocamos el estado inicial de LangGraph (SOLO requiere la nueva pregunta)
    inputs = {
        "question": request.query
    }
    
    # CONFIGURACIÓN LEVEL 3: Insertamos la llave que abre el baúl de los recuerdos de este usuario
    config = {"configurable": {"thread_id": request.thread_id}}
    
    result = rag_app.invoke(inputs, config=config)
    
    # Extraemos las fuentes reales usadas en el turno (quitamos el texto 'Fuente: ' si existe)
    fuentes_usadas = []
    if "documents" in result:
        for doc in result["documents"]:
            nombre = doc["metadata"].replace("Fuente: ", "")
            if nombre not in fuentes_usadas:
                fuentes_usadas.append(nombre)
                
    # Mapeamos los resultados devueltos por el grafo al modelo de FastAPI
    return {
        "response": result["generation"],
        "sources": fuentes_usadas
    }

@app.post("/whatsapp-webhook")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(...),
    From: str = Form(...)
):
    """
    Endpoint nativo para recibir pings desde Twilio (WhatsApp/SMS).
    Utiliza validación criptográfica militar (RequestValidator) para evitar spoofing.
    """
    # 1. Blindaje de Seguridad: Validación de Firma de Twilio
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    if auth_token:
        validator = RequestValidator(auth_token)
        
        # Considerar proxies como Railway o Ngrok (HTTPS)
        forwarded_proto = request.headers.get("x-forwarded-proto", request.url.scheme)
        url = str(request.url.replace(scheme=forwarded_proto))
        
        form_data = await request.form()
        params = dict(form_data)
        signature = request.headers.get("X-Twilio-Signature", "")
        
        if not validator.validate(url, params, signature):
            print(f"🚨 [ALERTA DE SEGURIDAD] Petición falsa detectada y bloqueada (Firma HTTPS Inválida). IP: {request.client.host}")
            raise HTTPException(status_code=403, detail="Acceso denegado. Firma criptográfica inválida.")

    print(f"\n📲 [WhatsApp] Mensaje de {From}: '{Body}'")
    
    # Invocamos a nuestro agente usando el número de teléfono como la "llave" del cofre de memoria
    inputs = {"question": Body}
    config = {"configurable": {"thread_id": From}}
    
    result = rag_app.invoke(inputs, config=config)
    respuesta_ia = result["generation"]
    
    # Twilio requiere una respuesta sincrónica en formato TwiML (XML)
    twiml = MessagingResponse()
    twiml.message(respuesta_ia)
    
    return Response(content=str(twiml), media_type="application/xml")

# Si se ejecuta este archivo directamente
if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando Arquitectura de Servidor Backend High Ticket...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
