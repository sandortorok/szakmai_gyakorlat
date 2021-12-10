import redis
from datetime import timedelta, datetime
redis_client = redis.Redis(host='localhost', port='6379')


a = redis_client.keys("*asdasd*")
if not a:
    print('empty')
else:
    print(a)