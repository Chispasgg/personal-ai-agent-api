'''
Created on 6 nov 2025

@author: chispas
'''

import uvicorn
from config.settings import settings

if __name__ == "__main__":
    print("INICIO")
    print("Starting server on {}:{}".format(settings.app_host, settings.app_port))
    
    uvicorn.run(
        "server.server:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "dev",
        workers=4,
        use_colors=True,
        log_level=settings.log_level.lower()
    )
    print("FIN")
