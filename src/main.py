"""Punto de entrada de la API REST de la tienda online (capa de exposición).

Ejecutar desde la carpeta Tienda_online con:
    uvicorn main:app --reload
y abrir http://localhost:8000/docs para probar los endpoints.
"""

from typing import Dict, List

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from models.Pedido import Pedido
from models.Producto import Producto, ProductoElectronico, ProductoRopa
from models.Usuario import Cliente, Usuario
from schemas.Pedido import PedidoCreate, PedidoItemRead, PedidoRead
from schemas.Producto import ProductoCreate, ProductoRead
from schemas.Usuario import UsuarioCreate, UsuarioRead
from Services.Tienda_service import TiendaService

app = FastAPI(title="Tienda online API")
NO_ENCONTRADO = {404: {"description": "Not Found: recurso no encontrado"}}
tienda = TiendaService()


@app.exception_handler(RequestValidationError)
async def datos_invalidos(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Devuelve 400 Bad Request cuando los datos recibidos no son válidos."""
    errores = [
        {"campo": ".".join(str(p) for p in e["loc"]), "mensaje": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": errores}
    )


def openapi_con_400() -> dict:
    """Documenta en /docs los errores de validación como 400 en lugar de 422."""
    if app.openapi_schema:
        return app.openapi_schema
    esquema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    for ruta in esquema["paths"].values():
        for operacion in ruta.values():
            respuestas = operacion.get("responses", {})
            if "422" in respuestas:
                respuestas["400"] = respuestas.pop("422")
                respuestas["400"]["description"] = "Bad Request: datos inválidos"
    app.openapi_schema = esquema
    return esquema


app.openapi = openapi_con_400


# ---------------------------------------------------------------------------
# Conversión de objetos del dominio a esquemas de respuesta
# ---------------------------------------------------------------------------

def usuario_a_read(usuario: Usuario) -> UsuarioRead:
    """Convierte un Usuario del dominio en un UsuarioRead."""
    return UsuarioRead(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        es_admin=usuario.is_admin(),
    )


def producto_a_read(producto: Producto) -> ProductoRead:
    """Convierte un Producto del dominio en un ProductoRead según su tipo."""
    if isinstance(producto, ProductoElectronico):
        return ProductoRead(
            id=producto.id, tipo="electronico", nombre=producto.nombre,
            precio=producto.precio, stock=producto.stock,
            meses_garantia=producto.meses_garantia,
        )
    if isinstance(producto, ProductoRopa):
        return ProductoRead(
            id=producto.id, tipo="ropa", nombre=producto.nombre,
            precio=producto.precio, stock=producto.stock,
            talla=producto.talla, color=producto.color,
        )
    return ProductoRead(
        id=producto.id, tipo="generico", nombre=producto.nombre,
        precio=producto.precio, stock=producto.stock,
    )


def pedido_a_read(pedido: Pedido) -> PedidoRead:
    """Convierte un Pedido del dominio en un PedidoRead con sus líneas."""
    items = [
        PedidoItemRead(
            producto_id=producto.id,
            nombre=producto.nombre,
            precio_unitario=producto.precio,
            cantidad=cantidad,
            subtotal=producto.precio * cantidad,
        )
        for producto, cantidad in pedido.productos.items()
    ]
    return PedidoRead(
        id=pedido.id,
        fecha=pedido.fecha,
        cliente_id=pedido.cliente.id,
        cliente_nombre=pedido.cliente.nombre,
        total=pedido.calcular_total(),
        items=items,
    )


# ---------------------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------------------

@app.post("/usuarios", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCreate) -> UsuarioRead:
    """Crea un nuevo usuario (cliente o administrador)."""
    try:
        usuario = tienda.registrar_usuario(
            datos.tipo, datos.nombre, datos.email, datos.direccion_postal or ""
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return usuario_a_read(usuario)


@app.get("/usuarios", response_model=List[UsuarioRead])
def listar_usuarios() -> List[UsuarioRead]:
    """Devuelve la lista de usuarios registrados."""
    return [usuario_a_read(u) for u in tienda.listar_usuarios()]


@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead, responses=NO_ENCONTRADO)
def obtener_usuario(usuario_id: str) -> UsuarioRead:
    """Devuelve un usuario concreto a partir de su id."""
    usuario = tienda.obtener_usuario(usuario_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return usuario_a_read(usuario)


@app.get("/usuarios/{cliente_id}/pedidos", response_model=List[PedidoRead], responses=NO_ENCONTRADO)
def listar_pedidos_cliente(cliente_id: str) -> List[PedidoRead]:
    """Devuelve los pedidos de un cliente ordenados por fecha."""
    if tienda.obtener_usuario(cliente_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return [pedido_a_read(p) for p in tienda.listar_pedidos_usuario(cliente_id)]


# ---------------------------------------------------------------------------
# Productos
# ---------------------------------------------------------------------------

@app.post("/productos", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCreate) -> ProductoRead:
    """Añade al inventario un producto genérico, electrónico o de ropa."""
    producto = tienda.anadir_producto(
        datos.tipo,
        datos.nombre,
        datos.precio,
        datos.stock,
        meses_garantia=datos.meses_garantia or 0,
        talla=datos.talla or "",
        color=datos.color or "",
    )
    return producto_a_read(producto)


@app.get("/productos", response_model=List[ProductoRead])
def listar_productos() -> List[ProductoRead]:
    """Devuelve todos los productos de la tienda."""
    return [producto_a_read(p) for p in tienda.listar_productos()]


@app.get("/productos/{producto_id}", response_model=ProductoRead, responses=NO_ENCONTRADO)
def obtener_producto(producto_id: str) -> ProductoRead:
    """Devuelve un producto concreto a partir de su id."""
    producto = tienda.obtener_producto(producto_id)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado.")
    return producto_a_read(producto)


@app.delete("/productos/{producto_id}", responses=NO_ENCONTRADO)
def eliminar_producto(producto_id: str) -> Dict[str, str]:
    """Elimina un producto del inventario a partir de su id."""
    if not tienda.eliminar_producto(producto_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado.")
    return {"detail": "Producto eliminado."}


# ---------------------------------------------------------------------------
# Pedidos
# ---------------------------------------------------------------------------

@app.post("/pedidos", response_model=PedidoRead, status_code=status.HTTP_201_CREATED, responses=NO_ENCONTRADO)
def crear_pedido(datos: PedidoCreate) -> PedidoRead:
    """Crea un pedido comprobando cliente, productos y stock."""
    # 1. El cliente debe existir (404) y ser de tipo cliente (400)
    usuario = tienda.obtener_usuario(datos.cliente_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado.")
    if not isinstance(usuario, Cliente):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Solo los clientes pueden hacer pedidos."
        )

    # 2. Cada producto debe existir (404); se suman las líneas repetidas
    productos_solicitados: Dict[str, int] = {}
    for item in datos.items:
        if tienda.obtener_producto(item.producto_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto {item.producto_id} no encontrado.",
            )
        productos_solicitados[item.producto_id] = (
            productos_solicitados.get(item.producto_id, 0) + item.cantidad
        )

    # 3. TiendaService comprueba el stock, lo descuenta y crea el pedido (400 si falta stock)
    try:
        pedido = tienda.realizar_pedido(datos.cliente_id, productos_solicitados)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return pedido_a_read(pedido)
