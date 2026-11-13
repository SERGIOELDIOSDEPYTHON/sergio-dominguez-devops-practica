"""Modelo de usuario de la tienda online y sus subclases especializadas."""

import uuid


class Usuario:
    """Clase padre que representa a cualquier persona que usa la tienda."""

    def __init__(self, nombre: str, email: str) -> None:
        """Crea un usuario generando automáticamente su identificador único."""
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.email: str = email

    def is_admin(self) -> bool:
        """Indica si el usuario tiene permisos de administrador."""
        return False

    def __str__(self) -> str:
        """Devuelve una descripción legible del usuario."""
        return f"[{self.id[:8]}] {self.nombre} ({self.email})"


class Cliente(Usuario):
    """Usuario cliente, con dirección postal para poder recibir pedidos."""

    def __init__(self, nombre: str, email: str, direccion: str) -> None:
        """Crea un cliente con su dirección postal."""
        super().__init__(nombre, email)
        self.direccion: str = direccion

    def __str__(self) -> str:
        """Añade la dirección postal a la descripción base."""
        return f"{super().__str__()} | Dirección: {self.direccion}"


class Administrador(Usuario):
    """Usuario administrador o gestor de la tienda."""

    def is_admin(self) -> bool:
        """Un administrador siempre tiene permisos de administrador."""
        return True
