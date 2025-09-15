# -*- coding: utf-8 -*-
# File: src/application/api/v1/service/workspace/workspace_service.py


from sqlalchemy.orm import Session

from src.application.api.v1.service.sample import sample_schema
from src.core.logger import LogManager

logger = LogManager.get_logger("app")


def create_sample(
    db: Session, sample: sample_schema.sampleCreate
) -> sample_schema.sample:
    return sample_schema.sample(
        id=1, name=sample.name, description=sample.description
    )
