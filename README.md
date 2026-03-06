# Enterprise Agentic RAG: Sistema Multi-Canal Corporativo 🚀

Este es el **Pilar 1** del Portfolio de Automatización B2B/B2C. Es un Motor Neuronal Corporativo Privado diseñado para resolver cuellos de botella masivos de soporte al cliente o capacitación interna empresarial mediante una arquitectura *Retrieval-Augmented Generation* (RAG) ciega y resistente a alucinaciones.

## 💼 Caso de Uso Comercial (SaaS B2B/B2C)

Las empresas medianas (clínicas, e-commerces, concesionarias) pierden miles de dólares por soporte telefónico/chat demorado o ineficiente, requiriendo operadores humanos costosos para responder dudas repetitivas que se encuentran en el manual interno o el catálogo. 

**Este Agente resuelve ese problema drásticamente, ofreciendo un ROI positivo el primer mes:**
*   **Lee e interpreta instantáneamente** catálogos de cientos de páginas o Políticas de Recursos Humanos.
*   **Tiene memoria y entiende contexto** permitiendo a los usuarios hablar fluídamente (Ej: *"Y si me pasa eso, ¿cómo lo reclamo?"*).
*   **Arquitectura Dual/Omnicanal:** Un poderoso Backend de Python despacha texto tanto a un Dashboard Premium Web (para directivos/uso interno) como nativamente a Mensajería SMS/WhatsApp (para uso masivo B2C).

---

## 🏗️ Stack Tecnológico High-Ticket

### 1. Backend (El Motor Constante)
*   **FastAPI & Python 3:** Api Server ultra-veloz, asíncrono y listo para escalar a 1000s de peticiones/seg.
*   **LangGraph:** Motor de orquestación de agentes. No usamos IA lineal. Empleamos Nodos que Contextualizan el Historial, Extraen Data de la Base de Datos, y luego Redactan (Workflow Controlado).
*   **Pinecone Vector Database (Serverless):** Repositorio semántico ultraligero que transforma catálogos en vectores matemáticos.
*   **Integración Twilio Webhook:** Soporte nativo para WhatsApp/SMS Inbound/Outbound. Emplea el `To/From` como identificador único de Thread temporal en la memoria.

### 2. Frontend (La Percepción de Valor)
*   **React + Vite + Tailwind CSS V4:** Un dashboard SPA (Single Page Application) moderno.
*   **Framer Motion:** Animaciones, interpolación de colores (*Glassmorphism*) en tiempo real para un "Efecto WOW" en el Demo de Ventas, con indicadores del estado de la IA y el servidor en tiempo real.

---

## 🛠️ Instalación y Despliegue (Local)

Para correr la suite en tu computadora:

### Backend
1. Navegar a `backend/`: `cd backend`
2. Instalar dependencias puras: `pip install -r requirements.txt`
3. Renombrar `.env.example` a `.env` y poner tus llaves de **OpenAI** y **Pinecone**.
4. Iniciar el motor en el puerto 8000: `python -m backend.main`

### Frontend
1. Abrir otra terminal y navegar a `frontend/`: `cd frontend`
2. Instalar el empaquetador node: `npm install`
3. Desplegar servidor local Vite (Puerto 5173): `npm run dev`

---

## 🚀 Despliegue de Grado Comercial (Producción)

1. **El Backend** se empuja directamente a un contenedor en `Railway` o `Render`. (FastAPI es nativo allí).
2. **El Frontend** se sube directamente a `Vercel` bajo una URL propia. (Recuerda actualizar la variable de `API_URL` en React por el Host de tu Backend final).
3. Entras al portal de `Twilio` y configuras el **Webhook** ingresante apuntando hacia la ruta `TU-URL-BACKEND.com/whatsapp-webhook`.

*Todos los sistemas mantendrán la confidencialidad persistente dividiendo la memoria a través de tokens matemáticos dinámicos (Thread IDs).*
