import redis
import json

r = redis.Redis(
    host='localhost',
    port=6379,
) 
def ping():
    return r.ping()

def get_user(id: str):
    dict_bytes = r.get(id)

    if not dict_bytes:
        return {}

    dict_str = dict_bytes.decode('utf-8')

    my_dict = json.loads(dict_str)

    return my_dict

def set_user(id: str, data: dict):
    r.set(id, bytes(json.dumps(data), "utf-8"))


def is_user_exist(id: int) -> bool:
    return bool(get_user(id))