
# -*- coding: utf-8 -*-

"""
Modulo de reservas del sistema Software FJ.
Desarrollado por el Integrante 3.

Responsabilidades:
- Crear y validar reservas.
- Confirmar y cancelar reservas.
- Procesar reservas y calcular su costo.
- Controlar los estados de cada reserva.
"""../reserva.py

from infraestructura import (
    EntidadBase,
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    registrar_errores,
)

from entidades import Cliente, Servicio


class Reserva(EntidadBase):
    """
    Clase encargada de administrar las reservas
    de clientes para los diferentes servicios.
    """

    PREFIJO_ID = "RES"

    ESTADOS_VALIDOS = (
        "PENDIENTE",
        "CONFIRMADA",
        "CANCELADA",
        "PROCESADA",
    )

    def __init__(self, cliente, servicio, duracion):
        """Inicializa una nueva reserva."""

        super().__init__()

        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._estado = "PENDIENTE"
        self._costo = None

        self.validar()

    # ==============================
    # PROPIEDADES DE LA RESERVA
    # ==============================

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def duracion(self):
        return self._duracion

    @property
    def estado(self):
        return self._estado

    @property
    def costo(self):
        return self._costo

    # ==============================
    # VALIDACION DE DATOS
    # ==============================

    @registrar_errores
    def validar(self):
        """Comprueba que los datos de la reserva sean correctos."""

        if not isinstance(self._cliente, Cliente):
            raise ReservaInvalidaError(
                "El cliente proporcionado no es valido."
            )

        if not isinstance(self._servicio, Servicio):
            raise ReservaInvalidaError(
                "El servicio proporcionado no es valido."
            )

        if not self._cliente.activo:
            raise ReservaInvalidaError(
                "El cliente no se encuentra activo."
            )

        if not self._servicio.activo:
            raise ReservaInvalidaError(
                "El servicio no se encuentra activo."
            )

        if not self._servicio.disponible:
            raise ReservaInvalidaError(
                "El servicio no se encuentra disponible."
            )

        if (
            isinstance(self._duracion, bool)
            or not isinstance(self._duracion, (int, float))
            or self._duracion <= 0
        ):
            raise ReservaInvalidaError(
                "La duracion debe ser un numero mayor que cero."
            )

        if self._estado not in self.ESTADOS_VALIDOS:
            raise ReservaInvalidaError(
                "El estado de la reserva no es valido."
            )

        return True

    # ==============================
    # CONFIRMAR RESERVA
    # ==============================

    @registrar_errores
    def confirmar(self):
        """Confirma una reserva que se encuentre pendiente."""

        self.validar()

        if self._estado != "PENDIENTE":
            raise OperacionNoPermitidaError(
                "Solo se pueden confirmar reservas pendientes."
            )

        self._estado = "CONFIRMADA"

        return "Reserva confirmada correctamente."

    # ==============================
    # CANCELAR RESERVA
    # ==============================

    @registrar_errores
    def cancelar(self):
        """Cancela una reserva pendiente o confirmada."""

        if self._estado not in ("PENDIENTE", "CONFIRMADA"):
            raise OperacionNoPermitidaError(
                "No se puede cancelar esta reserva."
            )

        self._estado = "CANCELADA"

        return "Reserva cancelada correctamente."

    # ==============================
    # PROCESAR RESERVA
    # ==============================

    @registrar_errores
    def procesar(self):
        """Procesa una reserva confirmada y calcula su costo."""

        self.validar()

        if self._estado != "CONFIRMADA":
            raise OperacionNoPermitidaError(
                "Solo se pueden procesar reservas confirmadas."
            )

        costo_calculado = self._servicio.calcular_costo(
            self._duracion
        )

        if (
            isinstance(costo_calculado, bool)
            or not isinstance(costo_calculado, (int, float))
            or costo_calculado <= 0
        ):
            raise ReservaInvalidaError(
                "El costo calculado para la reserva no es valido."
            )

        self._costo = round(costo_calculado, 2)
        self._estado = "PROCESADA"

        return self._costo

    # ==============================
    # DESCRIPCION DE LA RESERVA
    # ==============================

    def describir(self):
        """Devuelve una descripcion completa de la reserva."""

        return (
            f"Reserva [{self.id}]\n"
            f"Cliente: {self._cliente}\n"
            f"Servicio: {self._servicio}\n"
            f"Duracion: {self._duracion}\n"
            f"Estado: {self._estado}\n"
            f"Costo: {self._costo}"
        )
