import base64
import datetime
from hashlib import md5

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from loguru import logger


def aes_encrypt(key: str, data: str, block_size=128):
    """加密数据
        :param key: 加密秘钥
        :param data: 需要加密数据
        :param block_size: 需要加密数据
        """
    # 将数据转换为byte类型
    data = data.encode("utf-8")
    secret_key = key.encode("utf-8")

    # 填充数据采用pkcs7
    padder = padding.PKCS7(block_size).padder()
    pad_data = padder.update(data) + padder.finalize()

    # 创建密码器
    cipher = Cipher(
        algorithms.AES(secret_key),
        mode=modes.ECB(),
        backend=default_backend()
    )
    # 加密数据
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(pad_data)
    return base64.urlsafe_b64encode(encrypted_data).decode()


def aes_decrypt(key: str, data: str, block_size=128):
    """
    解密数据

    :param key:
    :param data:
    :param block_size: 需要加密数据
    :return:
    """
    key = key.encode("utf-8")
    data = base64.urlsafe_b64decode(data)

    # 创建密码器
    cipher = Cipher(
        algorithms.AES(key),
        mode=modes.ECB(),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    decrypt_data = decryptor.update(data)
    un_padder = padding.PKCS7(block_size).unpadder()
    origin_data = un_padder.update(decrypt_data) + un_padder.finalize()
    return origin_data.decode("utf-8")


def auth_token(key: str, salt: str) -> str:
    data = f'{salt}.{int(datetime.datetime.now().timestamp())}'
    return aes_encrypt(key=key, data=data)


def check_token(key: str, salt: str, token: str, expired: int = 0, tolerance: int = 60) -> bool:
    """

    :param key:
    :param salt:
    :param token:
    :param expired: 超时(秒)
    :param tolerance: 容错范围(秒)
    :return:
    """
    try:
        data = aes_decrypt(key=key, data=token)
        if not data.startswith(salt):
            return False
        if not expired:
            return True
        token_time = int(data[len(salt) + 1:])
        now = int(datetime.datetime.now().timestamp())
        return -tolerance < now - token_time < expired + tolerance
    except Exception as e:
        logger.error("Check Token Error: %s" % e)
        return False


def md5_token(key, salt):
    if isinstance(key, str):
        key = key.encode('ASCII')
    if isinstance(salt, str):
        salt = salt.encode('ASCII')
    return md5(f'{md5(salt).hexdigest()}.{key}'.encode('ASCII')).hexdigest()
