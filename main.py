import uvicorn
from logger_settings import Logging_Uvicorn

if __name__ == "__main__":
    Logging_Uvicorn()
    uvicorn.run("app:create_app",
                host="0.0.0.0",
                port=8000,
                factory=True,
                log_config=None)