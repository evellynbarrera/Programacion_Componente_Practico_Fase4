# -*- coding: utf-8 -*-
"""
entidades.py
============
Módulo de Datos y Servicios (POO) para la empresa Software FJ
(Curso Programación 213023 - UNAD, Fase 4).

Responsabilidad (Integrante 2):
- Clase Cliente con encapsulamiento y validaciones estrictas.
- Clase abstracta Servicio y sus 3 hijas: Salas, Equipos y Asesorias.
- Herencia, polimorfismo, sobrecarga vía parámetros opcionales y validaciones.
"""

from abc import ABC, abstractmethod

from infraestructura import (
    CalculoInconsistenteError,
    ClienteInvalidoError,
    EntidadBase,
    ParametroFaltanteError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
    SoftwareFJError,
    ValidacionError,
    registrar_errores,
    validar_numero_positivo,
    validar_texto,
)


class Cliente(EntidadBase):
    """
    Representa un cliente de Software FJ con encapsulamiento
    y validaciones estrictas en sus datos personales.
    """

    PREFIJO_ID = "CLI"

    def __init__(self, documento: str, nombre: str, correo: str, telefono: str):
        super().__init__()
        self.documento = documento
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.validar()

    @property
    def documento(self) -> str:
        """Documento / cédula del cliente (encapsulado)."""
        return self._documento

    @documento.setter
    def documento(self, valor: str) -> None:
        texto = validar_texto(valor, "documento", minimo=6, maximo=20)
        if not texto.isdigit():
            raise ClienteInvalidoError(
                "El documento del cliente debe contener solo dígitos numéricos",
                detalle=valor,
            )
        self._documento = texto

    @property
    def nombre(self) -> str:
        """Nombre completo del cliente (encapsulado)."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = validar_texto(valor, "nombre", minimo=3, maximo=100)

    @property
    def correo(self) -> str:
        """Correo electrónico del cliente (encapsulado)."""
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        texto = validar_texto(valor, "correo", minimo=5, maximo=120)
        if "@" not in texto or "." not in texto.split("@")[-1]:
            raise ClienteInvalidoError(
                "El correo electrónico del cliente no tiene un formato válido",
                detalle=valor,
            )
        self._correo = texto.lower()

    @property
    def telefono(self) -> str:
        """Teléfono de contacto del cliente (encapsulado)."""
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        texto = validar_texto(valor, "telefono", minimo=7, maximo=15)
        if not texto.isdigit():
            raise ClienteInvalidoError(
                "El teléfono del cliente debe contener solo dígitos numéricos",
                detalle=valor,
            )
        self._telefono = texto

    @registrar_errores
    def validar(self) -> bool:
        """Valida que todos los datos del cliente cumplan las reglas del negocio."""
        if not self.activo:
            raise ClienteInvalidoError(
                "El cliente se encuentra inactivo", detalle=self.id
            )
        # Revalida propiedades encapsuladas
        self.documento = self._documento
        self.nombre = self._nombre
        self.correo = self._correo
        self.telefono = self._telefono
        return True

    def describir(self) -> str:
        """Descripción legible del cliente."""
        return (
            f"Cliente [{self.id}] Doc: {self._documento} | Nombre: {self._nombre} | "
            f"Correo: {self._correo} | Tel: {self._telefono}"
        )


class Servicio(EntidadBase, ABC):
    """
    Clase abstracta raíz para los servicios ofrecidos por Software FJ.
    Define la interfaz común para cálculo de costos, validación y descripción.
    """

    PREFIJO_ID = "SER"

    def __init__(self, nombre: str, tarifa_base: float, disponible: bool = True):
        super().__init__()
        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self.disponible = disponible
        self.validar()

    @property
    def nombre(self) -> str:
        """Nombre del servicio (encapsulado)."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        try:
            self._nombre = validar_texto(valor, "nombre del servicio", minimo=3, maximo=100)
        except SoftwareFJError as exc:
            raise ServicioInvalidoError(
                "Nombre de servicio inválido", detalle=valor
            ) from exc

    @property
    def tarifa_base(self) -> float:
        """Tarifa base del servicio (encapsulado)."""
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor: float) -> None:
        try:
            monto = validar_numero_positivo(valor, "tarifa_base", permitir_cero=False)
        except SoftwareFJError as exc:
            raise ServicioInvalidoError(
                "La tarifa base del servicio debe ser un número mayor que cero",
                detalle=valor,
            ) from exc
        self._tarifa_base = round(monto, 2)

    @property
    def disponible(self) -> bool:
        """Indica si el servicio está disponible para reserva."""
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise ServicioInvalidoError(
                "El estado de disponibilidad debe ser booleano (True/False)",
                detalle=valor,
            )
        self._disponible = valor

    def _validar_duracion(self, duracion, etiqueta: str) -> float:
        """Valida que la duración/cantidad sea un número positivo."""
        try:
            cantidad = validar_numero_positivo(duracion, etiqueta, permitir_cero=False)
        except SoftwareFJError as exc:
            raise ServicioInvalidoError(
                f"Cantidad inválida para '{etiqueta}'", detalle=duracion
            ) from exc
        return cantidad

    def _aplicar_ajustes_costo(
        self,
        subtotal: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        recargo_extra: float = 0.0,
    ) -> float:
        """
        Aplica recargos, descuentos e impuestos con validación de consistencia.
        Permite simular distintas variantes/sobrecargas del cálculo de costo.
        """
        try:
            desc = validar_numero_positivo(descuento_pct, "descuento_pct", permitir_cero=True)
            imp = validar_numero_positivo(impuesto_pct, "impuesto_pct", permitir_cero=True)
            rec = validar_numero_positivo(recargo_extra, "recargo_extra", permitir_cero=True)
        except SoftwareFJError as exc:
            raise CalculoInconsistenteError(
                "Parámetros de descuento, impuesto o recargo inválidos"
            ) from exc

        if desc >= 100:
            raise CalculoInconsistenteError(
                "El porcentaje de descuento no puede ser igual o mayor al 100%",
                detalle=desc,
            )

        monto_bruto = subtotal + rec
        con_descuento = monto_bruto * (1 - desc / 100.0)
        total = con_descuento * (1 + imp / 100.0)

        if total <= 0:
            raise CalculoInconsistenteError(
                "El costo total calculado no es válido", detalle=total
            )

        return round(total, 2)

    @registrar_errores
    def validar(self) -> bool:
        """Valida que el servicio esté activo, disponible y con datos correctos."""
        if not self.activo:
            raise ServicioNoDisponibleError(
                "El servicio está inactivo en el sistema", detalle=self.id
            )
        if not self._disponible:
            raise ServicioNoDisponibleError(
                "El servicio no se encuentra disponible actualmente", detalle=self.id
            )
        self.nombre = self._nombre
        self.tarifa_base = self._tarifa_base
        return True

    @abstractmethod
    def calcular_costo(self, duracion, *args, **kwargs) -> float:
        """Calcula el costo del servicio según duración y parámetros opcionales."""

    @abstractmethod
    def describir_servicio(self) -> str:
        """Retorna la descripción específica del servicio."""

    def describir(self) -> str:
        """Implementación del método abstracto de EntidadBase."""
        return self.describir_servicio()


