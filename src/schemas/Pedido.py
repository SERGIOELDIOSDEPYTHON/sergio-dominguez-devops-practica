"""Esquemas Pydantic de pedido para la API REST."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class PedidoItemCreate(BaseModel):
    """Una línea del pedido: producto y cantidad solicitada."""

    producto_id: str
    cantidad: int = Field(gt=0)


class PedidoCreate(BaseModel):
    """Datos que envía el cliente para crear un pedido."""

    cliente_id: str
    items: List[PedidoItemCreate] = Field(min_length=1)


class PedidoItemRead(BaseModel):
    """Una línea del pedido tal como la devuelve la API."""

    producto_id: str
    nombre: str
    precio_unitario: float
    cantidad: int
    subtotal: float


class PedidoRead(BaseModel):
    """Pedido completo devuelto por la API."""

    id: str
    fecha: datetime
    cliente_id: str
    cliente_nombre: str
    total: float
    items: List[PedidoItemRead]
