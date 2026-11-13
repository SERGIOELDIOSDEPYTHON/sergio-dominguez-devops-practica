"""Esquemas Pydantic de usuario para la API REST."""

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class UsuarioCreate(BaseModel):
    """Datos que envía el cliente para crear un usuario."""

    nombre: str = Field(min_length=1)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    tipo: Literal["cliente", "administrador"]
    direccion_postal: Optional[str] = None

    @model_validator(mode="after")
    def comprobar_direccion(self) -> "UsuarioCreate":
        """Un cliente debe indicar obligatoriamente su dirección postal."""
        if self.tipo == "cliente" and not self.direccion_postal:
            raise ValueError("Un cliente debe tener dirección postal.")
        return self


class UsuarioRead(BaseModel):
    """Datos de un usuario que la API devuelve al cliente."""

    id: str
    nombre: str
    email: str
    es_admin: bool
