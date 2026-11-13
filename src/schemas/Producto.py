"""Esquemas Pydantic de producto para la API REST."""

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class ProductoCreate(BaseModel):
    """Datos que envía el cliente para crear un producto de cualquier tipo."""

    tipo: Literal["generico", "electronico", "ropa"]
    nombre: str = Field(min_length=1)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)
    meses_garantia: Optional[int] = Field(default=None, ge=0)
    talla: Optional[str] = None
    color: Optional[str] = None

    @model_validator(mode="after")
    def comprobar_atributos_tipo(self) -> "ProductoCreate":
        """Comprueba que se envían los atributos propios de cada tipo."""
        if self.tipo == "electronico" and self.meses_garantia is None:
            raise ValueError("Un producto electrónico necesita meses_garantia.")
        if self.tipo == "ropa" and (not self.talla or not self.color):
            raise ValueError("Un producto de ropa necesita talla y color.")
        return self


class ProductoRead(BaseModel):
    """Datos de un producto que la API devuelve al cliente."""

    id: str
    tipo: str
    nombre: str
    precio: float
    stock: int
    meses_garantia: Optional[int] = None
    talla: Optional[str] = None
    color: Optional[str] = None
