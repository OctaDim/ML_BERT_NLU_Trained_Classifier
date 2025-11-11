from copy import copy
from typing import Any, Callable, List, Tuple

from sqladmin.filters import (
    BooleanFilter, StaticValuesFilter, ForeignKeyFilter)
from sqlalchemy import Select
from starlette.requests import Request

from configs.labels_messages import LABELS


class CustomBooleanFilter(BooleanFilter):
    async def lookups(self, request: Request, model: Any,
                      run_query: Callable[[Select], Any]
                      ) -> List[Tuple[str, str]]:
        custom_list = [("all", LABELS.ALL_RECS),
                       ("true", LABELS.ALLOWED_RECS),
                       ("false", LABELS.NOT_ALLOWED_RECS)]
        return custom_list


class CustomStaticValuesFilter(StaticValuesFilter):
    async def lookups(self, request: Request, model: Any,
                      run_query: Callable[[Select], Any]
                      ) -> List[Tuple[str, str]]:
        return [("", LABELS.ALL_RECS)] + self.values


class CustomForeignKeyFilter(ForeignKeyFilter):
    async def lookups(self, request: Request, model: Any,
                      run_query: Callable[[Select], Any]
                      ) -> List[Tuple[str, str]]:
        parent_lookup = await super().lookups(request, model, run_query)
        override_lookup = copy(parent_lookup)
        override_lookup[0] = ("", LABELS.ALL_RECS)
        return override_lookup
