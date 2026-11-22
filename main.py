
# -*- coding: utf-8 -*-

"""
PROYECTO SOFTWARE FJ
Sistema Integral de Gestion de Clientes, Servicios y Reservas.

Integrante 4: Programa principal (main.py).
Integra las clases de los integrantes anteriores y ejecuta
operaciones exitosas y pruebas de errores.
"""

# IMPORTACIONES

from infraestructura import ejecutar_operacion
from entidades import Cliente, Salas, Equipos, Asesorias
from reserva import Reserva


def main():

    print("=" * 55)
    print(" SISTEMA INTEGRAL DE GESTION SOFTWARE FJ")
    print("=" * 55)

    # ==================================================
    # 1. CREACION DE CLIENTE VALIDO
    # ==================================================

    print("\n1. REGISTRAR CLIENTE VALIDO")

    cliente = ejecutar_operacion(
        "Registrar cliente valido",
        Cliente,
        "1085234567",
        "Juan Perez",
        "juan@gmail.com",
        "3105551234"
    )

    if cliente is not None:
        print(cliente.describir())

    # ==================================================
    # 2. CREACION DE CLIENTE INVALIDO
    # ==================================================

    print("\n2. REGISTRAR CLIENTE INVALIDO")

    cliente_invalido = ejecutar_operacion(
        "Registrar cliente con datos incorrectos",
        Cliente,
        "123",
        "A",
        "correo_invalido",
        "123"
    )

    print("Resultado:", cliente_invalido)

    # ==================================================
    # 3. CREACION DE SALA
    # ==================================================

    print("\n3. CREAR SERVICIO DE SALA")

    sala = ejecutar_operacion(
        "Crear sala de reuniones",
        Salas,
        "Sala de reuniones",
        50000,
        20,
        True
    )

    if sala is not None:
        print(sala.describir())

    # ==================================================
    # 4. CREACION DE SERVICIO INVALIDO
    # ==================================================

    print("\n4. CREAR SERVICIO CON DATOS INVALIDOS")

    sala_invalida = ejecutar_operacion(
        "Crear sala con capacidad incorrecta",
        Salas,
        "Sala invalida",
        50000,
        0
    )

    print("Resultado:", sala_invalida)

    # ==================================================
    # 5. CREACION DE EQUIPO
    # ==================================================

    print("\n5. CREAR SERVICIO DE EQUIPOS")

    equipo = ejecutar_operacion(
        "Crear equipo audiovisual",
        Equipos,
        "Proyector audiovisual",
        30000,
        "Proyector Full HD",
        True
    )

    if equipo is not None:
        print(equipo.describir())

    # ==================================================
    # 6. CREACION DE ASESORIA
    # ==================================================

    print("\n6. CREAR SERVICIO DE ASESORIA")

    asesoria = ejecutar_operacion(
        "Crear asesoria de programacion",
        Asesorias,
        "Asesoria de programacion",
        60000,
        "Desarrollo de software",
        "Virtual"
    )

    if asesoria is not None:
        print(asesoria.describir())

    # ==================================================
    # 7. CREACION DE RESERVA VALIDA
    # ==================================================

    print("\n7. CREAR RESERVA VALIDA")

    reserva = None

    if cliente is not None and sala is not None:
        reserva = ejecutar_operacion(
            "Crear reserva de sala",
            Reserva,
            cliente,
            sala,
            2
        )

    if reserva is not None:
        print(reserva.describir())

    # ==================================================
    # 8. CREACION DE RESERVA INVALIDA
    # ==================================================

    print("\n8. CREAR RESERVA CON DURACION INVALIDA")

    if cliente is not None and sala is not None:
        reserva_invalida = ejecutar_operacion(
            "Crear reserva con duracion cero",
            Reserva,
            cliente,
            sala,
            0
        )

        print("Resultado:", reserva_invalida)

    # ==================================================
    # 9. INTENTAR PROCESAR RESERVA PENDIENTE
    # ==================================================

    print("\n9. INTENTAR PROCESAR RESERVA PENDIENTE")

    if reserva is not None:
        resultado = ejecutar_operacion(
            "Intentar procesar reserva pendiente",
            reserva.procesar
        )

        print("Resultado:", resultado)

    # ==================================================
    # 10. CONFIRMAR RESERVA
    # ==================================================

    print("\n10. CONFIRMAR RESERVA")

    if reserva is not None:
        resultado = ejecutar_operacion(
            "Confirmar reserva",
            reserva.confirmar
        )

        print("Resultado:", resultado)
        print("Estado:", reserva.estado)

    # ==================================================
    # 11. PROCESAR RESERVA
    # ==================================================

    print("\n11. PROCESAR RESERVA")

    if reserva is not None:
        costo = ejecutar_operacion(
            "Procesar reserva confirmada",
            reserva.procesar
        )

        print("Costo total:", costo)
        print("Estado:", reserva.estado)

    # ==================================================
    # 12. CREAR OTRA RESERVA PARA CANCELAR
    # ==================================================

    print("\n12. CREAR RESERVA PARA CANCELACION")

    reserva_cancelable = None

    if cliente is not None and sala is not None:
        reserva_cancelable = ejecutar_operacion(
            "Crear reserva para cancelar",
            Reserva,
            cliente,
            sala,
            1
        )

    if reserva_cancelable is not None:
        print("Estado inicial:", reserva_cancelable.estado)

    # ==================================================
    # 13. CANCELAR RESERVA
    # ==================================================

    print("\n13. CANCELAR RESERVA")

    if reserva_cancelable is not None:
        resultado = ejecutar_operacion(
            "Cancelar reserva",
            reserva_cancelable.cancelar
        )

        print("Resultado:", resultado)
        print("Estado final:", reserva_cancelable.estado)

    # ==================================================
    # 14. INTENTAR CONFIRMAR RESERVA CANCELADA
    # ==================================================

    print("\n14. INTENTAR CONFIRMAR RESERVA CANCELADA")

    if reserva_cancelable is not None:
        resultado = ejecutar_operacion(
            "Intentar confirmar reserva cancelada",
            reserva_cancelable.confirmar
        )

        print("Resultado:", resultado)

    # ==================================================
    # FINALIZACION
    # ==================================================

    print("\n" + "=" * 55)
    print(" FIN DEL SISTEMA SOFTWARE FJ")
    print("=" * 55)


# PUNTO DE ENTRADA DEL PROGRAMA

if __name__ == "__main__":
    main()
