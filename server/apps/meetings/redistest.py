import redis
 
# 创建Redis连接
# 假设你的Redis服务器运行在localhost的默认端口6379上，没有密码
# r = redis.Redis(host='127.0.0.1', port=6379, db=0)
 
# 创建Redis连接
# 使用 REDIS_CACHE_URL 进行连接
REDIS_CACHE_URL = 'redis://:1@127.0.0.1:6379/0'
r = redis.from_url(REDIS_CACHE_URL)

# 测试连接
try:
    # 使用ping命令测试连接
    response = r.ping()
    print(f"Ping response REDIS_CACHE_URL : {response}")  # 应该输出'PONG'表示连接成功
except redis.ConnectionError as e:
    print(f"Connection error: {e}")
    
 
# 设置键值对
key = 'test_key'
value = 'Hello Redis!'
r.set(key, value)
 
# 获取键值对
value_retrieved = r.get(key).decode('utf-8')  # decode因为get返回的是bytes类型
print(f"Value for {key}: {value_retrieved}")  # 应该输出之前设置的值
 
# 删除键值对
r.delete(key)
print(f"Key {key} deleted")
 
# 执行其他操作，比如递增计数器等...
counter_key = 'counter'
initial_count = r.get(counter_key)  # 如果不存在则返回None，需要处理或默认值0
if initial_count is None:
    initial_count_value = 0
else:
    initial_count_value = int(initial_count) + 1  # 假设初始值为0，这里增加计数器值
r.set(counter_key, str(initial_count_value))  # 设置新的计数器值到Redis中
print(f"Counter value after increment: {initial_count_value}")  # 打印新的计数器值