class Salas(Servicio):
    """Servicio especializado 1: Reserva de salas."""

    PREFIJO_ID = "SAL"

    def __init__(
        self,
        nombre: str,
        tarifa_base: float,
        capacidad: int,
        incluye_proyector: bool = True,
        disponible: bool = True,
    ):
        self.capacidad = capacidad
        self.incluye_proyector = incluye_proyector
        super().__init__(nombre=nombre, tarifa_base=tarifa_base, disponible=disponible)

    @property
    def capacidad(self) -> int:
        return self._capacidad

    @capacidad.setter
    def capacidad(self, valor: int) -> None:
        try:
            cap = validar_numero_positivo(valor, "capacidad", permitir_cero=False)
        except SoftwareFJError as exc:
            raise ServicioInvalidoError(
                "La capacidad de la sala debe ser mayor que cero", detalle=valor
            ) from exc
        if not float(cap).is_integer():
            raise ServicioInvalidoError(
                "La capacidad de la sala debe ser un número entero", detalle=valor
            )
        self._capacidad = int(cap)

    @property
    def incluye_proyector(self) -> bool:
        return self._incluye_proyector

    @incluye_proyector.setter
    def incluye_proyector(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise ServicioInvalidoError(
                "El campo 'incluye_proyector' debe ser booleano", detalle=valor
            )
        self._incluye_proyector = valor

    @registrar_errores
    def validar(self) -> bool:
        super().validar()
        self.capacidad = self._capacidad
        return True

    @registrar_errores
    def calcular_costo(
        self,
        duracion,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        recargo_aseo: float = 0.0,
    ) -> float:
        """
        Calcula el costo de reserva de sala por horas.
        Soporta variantes opcionales con descuento, impuesto y recargo de aseo.
        """
        horas = self._validar_duracion(duracion, "horas")
        subtotal = self._tarifa_base * horas
        return self._aplicar_ajustes_costo(
            subtotal=subtotal,
            descuento_pct=descuento_pct,
            impuesto_pct=impuesto_pct,
            recargo_extra=recargo_aseo,
        )

    def describir_servicio(self) -> str:
        proy = "Sí" if self._incluye_proyector else "No"
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"Sala [{self.id}] '{self._nombre}' | Capacidad: {self._capacidad} | "
            f"Proyector: {proy} | Tarifa/h: ${self._tarifa_base:.2f} | {estado}"
        )


