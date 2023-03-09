# -*- coding: utf-8 -*-
from typing import Any, List

from core import schemas
from core.router import DeferredAPIRouter

router = DeferredAPIRouter()


@router.post("/test", response_model=schemas.Response[List], summary="库信息")
async def test(*, conn: dict) -> Any:
    """
    库信息

    :param conn:
    :return:
    """
    return schemas.Response(data=conn)
