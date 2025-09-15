# -*- coding: utf-8 -*-
# src/middleware/__init__.py
# Auto Load Middleware package

import importlib
import importlib.util
import inspect
import os
import pathlib
import sys

from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logger import LogManager

logger = LogManager.get_logger("app")

middlewares: list[type[BaseHTTPMiddleware]] = []

current_dir = pathlib.Path(__file__).parent.resolve()
project_root = current_dir
while not (project_root / "src").is_dir():
    if project_root.parent == project_root:
        raise RuntimeError("Could not determine the project root.")
    project_root = project_root.parent

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# 프로젝트 루트로부터 현재 디렉토리까지의 상대 경로를 계산.
relative_path = current_dir.relative_to(project_root)
# 파일 경로를 파이썬 임포트 경로로 변환
import_prefix = ".".join(relative_path.parts)

# 현재 디렉토리 내의 모든 .py 파일을 동적으로 import (mypy 타입 체크 통과)
for filename in os.listdir(current_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f"{import_prefix}.{filename[:-3]}"
        file_path = current_dir / filename
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            logger.warning(f"Failed to import {filename}: spec or loader is None")
            continue
        module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        try:
            spec.loader.exec_module(module)  # type: ignore[union-attr]
            # __LOAD__가 명시적으로 False가 아니면 import
            if (
                not hasattr(module, "__LOAD__")
                or getattr(module, "__LOAD__") is not False
            ):
                logger.info(f"Auto-imported middleware: {filename}")
                globals()[filename[:-3]] = module
                # BaseHTTPMiddleware를 상속받은 클래스만 middlewares에 추가
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(obj, BaseHTTPMiddleware)
                        and obj is not BaseHTTPMiddleware
                    ):
                        middlewares.append(obj)
        except Exception as e:
            logger.warning(f"Failed to import {filename}: {e}")

__all__ = ["middlewares"]
