from fastapi import FastAPI,Request,Response
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi.responses import PlainTextResponse,HTMLResponse

from .super_almacenamiento import limitar_porip

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/home")
@limiter.limit("5/minute")
async def home(request: Request):
    return PlainTextResponse("Este es el home de la API")

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

