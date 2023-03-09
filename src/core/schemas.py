# coding:utf-8
import math
from typing import Generic, List, Tuple, TypeVar, Optional, Union

from pydantic import BaseModel
from pydantic.generics import GenericModel
from pydantic.types import conint

DataType = TypeVar('DataType')
BaseSchemaType = TypeVar("BaseSchemaType", bound=BaseModel)


class Pagination(BaseModel):
    page: Optional[conint(gt=0, le=500)] = 1
    paginate_by: Optional[conint(gt=0, le=500, multiple_of=5)] = 20

    def offset_limit(self) -> Tuple[Union[int, None], Union[int, None]]:
        if self.paginate_by and self.page:
            return (self.page - 1) * self.paginate_by, self.paginate_by
        return None, None

    @property
    def offset(self) -> int:
        if self.paginate_by and self.page:
            return (self.page - 1) * self.paginate_by
        return 0

    @property
    def limit(self) -> int:
        if self.paginate_by:
            return self.paginate_by
        return 20

    def paginate(self, total: int) -> 'Paginate':
        return Paginate(page=self.page, paginate_by=self.paginate_by, total=total,
                        total_page=math.ceil(total / self.paginate_by))


class Paginate(BaseModel):
    page: int
    paginate_by: int
    total: int

    @property
    def total_page(self):
        return math.ceil(self.total / self.paginate_by)


class Page(GenericModel, Generic[DataType]):
    paginate: Paginate
    content: List[DataType]

    class Config:
        arbitrary_types_allowed = True


class Response(GenericModel, Generic[DataType]):
    code: Optional[str] = "0"
    message: Optional[str] = "success"
    data: Optional[DataType] = None

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def ok(cls, data):
        return Response(data=data)

    @classmethod
    def error(cls, code: str = "-1", message="error", data=None):
        return Response(code=code, message=message, data=data)
