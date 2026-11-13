# Tienda online: API REST contenerizada

Autor: Sergio Domínguez (Arquitectura del Software, UIE)

Esta es la tienda online que llevo haciendo en las prácticas de la asignatura. Empezó en la práctica 1.3 con las clases `Producto`, `Usuario` y `Pedido` y el `TiendaService`, y en la práctica 2 la convertí en una API REST con FastAPI. En las prácticas 3.1 y 3.2 la he subido a GitHub y la he metido en un contenedor de Docker.

El código de la API está en `src/`. En la raíz están el `requirements.txt` con las versiones fijadas, el `dockerfile` y el `.dockerignore`.

## Sin Docker

Si tienes Python, basta con instalar las dependencias y arrancar uvicorn desde `src`:

```bash
pip install -r requirements.txt
cd src
uvicorn main:app --reload
```

## Con Docker

### Construir la imagen

Desde la carpeta del repo:

```bash
docker build -t tienda-online:1.0 .
```

El `-t` le pone nombre y versión a la imagen, y el punto del final le dice a Docker que use la carpeta actual como contexto, que es donde está el `dockerfile`. En mi Mac la primera vez tardó unos 20 segundos, porque tiene que descargar `python:3.12-slim`.

### Arrancar el contenedor

```bash
docker run --rm -p 8000:8000 tienda-online:1.0
```

El `-p 8000:8000` conecta el puerto 8000 del contenedor con el del ordenador, y con `--rm` el contenedor se borra solo cuando lo paras con Ctrl+C. También se puede dejar en segundo plano; en ese caso `docker stop` solo lo detiene, y hasta que no lo borras con `docker rm` el nombre `tienda` sigue ocupado:

```bash
docker run -d --name tienda -p 8000:8000 tienda-online:1.0
docker logs tienda
docker stop tienda
docker rm tienda
```

Si ya tienes algo usando el puerto 8000, cambia el primer número (por ejemplo `-p 8080:8000`) y entra por http://localhost:8080/docs.

### Variables de entorno

No hace falta configurar ninguna. La app no usa base de datos ni claves y lo guarda todo en memoria, así que al parar el contenedor los datos se pierden.

### Cómo comprobar que funciona

Al arrancar, la terminal tiene que mostrar esto:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Después abre http://localhost:8000/docs y prueba los endpoints con "Try it out". Yo hice estas pruebas, en este orden:

1. Crear un cliente con `POST /usuarios` y `{"tipo": "cliente", "nombre": "Ana", "email": "ana@mail.com", "direccion_postal": "Calle Mayor 1"}`. Devuelve 201.
2. Crear un producto con `POST /productos` y `{"tipo": "electronico", "nombre": "Portátil", "precio": 800, "stock": 5, "meses_garantia": 24}`. También 201.
3. Hacer un pedido con `POST /pedidos` usando el id de Ana, el del portátil y cantidad 2. Devuelve 201 con un total de 1600.
4. Mirar `GET /productos`: devuelve 200, y el stock del portátil ha bajado de 5 a 3.
5. Pedir un usuario que no existe con `GET /usuarios/no-existe`: devuelve 404.

## Docker Hub

La imagen está publicada en https://hub.docker.com/r/sergiodomiinguez/tienda-online. La subí así:

```bash
docker tag tienda-online:1.0 sergiodomiinguez/tienda-online:1.0
docker login
docker push sergiodomiinguez/tienda-online:1.0
```

Para usarla en otro ordenador no hace falta clonar el repo:

```bash
docker pull sergiodomiinguez/tienda-online:1.0
docker run --rm -p 8000:8000 sergiodomiinguez/tienda-online:1.0
```
