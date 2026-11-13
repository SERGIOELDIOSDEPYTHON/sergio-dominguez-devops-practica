"""Modelo de pedido de la tienda online."""

import uuid
from datetime import datetime
from typing import Dict

from models.Producto import Producto
from models.Usuario import Cliente


class Pedido:
    """Representa un pedido realizado por un cliente sobre uno o más productos."""

    def __init__(self, cliente: Cliente, productos: Dict[Producto, int]) -> None:
        """Crea un pedido con fecha e identificador generados automáticamente."""
        self.id: str = str(uuid.uuid4())
        self.cliente: Cliente = cliente
        self.productos: Dict[Producto, int] = productos
        self.fecha: datetime = datetime.now()

    def calcular_total(self) -> float:
        """Calcula el importe total del pedido en función de precios y cantidades."""
        total = 0.0
        for producto, cantidad in self.productos.items():
            total += producto.precio * cantidad
        return total

    def __str__(self) -> str:
        """Devuelve un resumen legible del pedido, con cliente y total."""
        detalle = ""
        for producto, cantidad in self.productos.items():
            subtotal = producto.precio * cantidad
            detalle += f"    - {producto.nombre} x{cantidad} = {subtotal:.2f}€\n"
        return (
            f"Pedido [{self.id[:8]}] - Cliente: {self.cliente.nombre} "
            f"({self.fecha.strftime('%Y-%m-%d %H:%M:%S')})\n"
            f"{detalle}"
            f"    TOTAL: {self.calcular_total():.2f}€"
        )
