import structlog

logger = structlog.get_logger()

def setup_logging(app):
    \"\"\"Configure structured logging with structlog.\"\"\"
    import structlog
    from structlog.stdlib import LoggerFactory
    from structlog.processors import TimeStamper, JSONRenderer

    timestamper = TimeStamper(fmt="iso")
    processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
        structlog.processors.format_exc_info,
        JSONRenderer()
    ]

    structlog.configure(
        processors=processors,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Bind app context
    logger = structlog.get_logger("arch-compass")
    logger.info("structured_logging_configured", app_name=app.__class__.__name__ if app else "unknown")

# Example usage (unchanged, now functional)
async def update_marker(marker_id: str, status: str):
    logger.info("marker_update_started", marker_id=marker_id, new_status=status)
    try:
        # TODO: логика обновления
        logger.info("marker_update_success", marker_id=marker_id)
    except Exception as e:
        logger.error("marker_update_failed", marker_id=marker_id, error=str(e))
        raise
