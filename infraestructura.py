# -*- coding: utf-8 -*-
"""
infraestructura.py
==================
Módulo base del Sistema Integral de Gestión de Clientes, Servicios y Reservas
de la empresa Software FJ (Curso Programación 213023 - UNAD, Fase 4).

Responsabilidad de este módulo (Integrante 1 - Infraestructura y Logs):
    1. Configurar el sistema de registro de eventos y errores (logging) en archivo.
    2. Definir la jerarquía de excepciones personalizadas del sistema.
    3. Definir la clase abstracta raíz EntidadBase, de la que heredan
       Cliente, Servicio y Reserva (módulos entidades.py y reserva.py).
    4. Ofrecer utilidades de ejecución segura (try/except/else/finally)
       para que main.py ejecute operaciones sin que el programa se detenga.

Este módulo NO usa bases de datos: los eventos se guardan en un archivo de
texto (logs/software_fj.log) tal como lo exige el enunciado.
"""

# ---------------------------------------------------------------------------
# IMPORTACIONES
# ---------------------------------------------------------------------------
import logging                                  # Librería estándar para registrar eventos y errores
import os                                       # Permite crear la carpeta de logs si no existe
from abc import ABC, abstractmethod             # ABC = clase base abstracta; abstractmethod = método obligatorio en hijas
from datetime import datetime                   # Para registrar la fecha de creación de cada entidad
from functools import wraps                     # Conserva el nombre/documentación de funciones decoradas
from itertools import count                     # Generador de números consecutivos para los IDs


# ===========================================================================
# 1. CONFIGURACIÓN DEL SISTEMA DE LOGS
# ===========================================================================

CARPETA_LOGS = "logs"                                        # Carpeta donde se guardará el archivo de logs
ARCHIVO_LOGS = os.path.join(CARPETA_LOGS, "software_fj.log") # Ruta completa del archivo de logs
NOMBRE_LOGGER = "SoftwareFJ"                                 # Nombre del logger principal del sistema
FORMATO_LOG = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"  # Fecha | nivel | módulo | mensaje
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"                          # Formato de fecha legible: 2026-11-11 12:30:00


def configurar_logger(nivel_archivo=logging.DEBUG, nivel_consola=logging.INFO):
    """
    Crea (una sola vez) y devuelve el logger principal del sistema.

    - Escribe TODOS los eventos (DEBUG en adelante) en logs/software_fj.log.
    - Muestra en consola los eventos de nivel INFO en adelante.
    - Si se llama varias veces, no duplica los manejadores (handlers).

    :param nivel_archivo: nivel mínimo que se guarda en el archivo.
    :param nivel_consola: nivel mínimo que se muestra en pantalla.
    :return: objeto logging.Logger listo para usar.
    """
    logger = logging.getLogger(NOMBRE_LOGGER)   # Obtiene (o crea) el logger con el nombre del sistema
    if logger.handlers:                         # Si ya tiene manejadores, ya fue configurado antes
        return logger                           # Se devuelve tal cual para no duplicar líneas en el log

    os.makedirs(CARPETA_LOGS, exist_ok=True)    # Crea la carpeta logs/ si no existe (no falla si ya existe)
    logger.setLevel(logging.DEBUG)              # El logger acepta todos los niveles; los handlers filtran
    formato = logging.Formatter(FORMATO_LOG, datefmt=FORMATO_FECHA)  # Formato común para archivo y consola

    manejador_archivo = logging.FileHandler(ARCHIVO_LOGS, encoding="utf-8")  # Escribe en el archivo con tildes/ñ
    manejador_archivo.setLevel(nivel_archivo)   # Nivel mínimo que se guarda en el archivo
    manejador_archivo.setFormatter(formato)     # Aplica el formato definido
    logger.addHandler(manejador_archivo)        # Conecta el manejador de archivo al logger

    manejador_consola = logging.StreamHandler() # Muestra los mensajes en la terminal
    manejador_consola.setLevel(nivel_consola)   # En pantalla solo INFO, WARNING, ERROR y CRITICAL
    manejador_consola.setFormatter(formato)     # Mismo formato que el archivo
    logger.addHandler(manejador_consola)        # Conecta el manejador de consola al logger

    logger.propagate = False                    # Evita que los mensajes se repitan en el logger raíz
    return logger                               # Devuelve el logger configurado


