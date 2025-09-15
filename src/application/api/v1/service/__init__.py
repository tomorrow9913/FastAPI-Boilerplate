# -*- coding: utf-8 -*-
# src/application/api/v1/service/__init__.py
# Auto load service modules and collect routers
import importlib
import os
import pathlib
import sys

from src.core.logger import LogManager

logger = LogManager.get_logger("app")

routers = []

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

# 파일 경로를 파이썬 임포트 경로로 변환합
import_prefix = ".".join(relative_path.parts)

for folder_name in os.listdir(current_dir):
    sub_path = current_dir / folder_name
    if sub_path.is_dir() and not folder_name.startswith("__"):
        route_file_name = f"{folder_name}_route.py"
        route_file = sub_path / route_file_name

        if route_file.is_file():
            # 동적으로 생성된 임포트 경로를 사용합니다.
            module_name = (
                f"{import_prefix}.{folder_name}.{route_file_name.replace('.py', '')}"
            )
            module = importlib.import_module(module_name)

            if hasattr(module, "router") and not getattr(
                module, "__EXCLUDING_ROUTE__", False
            ):
                logger.info(
                    f"Loading router from {import_prefix.split('.')[-2]}:{folder_name}"
                )
                routers.append(module.router)

__all__ = ["routers"]
