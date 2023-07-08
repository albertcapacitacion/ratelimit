creditos_disponibles={}

def limitar_porcreditos(ip_cliente, creditos_endpoint): 
    try:
        req=creditos_disponibles[ip_cliente]
        
        if req==0:
            return {            
                "call": False,            
                "creditos": req   
                }   
        else:    
            creditos_disponibles[ip_cliente]=creditos_disponibles[ip_cliente]-1
            return {            
                "call": True,            
                "creditos": creditos_disponibles       
                }
   
    except KeyError:
        creditos_disponibles[ip_cliente]=creditos_endpoint
        return {            
            "call": True,            
            "creditos": creditos_endpoint       
            }    