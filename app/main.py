from app.config import settings
from app.core.logger import configure_logging
from app.core.setup import create_application

# 1. Configure Logging
configure_logging()

# 2. Setup Application
app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)