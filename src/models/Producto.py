"""Modelo de producto de la tienda online y sus subclases especializadas."""

import uuid


class Producto:
    """Clase padre que representa un producto genérico de la tienda."""

    def __init__(self, nombre: str, precio: float, stock: int) -> None:
        """Crea un producto generando automáticamente su identificador único."""
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.precio: float = precio
        self.stock: int = stock

    def hay_stock(self, cantidad: int) -> bool:
        """Comprueba si hay stock suficiente para la cantidad solicitada."""
        return self.stock >= cantidad

    def actualizar_stock(self, cantidad: int) -> None:
        """Suma unidades al stock (reposición) o las resta si es negativo (compra)."""
        self.stock += cantidad

    def __str__(self) -> str:
        """Devuelve una descripción legible del producto."""
        return (
            f"[{self.id[:8]}] {self.nombre} - {self.precio:.2f}€ "
            f"(Stock: {self.stock})"
        )


class ProductoElectronico(Producto):
    """Producto electrónico, con meses de garantía adicionales."""

    def __init__(
        self, nombre: str, precio: float, stock: int, meses_garantia: int
    ) -> None:
        """Crea un producto electrónico con sus meses de garantía."""
        super().__init__(nombre, precio, stock)
        self.meses_garantia: int = meses_garantia

    def __str__(self) -> str:
        """Añade la información de garantía a la descripción base."""
        return f"{super().__str__()} | Garantía: {self.meses_garantia} meses"


class ProductoRopa(Producto):
    """Producto de ropa, con talla y color adicionales."""

    def __init__(
        self, nombre: str, precio: float, stock: int, talla: str, color: str
    ) -> None:
        """Crea un producto de ropa con su talla y color."""
        super().__init__(nombre, precio, stock)
        self.talla: str = talla
        self.color: str = color

    def __str__(self) -> str:
        """Añade talla y color a la descripción base."""
        return f"{super().__str__()} | Talla: {self.talla}, Color: {self.color}"
