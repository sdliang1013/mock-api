import datetime
import os
from enum import Enum
from pathlib import Path
from typing import List, Optional

import anyio
import filetype
from fastapi import HTTPException
from pydantic import BaseModel

_EXPLORER_ROOT_ = '/'
_ABS_ROOT_PATH_ = os.path.abspath(_EXPLORER_ROOT_)


class FileType(str, Enum):
    File = "file"
    Dir = "dir"
    Link = "link"
    UNKNOWN = "unknown"

    @classmethod
    def get_type(cls, path: str):
        if os.path.isdir(path):
            return cls.Dir
        elif os.path.isfile(path):
            return cls.File
        elif os.path.islink(path):
            return cls.Link
        return cls.UNKNOWN


class FileInfo(BaseModel):
    name: str  # 文件名
    path: str  # 路径
    suffix: Optional[str]  # 后缀
    size: int  # 大小
    type: FileType  # 类型
    create_at: datetime.datetime  # 创建时间
    update_at: datetime.datetime  # 更新时间


async def list_dir(parent: str = '/') -> List[FileInfo]:
    files = list()
    # check dir
    if os.path.isfile(parent):
        return files
    # list files
    paths = list(map(lambda x: unix_path_join(parent, x), os.listdir(parent)))
    paths.sort()
    for path in paths:
        f_path = Path(path)
        f_stat = os.stat(path)
        files.append(FileInfo(name=f_path.name,
                              path=path,
                              suffix=f_path.suffix,
                              size=f_stat.st_size,
                              type=FileType.get_type(path),
                              create_at=f_stat.st_ctime,
                              update_at=f_stat.st_mtime))
    return files


def to_unix_split(path: str):
    """
    To Unix文件路径符号

    :param path:
    :return:
    """
    return path.replace("\\", "/")


def unix_path_join(str1: str, str2: str):
    """
    路径合并

    :param str1:
    :param str2:
    :return:
    """
    str1 = to_unix_split(str1)
    str2 = to_unix_split(str2)
    if str1.endswith("/"):
        str1 = str1[:-1]
    if str2.startswith("/"):
        str2 = str2[1:]
    return f"{str1}/{str2}"


def wrap_root(path: str):
    """
    append [root]/path, disable .. path
    :param path:
    :return:
    """
    path = unix_path_join(_EXPLORER_ROOT_, path)
    if "../" in path or "/.." in path:
        raise HTTPException(status_code=500, detail="Illegal Path")
    return path


def remove_root(path: str):
    abs_path = os.path.abspath(path)
    if abs_path.startswith(_ABS_ROOT_PATH_):
        return to_unix_split(abs_path[len(_ABS_ROOT_PATH_):])
    return to_unix_split(path)


def txt_file(path: str) -> bool:
    return filetype.guess(path) is None


async def read_last(path: str, lines: int = 1) -> (list, int):
    """
    读取文件最后的内容

    :param path:
    :param lines: 最后的行数
    :return:
    """
    lines = max(lines, 1)
    limit = os.stat(path).st_size
    async with await anyio.open_file(file=path, mode='rb') as f:  # 打开文件
        off = 50  # 设置偏移量
        while True:
            if off >= limit:
                await f.seek(0)
                last_lines = await f.readlines()  # 读取文件指针范围内所有行
                tell = await f.tell()
                break
            await f.seek(-off, 2)  # seek(off, 2)表示文件指针：从文件末尾(2)开始向前50个字符(-50)
            last_lines = await f.readlines()  # 读取文件指针范围内所有行
            if len(last_lines) >= lines:  # 判断是否最后至少有两行，这样保证了最后一行是完整的
                last_lines = last_lines[-lines:]
                tell = await f.tell()
                break
            off *= 2

    return last_lines, tell


async def read_lines(path: str, lines: int = 0, offset: int = 0) -> (list, int, bool):
    size = os.stat(path).st_size
    content = list()
    # is end
    if offset >= size:
        return content, size, True
    async with await anyio.open_file(file=path, mode='rb') as f:
        if offset:
            await f.seek(offset)
        if not lines:
            content = await f.readlines()
            tell = size
        else:
            for _ in range(lines):
                content.append(await f.readline())
                tell = await f.tell()
                if tell >= size:
                    break

    return content, tell, tell >= size


async def read_range(path: str, start: int = 0, end: int = -1) -> bytes:
    """

    :param path:
    :param start:
    :param end:
    :return: [start, end)
    """
    len_file = os.stat(path=path).st_size
    if end < 0 or end > len_file:
        end = len_file
    # end
    if start >= end or start >= len_file:
        return b''
    async with await anyio.open_file(file=path, mode='rb') as file:
        await file.seek(start)
        return await file.read(end - start)
