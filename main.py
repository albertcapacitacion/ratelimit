from fastapi import FastAPI,Request,Response,HTTPException,status
from fastapi import Depends
from slowapi import Limiter,_rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import PlainTextResponse,HTMLResponse

from super_almacenamiento import limitar_porcreditos
from redis_ratelimit import limitar_con_redis


import redis

#setup limiter via slowapi
limiter = Limiter(key_func=get_remote_address)

#Conectar con server Redis
def get_redis():
    # Verificar que esta corriendo localmente en consola
    redis_conn = redis.Redis(host='localhost', port=6379, db=0)

    try:
        yield redis_conn
    finally:
        redis_conn.close()

#crear cliente redis
cliente_redis = redis.Redis(host="redis-server")

#crear API
app = FastAPI()

#namespace interno de la API disponible para todas las rutas
app.state.limiter = limiter

#control de errores granular creando exceptions exclusivas de esta API
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

#cada endpoint llevara un decorator adicional que implementa el limite
#asi podemos tener un control de limite granular
#el limite va DESPUES del decorator que controla la 

#5 requests por minuto,respuesta en formato texto
@app.get("/")
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

#rate limit por cantidad de creditos
@app.get("/vosno")
def ratelimit_ip(request: Request):
    #envia IP del dispositivo, maximos creditos para este endpoint
    tengo_creditos=limitar_porcreditos(get_remote_address,2)
    if tengo_creditos['call']==True:
        return PlainTextResponse("Bienvenidos!")
    else:
        return PlainTextResponse("Sin creditos disponibles")     

#rate limiting con Redis como cache
#repasar Dependencias en clase
@app.get("/redis")
def test(request: Request, redis=Depends(get_redis)):    
  clientIp = request.client.host    
  res = limitar_con_redis(redis,clientIp, 2)    
  if res["call"]:        
    return {            
        "message": "Bienvenido",            
        "ttl": res["ttl"]        
        }    
  else:       
     raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,      
        detail={       
           "message": "Limite alcanzado",      
           "ttl": res["ttl"]    
           }
        )