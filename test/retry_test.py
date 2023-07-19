from retrying import retry
import time

s = 0
e = 0

@retry(wait_random_min=3000, wait_random_max=10000)
def wait_exponential_1000():
    s = time.time()
    print(time.time() - s)
    # print("Wait 2^x * 1000 milliseconds between each retry, up to 10 seconds, then 10 seconds afterwards")
    raise Exception("Retry!")


wait_exponential_1000()