from fastapi import FastAPI,Request,Response
from slowapi import Limiter,_rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import PlainTextResponse,HTMLResponse

from .super_almacenamiento import limitar_porcreditos

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

#namespace interno de la API disponible para todas las rutas
app.state.limiter = limiter

#control de errores granular creando exceptions exclusivas de esta API
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

#cada endpoint llevara un decorator adicional que implementa el limite
#asi podemos tener un control de limite granular
#el limite va DESPUES del decorator que controla la 

#5 requests por minuto,respuesta en formato texto
@app.get("/home")
@limiter.limit("5/minute")
async def home(request: Request):
    return PlainTextResponse("Este es el home de la API")

#rate limit bajo y respuesta en formato HTML
@app.get("/ceropaciencia")
@limiter.limit("1/minute")
def ratelimit_general(request: Request, response: Response):
   respuesta_html="""
            <!DOCTYPE html>
    <html>
    <head>
      <title>Page Title</title>
      <style>
        .center-text {
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
          font-weight: bold;
          font-size: 2em;
        }
      </style>
    </head>
    <body>
      <div class="center-text">
        Request Exitoso
      </div>
    </body>
    </html>
    """
   return HTMLResponse(content=respuesta_html, status_code=200)

#por ip
@app.get("/vosno")
def ratelimit_ip(request: Request):
    return PlainTextResponse("Este es el home de la API")