def obtener_logger(modulo=None):
    """
    Devuelve un logger hijo para un módulo concreto (ej. 'entidades', 'reserva').
    Los mensajes quedan en el mismo archivo pero identificados por módulo:
        SoftwareFJ.entidades, SoftwareFJ.reserva, etc.

    :param modulo: nombre corto del módulo que va a registrar eventos.
    :return: logging.Logger hijo del logger principal.
    """
    configurar_logger()                                     # Garantiza que el logger principal exista
    if modulo:                                              # Si se indicó un módulo...
        return logging.getLogger(f"{NOMBRE_LOGGER}.{modulo}")  # ...se crea un logger hijo con ese nombre
    return logging.getLogger(NOMBRE_LOGGER)                 # Si no, se devuelve el logger principal


logger = obtener_logger("infraestructura")  # Logger propio de este módulo


# ===========================================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ===========================================================================
# Jerarquía:
#   SoftwareFJError                      (raíz: todas las del sistema)
#   ├── ValidacionError                  (datos inválidos)
#   │   ├── ParametroFaltanteError       (falta un dato obligatorio)
#   │   └── ClienteInvalidoError         (datos del cliente incorrectos)
#   ├── ServicioError                    (problemas con servicios)
#   │   ├── ServicioInvalidoError        (servicio mal creado / parámetros erróneos)
#   │   └── ServicioNoDisponibleError    (servicio inactivo u ocupado)
#   ├── ReservaError                     (problemas con reservas)
#   │   ├── ReservaInvalidaError         (datos de reserva incorrectos)
#   │   └── OperacionNoPermitidaError    (ej. cancelar algo ya cancelado)
#   └── CalculoInconsistenteError        (costos negativos, descuentos imposibles)
# ===========================================================================

class SoftwareFJError(Exception):
    """
    Excepción raíz del sistema. Todas las excepciones propias heredan de ella,
    así main.py puede capturar cualquier error del negocio con un solo except.

    Cada excepción guarda un código y un mensaje, y se registra
    automáticamente en el archivo de logs al ser creada.
    """

    codigo = "FJ-000"  # Código genérico; cada subclase define el suyo

    def __init__(self, mensaje="Error en el sistema Software FJ", detalle=None):
        """
        :param mensaje: descripción legible del error.
        :param detalle: información adicional opcional (dato recibido, campo, etc.).
        """
        self.mensaje = mensaje                  # Guarda el mensaje principal
        self.detalle = detalle                  # Guarda el detalle adicional (puede ser None)
        super().__init__(self.__str__())        # Inicializa Exception con el texto completo
        logger.debug("Excepción creada -> %s", self.__str__())  # Deja rastro técnico en el log

    def __str__(self):
        """Representación en texto: [código] mensaje (detalle)."""
        texto = f"[{self.codigo}] {self.mensaje}"   # Arma el texto base con el código
        if self.detalle is not None:                # Si hay detalle...
            texto += f" | Detalle: {self.detalle}"  # ...se agrega al final
        return texto                                # Devuelve el texto completo


# --- Validación de datos ---------------------------------------------------
class ValidacionError(SoftwareFJError):
    """Datos de entrada inválidos (tipo, formato o rango incorrecto)."""
    codigo = "FJ-100"


class ParametroFaltanteError(ValidacionError):
    """Falta un parámetro obligatorio o llegó vacío."""
    codigo = "FJ-101"


class ClienteInvalidoError(ValidacionError):
    """Los datos del cliente (nombre, documento, correo, teléfono) no son válidos."""
    codigo = "FJ-102"


