import os
import uvicorn

if __name__ == "__main__":
    host = os.environ.get("SERVER_HOST", "0.0.0.0")
    port = int(os.environ.get("SERVER_PORT", 8000))
    uvicorn.run("src.app_module:http_server", host=host, port=port, reload=True)
