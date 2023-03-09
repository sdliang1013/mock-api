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
    page_size: Optional[conint(gt=0, le=500, multiple_of=5)] = 20

    def offset_limit(self) -> Tuple[Union[int, None], Union[int, None]]:
        if self.page_size and self.page:
            return (self.page - 1) * self.page_size, self.page_size
        return None, None

    @property
    def offset(self) -> int:
        if self.page_size and self.page:
            return (self.page - 1) * self.page_size
        return 0

    @property
    def limit(self) -> int:
        if self.page_size:
            return self.page_size
        return 20

    def paginate(self, total: int) -> 'Paginate':
        return Paginate(page=self.page, paginate_by=self.page_size, total=total,
                        total_page=math.ceil(total / self.page_size))


class Paginate(BaseModel):
    page: int
    page_size: int
    total: int

    @property
    def total_page(self):
        return math.ceil(self.total / self.page_size)


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