# --- Servicios ---------------------------------------------------------------
class ServicioError(SoftwareFJError):
    """Error general relacionado con los servicios (salas, equipos, asesorías)."""
    codigo = "FJ-200"


class ServicioInvalidoError(ServicioError):
    """El servicio se intentó crear o configurar con parámetros incorrectos."""
    codigo = "FJ-201"


class ServicioNoDisponibleError(ServicioError):
    """El servicio existe pero no está disponible (inactivo, ocupado, sin cupo)."""
    codigo = "FJ-202"


# --- Reservas ----------------------------------------------------------------
class ReservaError(SoftwareFJError):
    """Error general relacionado con reservas."""
    codigo = "FJ-300"


class ReservaInvalidaError(ReservaError):
    """La reserva tiene datos incorrectos (duración, cliente o servicio inválido)."""
    codigo = "FJ-301"


class OperacionNoPermitidaError(ReservaError):
    """La operación no se permite en el estado actual (ej. confirmar una cancelada)."""
    codigo = "FJ-302"


# --- Cálculos ------------------------------------------------------------------
class CalculoInconsistenteError(SoftwareFJError):
    """Resultado de cálculo imposible: costo negativo, descuento > 100 %, etc."""
    codigo = "FJ-400"


# ===========================================================================
# 3. FUNCIONES DE VALIDACIÓN REUTILIZABLES
# ===========================================================================
# Los demás módulos las usan para no repetir código de validación.

def validar_texto(valor, campo, minimo=1, maximo=100):
    """
    Verifica que 'valor' sea un texto no vacío con longitud entre minimo y maximo.

    :raises ParametroFaltanteError: si el valor es None o está vacío.
    :raises ValidacionError: si no es texto o su longitud está fuera de rango.
    :return: el texto sin espacios sobrantes.
    """
    if valor is None or (isinstance(valor, str) and not valor.strip()):    # None o "" o "   "
        raise ParametroFaltanteError(f"El campo '{campo}' es obligatorio")  # Falta el dato
    if not isinstance(valor, str):                                          # No es texto
        raise ValidacionError(f"El campo '{campo}' debe ser texto", detalle=repr(valor))
    limpio = valor.strip()                                                  # Quita espacios al inicio y final
    if not (minimo <= len(limpio) <= maximo):                               # Longitud fuera de rango
        raise ValidacionError(
            f"El campo '{campo}' debe tener entre {minimo} y {maximo} caracteres",
            detalle=limpio,
        )
    return limpio                                                           # Devuelve el texto validado


def validar_numero_positivo(valor, campo, permitir_cero=False):
    """
    Verifica que 'valor' sea un número (int o float) positivo.

    Usa ENCADENAMIENTO DE EXCEPCIONES (raise ... from ...): si la conversión
    falla, la excepción original (ValueError/TypeError) queda guardada en
    __cause__ para poder rastrear el origen del problema en el log.

    :raises ParametroFaltanteError: si el valor es None.
    :raises ValidacionError: si no es numérico o no es positivo.
    :return: el valor convertido a float.
    """
    if valor is None:                                                       # No llegó el dato
        raise ParametroFaltanteError(f"El campo '{campo}' es obligatorio")
    if isinstance(valor, bool):                                             # True/False no son cantidades válidas
        raise ValidacionError(f"El campo '{campo}' debe ser numérico", detalle=repr(valor))
    try:                                                                    # Intenta convertir a número
        numero = float(valor)
    except (TypeError, ValueError) as error_original:                       # Falló la conversión
        raise ValidacionError(                                              # Lanza la excepción propia...
            f"El campo '{campo}' debe ser numérico", detalle=repr(valor)
        ) from error_original                                               # ...encadenada con la original
    if numero < 0 or (numero == 0 and not permitir_cero):                   # Negativo, o cero no permitido
        raise ValidacionError(f"El campo '{campo}' debe ser mayor que cero", detalle=numero)
    return numero                                                           # Devuelve el número validado


