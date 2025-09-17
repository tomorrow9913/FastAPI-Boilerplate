# -*- coding: utf-8 -*-
# File: src/crud/sample_crud.py
from src.crud.base_crud import BaseRepository
from src.infrastructure.database.models import Sample


class SampleRepository(BaseRepository[Sample]):
    def __init__(self):
        super().__init__(model=Sample)


sample_repository = SampleRepository()