class Equipos(Servicio):
    """Servicio especializado 2: Alquiler de equipos."""

    PREFIJO_ID = "EQP"

    def __init__(
        self,
        nombre: str,
        tarifa_base: float,
        especificaciones: str,
        con_seguro: bool = False,
        disponible: bool = True,
    ):
        self.especificaciones = especificaciones
        self.con_seguro = con_seguro
        super().__init__(nombre=nombre, tarifa_base=tarifa_base, disponible=disponible)

    @property
    def especificaciones(self) -> str:
        return self._especificaciones

    @especificaciones.setter
    def especificaciones(self, valor: str) -> None:
        try:
            self._especificaciones = validar_texto(
                valor, "especificaciones", minimo=3, maximo=150
            )
        except SoftwareFJError as exc:
            raise ServicioInvalidoError(
                "Las especificaciones del equipo son obligatorias", detalle=valor
            ) from exc

    @property
    def con_seguro(self) -> bool:
        return self._con_seguro

    @con_seguro.setter
    def con_seguro(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise ServicioInvalidoError(
                "El campo 'con_seguro' debe ser booleano", detalle=valor
            )
        self._con_seguro = valor

    @registrar_errores
    def validar(self) -> bool:
        super().validar()
        self.especificaciones = self._especificaciones
        return True

    @registrar_errores
    def calcular_costo(
        self,
        duracion,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        costo_seguro_diario: float = 15.0,
    ) -> float:
        """
        Calcula el costo de alquiler de equipos por días.
        Si el equipo tiene seguro activo, suma el seguro diario automáticamente.
        """
        dias = self._validar_duracion(duracion, "días")
        seguro_total = (costo_seguro_diario * dias) if self._con_seguro else 0.0
        subtotal = self._tarifa_base * dias
        return self._aplicar_ajustes_costo(
            subtotal=subtotal,
            descuento_pct=descuento_pct,
            impuesto_pct=impuesto_pct,
            recargo_extra=seguro_total,
        )

    def describir_servicio(self) -> str:
        seguro = "Con seguro" if self._con_seguro else "Sin seguro"
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"Equipo [{self.id}] '{self._nombre}' | Specs: {self._especificaciones} | "
            f"{seguro} | Tarifa/día: ${self._tarifa_base:.2f} | {estado}"
        )


