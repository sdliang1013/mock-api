import json
import re
from hashlib import md5
from typing import List, Any, Callable

import redis

from core.config import settings
from security.util import aes_decrypt
from plugins.redis import enums
from plugins.redis.schemas import RedisPage, RedisPagination, KeyInfo

_REDIS_SETTINGS_ = {}
_REDIS_COUNT_LIMIT_ = 200


def get_id(conn_settings: dict) -> id:
    return md5(json.dumps(conn_settings).encode('ASCII')).hexdigest()


def add_conn_setting(conn_settings: dict) -> dict:
    """
    增加链接配置

    :param conn_settings:
    :return:
    """
    cache_settings = {**conn_settings}
    conn_id = get_id(cache_settings)
    # 密码解密
    pwd = cache_settings.get("password", None)
    if pwd:
        cache_settings.update({"password": aes_decrypt(key=settings.key, data=pwd)})
    _REDIS_SETTINGS_.update({conn_id: cache_settings})
    return cache_settings


def get_conn(conn_settings: dict) -> redis.Redis:
    """
    获取链接

    :param conn_settings:
    :return:
    """
    cache_settings = _REDIS_SETTINGS_.get(get_id(conn_settings), None)
    if not cache_settings:
        cache_settings = add_conn_setting(conn_settings)
    return redis.Redis(host=cache_settings.get('host', 'localhost'),
                       port=cache_settings.get('port', 6379),
                       password=cache_settings.get('password', None),
                       db=cache_settings.get('db', 0),
                       decode_responses=True,
                       encoding_errors='replace')


async def db_size(conn_settings: dict) -> List[str]:
    """
    key数量
    :param conn_settings:
    :return:
    """
    with get_conn(conn_settings) as conn:
        return conn.dbsize()


async def dirs(conn_settings: dict) -> List[str]:
    """
    分支节点

    :param conn_settings:
    :return:
    """
    cursor = 0
    page_size = 200
    idx = 0
    dir_list = list()
    with get_conn(conn_settings) as conn:
        while idx < settings.redis_scan_limit:
            cursor, keys = conn.scan(cursor=cursor, count=page_size)
            for key in keys:
                branch = key
                if ":" in branch:
                    branch = branch[: branch.rindex(":") + 1]
                if branch not in dir_list:
                    dir_list.append(branch)
            if cursor == 0:
                break
            idx += page_size
    # 排序
    dir_list.sort()
    return dir_list


async def scan(conn_settings: dict, pattern: str = None, pagination: RedisPagination = RedisPagination()) -> RedisPage:
    """
    key查找
    :param conn_settings:
    :param pattern:
    :param pagination:
    :return:
    """
    with get_conn(conn_settings) as conn:
        cursor, keys = _scan_(func=conn.scan, match=pattern,
                              cursor=pagination.cursor, count=pagination.page_size)
        content = list()
        for key in keys:
            k_type = conn.type(key)
            content.append(KeyInfo(name=key,
                                   type=enums.RedisType(k_type),
                                   size=await get_len(conn=conn, key=key, key_type=k_type)))
        return RedisPage(content=content, total=len(content), cursor=cursor, paginate_by=pagination.page_size)


async def get(conn_settings: dict, key: str, match: str = None,
              pagination: RedisPagination = RedisPagination()) -> RedisPage:
    """
    查找key值

    :param conn_settings:
    :param key:
    :param match:
    :param pagination:
    :return:
    """
    total = 0
    content = None
    cursor = pagination.cursor + pagination.page_size
    with get_conn(conn_settings) as conn:
        if not conn.exists(key):
            return RedisPage(content=content, total=total, cursor=cursor, paginate_by=pagination.page_size)
        # get type
        key_type = enums.RedisType(conn.type(key))
        # get value
        if key_type == enums.RedisType.string:  # string
            return RedisPage(content=conn.get(key), total=1)
        elif key_type == enums.RedisType.list:  # list
            total = conn.llen(name=key)
            content = conn.lrange(name=key, start=pagination.cursor, end=total)
            cursor = 0
        elif key_type == enums.RedisType.hash:  # hash
            total = conn.hlen(name=key)
            cursor, content = conn.hscan(name=key, cursor=pagination.cursor, match=match)
            # cursor, content = conn.hscan(name=key, cursor=pagination.cursor, match=match, count=pagination.paginate_by)
        elif key_type == enums.RedisType.set:  # set
            total = conn.scard(name=key)
            cursor, content = conn.sscan(name=key, cursor=pagination.cursor, match=match)
            # cursor, content = conn.sscan(name=key, cursor=pagination.cursor, match=match, count=pagination.paginate_by)
        elif key_type == enums.RedisType.zset:  # zset
            total = conn.zcard(name=key)
            cursor, content = conn.zscan(name=key, cursor=pagination.cursor, match=match)
            # cursor, content = conn.zscan(name=key, cursor=pagination.cursor, match=match, count=pagination.paginate_by)
    return RedisPage(content=content, total=total, cursor=cursor, paginate_by=pagination.page_size)


async def delete(*names, conn_settings: dict) -> Any:
    """
    删除指令
    :param conn_settings:
    :return:
    """
    with get_conn(conn_settings) as conn:
        conn.hset()
        return conn.delete(*names)


async def execute(*args, conn_settings: dict) -> Any:
    """
    执行指令
    :param conn_settings:
    :return:
    """
    with get_conn(conn_settings) as conn:
        return conn.execute_command(*args)


async def batch_execute(conn_settings: dict, cmds: List[str]) -> int:
    """
    批量执行

    :param conn_settings:
    :param cmds:
    :return:
    """
    with get_conn(conn_settings) as conn:
        pipe = conn.pipeline()
        for cmd in cmds:
            pipe.execute_command(*split_cmd(cmd))
        return pipe.execute()


async def get_len(conn: redis.Redis, key: str, key_type: str = None) -> int:
    """
    获取key长度/数量

    :param conn:
    :param key:
    :param key_type:
    :return:
    """
    if not key_type:
        key_type = conn.type(key)
    if key_type == enums.RedisType.string:  # string
        return conn.strlen(key)
    elif key_type == enums.RedisType.list:  # list
        return conn.llen(key)
    elif key_type == enums.RedisType.hash:  # hash
        return conn.hlen(key)
    elif key_type == enums.RedisType.set:  # set
        return conn.scard(key)
    elif key_type == enums.RedisType.zset:  # zset
        return conn.zcard(key)
    return conn.memory_usage(key)


def split_cmd(cmd: str) -> list:
    return _split_quote_(cmd=cmd, split='"',
                         left_split=lambda x: _split_quote_(cmd=x, split="'",
                                                            left_split=lambda y: filter(lambda z: z, y.split())))


def _split_quote_(cmd: str, split: str, left_split: Callable = None) -> list:
    pattern = f'({split}[^{split}]*{split})'
    groups = re.split(pattern, cmd)
    cmds = list()
    for group in groups:
        if not group:
            continue
        if group.startswith(split) and group.endswith(split):
            cmds.append(group[1:-1])
        elif left_split:
            cmds.extend(left_split(group))
        else:
            cmds.append(group)
    return cmds


def _scan_(func: Callable, cursor: int, count: int, **kwargs) -> (int, Any):
    c_next, content = func(cursor=cursor, count=count, **kwargs)
    if content or not c_next:
        return c_next, content
    if count <= _REDIS_COUNT_LIMIT_:
        count *= 2
    return _scan_(func=func, cursor=c_next, count=count, **kwargs)
