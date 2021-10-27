import json
import threading
import time
import requests


class Presstest(object):
    """并发压力测试"""
    def __init__(self, press_url, data):
        self.press_url = press_url
        self.data = data
        self.headers = {
            'Content-Type': 'application/json; charset=UTF-8',
        }

    def test_interface(self, thread_i, work_i):
        """压测接口"""
        global INDEX
        INDEX += 1

        global ERROR_NUM
        global TIME_LENS
        try:
            start = time.time()
            r = requests.post(self.press_url, json=self.data).json()
            # ensure the request was sucessful
            print(r)
            if r["success"]:
                print("[INFO] thread {} work {} OK".format(thread_i, work_i))
            # otherwise, the request failed
            else:
                print("[INFO] thread {} work {} FAILED".format(thread_i, work_i))
            end = time.time()
            TIME_LENS.append(end - start)
        except Exception as e:
            ERROR_NUM += 1
            print(e)

    def test_onework(self, thread_i):
        """一次并发处理单个任务"""
        i = 0
        while i < ONE_WORKER_NUM:
            i += 1
            self.test_interface(thread_i, i)
        time.sleep(LOOP_SLEEP)

    # def do_request(self, url, payload):
    #     """通用http获取webapi请求结果方法"""
    #     request = urllib.request.Request(url, json.dumps(payload).encode("utf-8"), headers=self.headers)
    #     retry_num = 0
    #     while retry_num < 3:
    #         response = urllib.request.urlopen(request, timeout=300)
    #         if not response or response.status == 421:
    #             time.sleep(1)
    #             retry_num = retry_num + 1
    #             continue
    #         else:
    #             break
    #     response_content = response.read()
    #     if hasattr(response_content, 'decode'):
    #         response_content = response_content.decode('utf-8')
    #     return response_content

    def run(self):
        """使用多线程进程并发测试"""
        t1 = time.time()
        Threads = []

        for i in range(THREAD_NUM):
            t = threading.Thread(target=self.test_onework, name="T" + str(i), args=(i,))
            t.setDaemon(True)
            Threads.append(t)

        for t in Threads:
            t.start()
        for t in Threads:
            t.join()
        t2 = time.time()

        print("===============压测结果===================")
        print("URL:", self.press_url)
        print("任务数量:", THREAD_NUM, "*", ONE_WORKER_NUM, "=", THREAD_NUM * ONE_WORKER_NUM)
        print("总耗时(秒):", t2 - t1)
        print("每次请求耗时(秒):", (t2 - t1) / (THREAD_NUM * ONE_WORKER_NUM))
        print("每秒承载请求数:", 1 / ((t2 - t1) / (THREAD_NUM * ONE_WORKER_NUM)))
        print("错误数量:", ERROR_NUM)
        print(INDEX)


if __name__ == '__main__':
    press_url = 'http://localhost:5000/predict'
    DATA_PATH = "test.json"
    TIME_LENS = []
    INDEX = 0
    THREAD_NUM = 25  # 并发线程总数
    ONE_WORKER_NUM = 25  # 每个线程的循环次数
    LOOP_SLEEP = 10  # 每次请求时间间隔(ms)
    ERROR_NUM = 0  # 出错数

    with open(DATA_PATH, 'r') as f:
        data = json.load(f)
    obj = Presstest(press_url, data)
    obj.run()