# ===========================================================================
# 4. CLASE ABSTRACTA RAÍZ: EntidadBase
# ===========================================================================

class EntidadBase(ABC):
    """
    Clase abstracta que representa cualquier entidad general del sistema
    (Cliente, Servicio, Reserva). No se puede instanciar directamente.

    Aporta a todas las hijas:
        - Un ID único y consecutivo por tipo (ej. CLI-0001, SER-0002, RES-0003).
        - La fecha y hora de creación.
        - Un estado activo/inactivo.
        - Registro automático en el log al crearse.

    Obliga a las hijas a implementar:
        - validar():   revisa que los datos de la entidad sean correctos.
        - describir(): devuelve un texto que describe la entidad.
    """

    _contador_ids = count(1)   # Generador compartido de números consecutivos (1, 2, 3, ...)
    PREFIJO_ID = "ENT"         # Prefijo por defecto; cada hija lo puede cambiar (CLI, SER, RES)

    def __init__(self):
        """Inicializa los atributos comunes. Las hijas deben llamar a super().__init__()."""
        numero = next(EntidadBase._contador_ids)                  # Toma el siguiente número disponible
        self.__id = f"{self.PREFIJO_ID}-{numero:04d}"             # ID privado, ej. CLI-0001 (encapsulado)
        self.__fecha_creacion = datetime.now()                    # Fecha de creación privada
        self._activo = True                                       # Estado protegido; las hijas pueden cambiarlo
        self._log = obtener_logger(self.__class__.__name__.lower())  # Logger propio de la clase hija
        self._log.debug("Entidad creada: %s (%s)", self.__id, self.__class__.__name__)

    # --- Propiedades de solo lectura (encapsulación) ---------------------
    @property
    def id(self):
        """ID único de la entidad (solo lectura: no tiene setter)."""
        return self.__id

    @property
    def fecha_creacion(self):
        """Fecha y hora en que se creó la entidad (solo lectura)."""
        return self.__fecha_creacion

    @property
    def activo(self):
        """Indica si la entidad está activa."""
        return self._activo

    # --- Métodos comunes -------------------------------------------------
    def desactivar(self):
        """Marca la entidad como inactiva. No se puede desactivar dos veces."""
        if not self._activo:                                      # Ya estaba inactiva
            raise OperacionNoPermitidaError(
                "La entidad ya se encuentra inactiva", detalle=self.__id
            )
        self._activo = False                                      # Cambia el estado
        self._log.info("Entidad %s desactivada", self.__id)       # Registra el evento

    # --- Métodos abstractos (obligatorios en las hijas) ------------------
    @abstractmethod
    def validar(self):
        """
        Debe revisar los datos de la entidad y lanzar una excepción
        de la jerarquía SoftwareFJError si algo es incorrecto.
        """

    @abstractmethod
    def describir(self):
        """Debe devolver un texto que describa la entidad."""

    # --- Representaciones ------------------------------------------------
    def __str__(self):
        """Texto amigable: usa la descripción de la clase hija (polimorfismo)."""
        return self.describir()

    def __repr__(self):
        """Texto técnico para depuración."""
        return f"<{self.__class__.__name__} id={self.__id} activo={self._activo}>"


# ===========================================================================
# 5. UTILIDADES DE EJECUCIÓN SEGURA (para main.py)
# ===========================================================================

