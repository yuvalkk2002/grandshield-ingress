from app.core.logger import configure_logging
from app.core.setup import create_application

# 1. Configure Logging
configure_logging()

# 2. Setup Application
app = create_application()
