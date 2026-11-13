"""Capa de servicios que centraliza las operaciones de la tienda online."""

from typing import Dict, List, Optional

from models.Pedido import Pedido
from models.Producto import Producto, ProductoElectronico, ProductoRopa
from models.Usuario import Administrador, Cliente, Usuario


class TiendaService:
    """Actúa como intermediario entre los usuarios y los productos de la tienda."""

    def __init__(self) -> None:
        """Inicializa los usuarios, productos y pedidos de la tienda."""
        self.usuarios: Dict[str, Usuario] = {}
        self.productos: Dict[str, Producto] = {}
        self.pedidos: List[Pedido] = []

    def registrar_usuario(
        self, tipo: str, nombre: str, email: str, direccion: str = ""
    ) -> Usuario:
        """Registra un nuevo usuario de tipo 'cliente' o 'administrador'."""
        for existente in self.usuarios.values():
            if existente.email == email:
                raise ValueError("Ya existe un usuario con ese email.")
        if tipo == "cliente":
            usuario = Cliente(nombre, email, direccion)
        elif tipo == "administrador":
            usuario = Administrador(nombre, email)
        else:
            raise ValueError("Tipo de usuario no válido.")
        self.usuarios[usuario.id] = usuario
        return usuario

    def obtener_usuario(self, usuario_id: str) -> Optional[Usuario]:
        """Devuelve el usuario con ese id, o None si no existe."""
        return self.usuarios.get(usuario_id)

    def listar_usuarios(self) -> List[Usuario]:
        """Devuelve todos los usuarios registrados."""
        return list(self.usuarios.values())

    def anadir_producto(
        self,
        categoria: str,
        nombre: str,
        precio: float,
        stock: int,
        meses_garantia: int = 0,
        talla: str = "",
        color: str = "",
    ) -> Producto:
        """Añade al inventario un producto de la categoría indicada."""
        if categoria == "electronico":
            producto = ProductoElectronico(nombre, precio, stock, meses_garantia)
        elif categoria == "ropa":
            producto = ProductoRopa(nombre, precio, stock, talla, color)
        else:
            producto = Producto(nombre, precio, stock)
        self.productos[producto.id] = producto
        return producto

    def eliminar_producto(self, producto_id: str) -> bool:
        """Elimina un producto del inventario a partir de su id."""
        if producto_id in self.productos:
            del self.productos[producto_id]
            return True
        return False

    def listar_productos(self) -> List[Producto]:
        """Devuelve todos los productos de la tienda."""
        return list(self.productos.values())

    def obtener_producto(self, producto_id: str) -> Optional[Producto]:
        """Devuelve el producto con ese id, o None si no existe."""
        return self.productos.get(producto_id)

    def realizar_pedido(
        self, usuario_id: str, productos_solicitados: Dict[str, int]
    ) -> Pedido:
        """Crea un pedido si el cliente existe y hay stock de todos los productos."""
        # 1. Comprobar que el usuario existe y que es un cliente
        if usuario_id not in self.usuarios:
            raise ValueError("El usuario no existe.")
        usuario = self.usuarios[usuario_id]
        if not isinstance(usuario, Cliente):
            raise ValueError("Solo los clientes pueden hacer pedidos.")

        # 2. Comprobar que los productos existen y que hay stock de todos
        productos_pedido = {}
        for producto_id, cantidad in productos_solicitados.items():
            if producto_id not in self.productos:
                raise ValueError("Uno de los productos no existe.")
            producto = self.productos[producto_id]
            if not producto.hay_stock(cantidad):
                raise ValueError(f"No hay stock suficiente de {producto.nombre}.")
            productos_pedido[producto] = cantidad

        # 3. Descontar el stock de cada producto
        for producto, cantidad in productos_pedido.items():
            producto.actualizar_stock(-cantidad)

        # 4. Crear el pedido, guardarlo y devolverlo
        pedido = Pedido(usuario, productos_pedido)
        self.pedidos.append(pedido)
        return pedido

    def listar_pedidos_usuario(self, usuario_id: str) -> List[Pedido]:
        """Devuelve los pedidos de un usuario ordenados por fecha."""
        pedidos_usuario = []
        for pedido in self.pedidos:
            if pedido.cliente.id == usuario_id:
                pedidos_usuario.append(pedido)
        return sorted(pedidos_usuario, key=lambda pedido: pedido.fecha)
