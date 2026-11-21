
from entidades import Cliente, Salas
from reserva import Reserva
from infraestructura import OperacionNoPermitidaError

print("====================================")
print(" PRUEBAS DEL SISTEMA DE RESERVAS")
print("====================================")

# Crear un cliente
cliente = Cliente(
    "1085234567",
    "Juan Perez",
    "juan@gmail.com",
    "3105551234"
)

# Crear un servicio
servicio = Salas(
    "Sala de reuniones",
    50000,
    20
)

# Crear una reserva
reserva = Reserva(cliente, servicio, 2)

print("\n1. RESERVA CREADA")
print(reserva.describir())

# Confirmar la reserva
print("\n2. CONFIRMAR RESERVA")
print(reserva.confirmar())
print("Estado:", reserva.estado)

# Procesar la reserva
print("\n3. PROCESAR RESERVA")
costo = reserva.procesar()
print("Costo total: $", costo)
print("Estado:", reserva.estado)

# Mostrar descripción final
print("\n4. DESCRIPCION FINAL")
print(reserva.describir())

print("\n====================================")
print(" FIN DE LAS PRUEBAS")
print("====================================")
# 5. PRUEBA DE CANCELACION
print("\n5. PRUEBA DE CANCELACION")

reserva_cancelada = Reserva(cliente, servicio, 1)

print("Estado inicial:", reserva_cancelada.estado)
print(reserva_cancelada.cancelar())
print("Estado final:", reserva_cancelada.estado)


# 6. PRUEBA DE OPERACION NO PERMITIDA
print("\n6. PRUEBA DE OPERACION NO PERMITIDA")

try:
    reserva_cancelada.confirmar()
except OperacionNoPermitidaError as error:
    print("Error controlado:", error)

print("\nFIN DE LAS PRUEBAS ADICIONALES")