def ejecutar_operacion(descripcion, funcion, *args, **kwargs):
    """
    Ejecuta una operación del sistema sin que un error detenga el programa.
    Demuestra la estructura completa try / except / else / finally:

        try     -> intenta ejecutar la operación.
        except  -> captura errores propios (SoftwareFJError) y luego cualquier
                   error inesperado (Exception), y los registra en el log.
        else    -> solo se ejecuta si NO hubo error: registra el éxito.
        finally -> se ejecuta SIEMPRE: registra el cierre de la operación.

    Uso en main.py:
        cliente = ejecutar_operacion("Registrar cliente Ana", Cliente, "Ana", "123", ...)

    :param descripcion: texto que identifica la operación en el log.
    :param funcion: función, método o clase a ejecutar.
    :return: el resultado de la función, o None si hubo error.
    """
    resultado = None                                              # Valor por defecto si algo falla
    logger.info(">>> Inicio operación: %s", descripcion)          # Registra el inicio
    try:
        resultado = funcion(*args, **kwargs)                      # Ejecuta la operación solicitada
    except SoftwareFJError as error:                              # Error controlado del negocio
        logger.error("Operación fallida (%s): %s", descripcion, error)
        if error.__cause__ is not None:                           # Si viene encadenada...
            logger.error("   Causa original: %s: %s",             # ...registra también el origen
                         type(error.__cause__).__name__, error.__cause__)
    except Exception as error:                                    # Error inesperado (bug, tipo, etc.)
        logger.critical("Error inesperado en '%s': %s: %s",
                        descripcion, type(error).__name__, error, exc_info=True)  # Guarda traza completa
    else:                                                         # Solo si no hubo excepción
        logger.info("Operación exitosa: %s", descripcion)
    finally:                                                      # Siempre se ejecuta
        logger.info("<<< Fin operación: %s", descripcion)
    return resultado                                              # Devuelve el resultado o None


def registrar_errores(funcion):
    """
    Decorador opcional: registra en el log cualquier SoftwareFJError que lance
    la función decorada y lo vuelve a lanzar (no lo oculta).
    Útil para métodos como Reserva.confirmar() o Servicio.calcular_costo().

    Ejemplo:
        @registrar_errores
        def confirmar(self): ...
    """
    @wraps(funcion)                                               # Mantiene nombre y docstring originales
    def envoltura(*args, **kwargs):
        try:
            return funcion(*args, **kwargs)                       # Ejecuta la función original
        except SoftwareFJError as error:                          # Si lanza un error propio...
            logger.warning("Error en %s(): %s", funcion.__name__, error)  # ...lo registra
            raise                                                 # ...y lo vuelve a lanzar sin cambios
    return envoltura


# ===========================================================================
# 6. PRUEBA RÁPIDA DEL MÓDULO
# ===========================================================================
# Se ejecuta solo con:  python infraestructura.py
# No se ejecuta cuando otro archivo hace "import infraestructura".

if __name__ == "__main__":

    class _EntidadPrueba(EntidadBase):
        """Entidad mínima solo para probar EntidadBase."""
        PREFIJO_ID = "TST"

        def __init__(self, nombre):
            super().__init__()                                    # Inicializa ID, fecha y estado
            self.nombre = validar_texto(nombre, "nombre")         # Valida el nombre

        def validar(self):
            validar_texto(self.nombre, "nombre")                  # Reutiliza la validación
            return True

        def describir(self):
            return f"Entidad de prueba {self.id}: {self.nombre}"

    print("=== Prueba de infraestructura.py ===")

    # 1) No se puede instanciar la clase abstracta
    ejecutar_operacion("Instanciar EntidadBase directamente", EntidadBase)

    # 2) Entidad válida
    e = ejecutar_operacion("Crear entidad válida", _EntidadPrueba, "Sala A")
    print("Creada:", e, "|", repr(e))

    # 3) Parámetro faltante
    ejecutar_operacion("Crear entidad sin nombre", _EntidadPrueba, "   ")

    # 4) Encadenamiento de excepciones
    ejecutar_operacion("Validar número inválido", validar_numero_positivo, "abc", "precio")

    # 5) Operación no permitida (desactivar dos veces)
    ejecutar_operacion("Desactivar entidad", e.desactivar)
    ejecutar_operacion("Desactivar entidad otra vez", e.desactivar)

    # 6) Error inesperado (no es del negocio): el programa sigue
    ejecutar_operacion("División por cero", lambda: 1 / 0)

    print(f"\nEl programa terminó sin detenerse. Revise el archivo: {ARCHIVO_LOGS}")
