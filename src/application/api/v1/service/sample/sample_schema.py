# -*- coding: utf-8 -*-
# File: src/application/api/v1/service/sample/sample_schema.py
from typing import Optional

from pydantic import BaseModel


class Sample(BaseModel):
    id: Optional[int]
    name: str
    description: Optional[str] = None


class SampleCreate(BaseModel):
    name: str
    description: Optional[str] = None
