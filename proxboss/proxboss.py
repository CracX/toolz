'''

        Proxboss - Mass proxy tester

        @creator: CracX
        @year: 2022
        @version: 1.0

'''

from ast import arg
from time import time
import requests
import argparse
import threading
import ctypes
import os
import time
import math

_PROXIES = []

def main(proxy_path: str, threads: int, timeout: int, output, url: str) -> None:
    if not os.path.isfile(proxy_path):
        print(f"File cannot be found: {proxy_path}")
        return
    
    with open(proxy_path, 'r') as f:
        pl = f.read().split('\n')
    
    t1 = time.time()
    try:
        for p in pl:
            while threading.active_count() >= threads:
                continue
            helper(p, timeout, url).start()
    except KeyboardInterrupt:
        print("[!] Stopping all threads, please wait...")
        for thread in threading.enumerate():
            if thread == threading.current_thread():
                continue
            i = thread.name
            thread.raise_exception()
        if output:
            with open(output, 'w') as f:
                f.write('\n'.join(_PROXIES))
        
        print("Bye")
        os._exit(0)
    
    while threading.active_count() > 1:
        continue

    if output:
        with open(output, 'w') as f:
            f.write('\n'.join(_PROXIES))
    print(f"[*] Job done. Time: {math.floor((time.time() - t1) // 0.01 / 100)}s | Proxies read: {len(pl)} | Proxies working: {len(_PROXIES)} | {math.floor((len(_PROXIES) / len(pl)) * 100)}% success rate")
    return

class helper(threading.Thread):
    def __init__(self, proxy, timeout, url):
        threading.Thread.__init__(self)
        self._proxy = proxy
        self._timeout = timeout
        self._url = url
    
    def run(self):
        proxies = {
            'http': "socks5://"+self._proxy,
            'https': "socks5://"+self._proxy
        }
        try:
            t1 = time.time()
            t = requests.get(self._url, proxies=proxies, timeout=self._timeout)
            speed = time.time() - t1
        except:
            return
        if t.status_code == 200:
            _PROXIES.append(self._proxy)
            print(f"[*] Found: {self._proxy}\t\t(total: {len(_PROXIES)})\t(time: {speed // 0.01 / 100}s)")
        return
    
    def get_id(self):
 
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
    
    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tests all proxies in a list and returns only working ones.')
    parser.add_argument('proxy_list', type=str, help="Path to the proxy file")
    parser.add_argument('-o', '--output', type=str, help="Path to the file where the working proxies will be written", default=None)
    parser.add_argument('-t', '--threads', type=int, help="Number of threads used for parsing proxies (Default = 10)", default=10)
    parser.add_argument('-T', '--timeout', type=int, help="Number of seconds to wait before timeouting the proxy connection (Default = 10)", default=10)
    parser.add_argument('-u', '--url', type=str, help="URL that will be used for proxy testing (Default = google.com)", default="https://google.com")

    args = parser.parse_args()
    main(args.proxy_list, args.threads, args.timeout, args.output, args.url)