class Asesorias(Servicio):
    """Servicio especializado 3: Asesorías especializadas."""

    PREFIJO_ID = "ASE"

    def __init__(
        self,
        nombre: str,
        tarifa_base: float,
        especialidad: str,
        modalidad: str = "Virtual",
        disponible: bool = True,
    ):
        self.especialidad = especialidad
        self.modalidad = modalidad
        super().__init__(nombre=nombre, tarifa_base=tarifa_base, disponible=disponible)

    @property
    def especialidad(self) -> str:
        return self._especialidad

    @especialidad.setter
    def especialidad(self, valor: str) -> None:
        try:
            self._especialidad = validar_texto(valor, "especialidad", minimo=3, maximo=100)
        except SoftwareFJError as exc:
            raise ServicioInvalidoError(
                "La especialidad de la asesoría es obligatoria", detalle=valor
            ) from exc

    @property
    def modalidad(self) -> str:
        return self._modalidad

    @modalidad.setter
    def modalidad(self, valor: str) -> None:
        texto = validar_texto(valor, "modalidad", minimo=3, maximo=30)
        modalidades_validas = {"Virtual", "Presencial", "Híbrida"}
        normalizada = texto.capitalize()
        if normalizada not in modalidades_validas:
            raise ServicioInvalidoError(
                "Modalidad no válida (use Virtual, Presencial o Híbrida)",
                detalle=valor,
            )
        self._modalidad = normalizada

    @registrar_errores
    def validar(self) -> bool:
        super().validar()
        self.especialidad = self._especialidad
        self.modalidad = self._modalidad
        return True

    @registrar_errores
    def calcular_costo(
        self,
        duracion,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        recargo_complejidad_pct: float = 0.0,
    ) -> float:
        """
        Calcula el costo de asesorías por horas/sesiones.
        Permite recargo opcional por complejidad y variantes de descuento/impuesto.
        """
        sesiones = self._validar_duracion(duracion, "sesiones")
        try:
            rec_comp = validar_numero_positivo(
                recargo_complejidad_pct, "recargo_complejidad_pct", permitir_cero=True
            )
        except SoftwareFJError as exc:
            raise CalculoInconsistenteError(
                "Recargo de complejidad inválido"
            ) from exc

        subtotal = (self._tarifa_base * sesiones) * (1 + rec_comp / 100.0)
        return self._aplicar_ajustes_costo(
            subtotal=subtotal,
            descuento_pct=descuento_pct,
            impuesto_pct=impuesto_pct,
        )

    def describir_servicio(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"Asesoría [{self.id}] '{self._nombre}' | Área: {self._especialidad} | "
            f"Modalidad: {self._modalidad} | Tarifa/sesión: ${self._tarifa_base:.2f} | {estado}"
        )


if __name__ == "__main__":
    from infraestructura import ejecutar_operacion

    print("=== Prueba rápida de entidades.py ===")
    c1 = ejecutar_operacion(
        "Crear cliente válido",
        Cliente,
        "1085234567",
        "Mónica Quiñones",
        "monica@correo.com",
        "3105551234",
    )
    print(c1)

    sala = ejecutar_operacion("Crear sala válida", Salas, "Sala Conferencias", 50.0, 20)
    equipo = ejecutar_operacion(
        "Crear equipo válido", Equipos, "Laptop Dev", 30.0, "16GB RAM / SSD 512GB", True
    )
    asesoria = ejecutar_operacion(
        "Crear asesoría válida", Asesorias, "Arquitectura Python", 80.0, "Backend & POO", "Virtual"
    )

    for srv in (sala, equipo, asesoría):
        if srv:
            print(srv.describir(), "-> Costo (2):", srv.calcular_costo(2))