from os import getenv

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

WS_DATA_BASE_DSN: 'str' = getenv('WS_DATA_BASE_DSN')

WS_DATA_BASE_ECHO: 'bool' = getenv('WS_DATA_BASE_ECHO', 'on') == 'on'

WS_SECRET_KEY: 'str' = getenv('WS_DATA_BASE_ECHO', None)

WS_ALGORITHM = getenv('WS_ALGORITHM', 'HS256')

WS_ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv('WS_ACCESS_TOKEN_EXPIRE_MINUTES', 60 * 24 * 7)) # неделя по дефолту
