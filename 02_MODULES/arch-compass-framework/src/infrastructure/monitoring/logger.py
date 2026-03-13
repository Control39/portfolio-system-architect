import structlog

logger = structlog.get_logger()

def setup_logging(app):
    # TODO: настроить структурированное логирование
    pass

# Пример использования в коде
async def update_marker(marker_id: str, status: str):
    logger.info("marker_update_started", marker_id=marker_id, new_status=status)
    try:
        # логика обновления
        logger.info("marker_update_success", marker_id=marker_id)
    except Exception as e:
        logger.error("marker_update_failed", marker_id=marker_id, error=str(e))
        raise