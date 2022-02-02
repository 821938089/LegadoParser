from enum import Enum


class Body(Enum):
    # 请求体类型
    JSON = 1
    FORM = 2
    XML = 3
