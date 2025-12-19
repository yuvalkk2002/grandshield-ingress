import logging
import os
import sys

import structlog


def configure_logging():
    """
    Configure structured logging for the application.
    Uses generic JSON renderer for production-ready logs.
    """
    
    # Define shared processors for both structlog and standard logging
    # Shared processors for both structlog and standard logging
    # These effectively parse/enrich the log record
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Processors specific to structlog (not for stdlib redirection)
    structlog_processors = [
        structlog.stdlib.filter_by_level,
    ] + shared_processors + [
        # Prepare event dict for stdlib logging
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    # Decide on the renderer
    renderer = (
        structlog.dev.ConsoleRenderer() 
        if os.getenv("ENV") == "local" 
        else structlog.processors.JSONRenderer()
    )

    structlog.configure(
        processors=structlog_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging to use structlog's formatting
    formatter = structlog.stdlib.ProcessorFormatter(
        # Processors to run on foreign (stdlib) logs to add structure
        foreign_pre_chain=shared_processors,
        # Processors to run on ALL logs to render final output
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

logger = structlog.get_logger()
