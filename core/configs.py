from datetime import timedelta

SECRET_ALGORITM = 'HS512'
REFRESH_TOKEN_UNLIMITED = True

ACCESS_TOKEN_EXPIRE_TIME = timedelta(minutes=15)
REFRESH_TOKEN_EXPIRE_TIME = timedelta(days=30)
DEACTIVE_COUNT = 5