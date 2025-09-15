# -*- coding: utf-8 -*-
# src/core/logger.py
import logging
import sys
from logging import LogRecord
from pathlib import Path
from types import FrameType
from typing import Optional, Set

import apprise
from loguru import logger

from src.core.config import config


class InterceptHandler(logging.Handler):
    """
    표준 `logging` 모듈의 로그를 가로채 `loguru`로 전달하는 핸들러입니다.
    """

    def emit(self, record: LogRecord) -> None:
        """
        로그 레코드를 받아 loguru 로거로 전달합니다.
        """
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame: Optional[FrameType] = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # 표준 로깅 레코드의 `name`을 가져와 loguru의 `extra` 데이터로 사용합니다.
        # get_logger()를 통해 생성된 로그는 bind된 name으로 덮어쓰여집니다.
        logger_with_name = logger.bind(name=record.name)
        logger_with_name.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class _LogManager:
    """
    애플리케이션의 로깅 시스템을 관리하는 싱글턴 클래스.
    """

    def __init__(self):
        self._configured_loggers: Set[str] = set()
        self.log_dir = Path(config.APP_CONFIG.LOG_DIR)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        logger.remove()
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

        logger.patch(lambda record: record["extra"].setdefault("name", "unnamed"))

        # 기본 콘솔 로거 추가
        logger.add(
            sys.stdout,
            level=config.APP_CONFIG.LOG_LEVEL.upper(),
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{extra[name]:<15}</cyan> | "
                "<cyan>{name}</cyan>:<cyan>{function}:{line}</cyan> - <level>{message}</level>"
            ),
            colorize=True,
        )

        # Apprise 알림 로거 추가 (ERROR 레벨)
        if config.APP_CONFIG.LOG_NOTIFIER_URL:
            notifier = apprise.Apprise()
            notifier.add(config.APP_CONFIG.LOG_NOTIFIER_URL)
            logger.add(
                lambda msg: notifier.notify(body=msg),
                level="ERROR",
                filter=lambda record: not record["extra"].get("no_notify", False),
                format="[{extra[name]}] {message}",
            )

    def get_logger(self, name: str, no_notify: bool = False) -> logger:
        """
        지정된 이름으로 로거를 가져오거나 생성합니다.
        """
        if name not in self._configured_loggers:
            log_file_path = self.log_dir / f"{name}.log"
            logger.add(
                log_file_path,
                level=config.APP_CONFIG.LOG_LEVEL.upper(),
                filter=lambda record: record["extra"].get("name") == name,
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
                rotation=f"{config.APP_CONFIG.LOG_MAX_BYTES} B",
                retention=f"{config.APP_CONFIG.LOG_BACKUP_COUNT} days",
                compression="zip",
                encoding="utf-8",
                enqueue=True,
                backtrace=config.ENV != "prod",
                diagnose=config.ENV != "prod",
            )
            self._configured_loggers.add(name)

        return logger.bind(name=name, no_notify=no_notify)


# 클래스의 인스턴스를 생성하여 싱글턴으로 사용
LogManager = _LogManager()
