import time
from functools import wraps
from typing import TypeVar, Callable
from enum import Enum
from datetime import datetime, timedelta

T = TypeVar('T')

# Patrón 1: Exponential Backoff (Reintentos Inteligentes)
def retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorador para reintentar funciones con un retraso exponencial (1s, 2s, 4s).
    Evita colapsar una API caída.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        sleep_time = backoff_factor ** attempt
                        print(f"⚠️ [RESILIENCE] Fallo en {func.__name__} ({e}). Reintentando en {sleep_time}s... (Intento {attempt + 1}/{max_attempts})")
                        time.sleep(sleep_time)
                        continue
                    raise
            print(f"❌ [RESILIENCE] Fallo crítico en {func.__name__} tras {max_attempts} intentos.")
            raise last_exception
        return wrapper
    return decorator

# Patrón 2: Circuit Breaker (Cortafuegos HTTP)
class CircuitState(Enum):
    CLOSED = "closed"       # Operación normal (La corriente fluye)
    OPEN = "open"           # Servicio caído (Se bloquean solicitudes)
    HALF_OPEN = "half_open" # Probando si el servicio resucitó

class CircuitBreaker:
    """
    Evita fallos en cascada. Si OpenAI o Pinecone caen, abre el circuito
    para devolver errores inmediatos sin hacer esperar al cliente y quemar CPU.
    """
    def __init__(
        self,
        name: str = "Service",
        failure_threshold: int = 3,
        timeout: timedelta = timedelta(seconds=30),
        success_threshold: int = 2
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None

    def call(self, func: Callable[[], T]) -> T:
        if self.state == CircuitState.OPEN:
            if datetime.now() - self.last_failure_time > self.timeout:
                print(f"🔄 [CIRCUIT BREAKER] Intentando reconexión a {self.name} (HALF-OPEN)...")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                # Cortocircuito: Falla rápido sin llamar a la API externa
                raise Exception(f"🔌 [{self.name}] Circuit Breaker ABIERTO. Servicio suspendido temporalmente por mantenimiento/caída.")

        try:
            result = func()
            self.on_success()
            return result
        except Exception as e:
            self.on_failure(e)
            raise

    def on_success(self):
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                print(f"✅ [CIRCUIT BREAKER] Servicio {self.name} recuperado (CLOSED).")
                self.state = CircuitState.CLOSED
                self.success_count = 0

    def on_failure(self, error: Exception):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        print(f"⚠️ [CIRCUIT BREAKER] Fallo {self.failure_count}/{self.failure_threshold} en {self.name}: {error}")
        if self.failure_count >= self.failure_threshold:
            if self.state != CircuitState.OPEN:
                print(f"🛑 [CIRCUIT BREAKER] ¡CIRCUITO ABIERTO en {self.name}! Bloqueando futuras peticiones.")
            self.state = CircuitState.OPEN
