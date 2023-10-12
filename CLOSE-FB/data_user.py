import requests
import time
import json

import numpy as np
from encAlgo import *
import  time


def Merge(dict1, dict2):
  res = {**dict1, **dict2}
  return res

class genTrapdoor:
  def __init__(self):
    self.AESKey = '123456'
    self.list = []
    self.CLen = 1200
    self.encAlgo = encAlgo()
    self.fidKey = 'password'

  def Hd(self, ctr, h):
    for i in range(ctr):
      h = self.encAlgo.get_str_sha1_secret_str(h)[:20]
    return h

  def search(self, keyword, ctr, number_circle):
    ktw = encAlgo().F1(self.fidKey, keyword + str(number_circle))[:20]
    begin_time_1 = time.time()
    stw = self.Hd(ctr, ktw)[:20]
    end_time_1 = time.time()
    print(end_time_1 - begin_time_1)
    return ctr, stw

def getCount(url0, keyword):
  headers = {'content-type': 'application/json'}
  response = requests.post(url0, data=keyword, headers=headers)
  if response.status_code == 200:
    print(f"Received response from server: {response.content}")
    Count = json.loads(response.text)
    print(type(Count))
    print(Count)

    # print(c_update)
    # print(c_search)
    return Count
  else:
    print("Error: server did not respond successfully")
    return 0, 0


if __name__=='__main__':
  url0 = 'http://localhost:8001/data_user/search/10000'
  post_body = getCount(url0, 'Subject')
  ctr, number_circle = post_body
  ctr = int(ctr)
  number_circle = int(number_circle)

  url1 = 'http://localhost:8100/data_user/search/10000'

  Sumtime_search = 0
  begin_time_search = time.time()
  ctr, ctw = genTrapdoor().search('Subject', ctr + 1, number_circle)

  headers = {'content-type': 'application/json'}
  response = requests.post(url1, data=json.dumps([ctr, ctw]), headers=headers)

  # print(response)
  if response.status_code == 200:
    # print(GRP)
    # print(response.text)
    end_time_search = time.time()
    Sumtime_search += (end_time_search - begin_time_search)

    print('Sum_search', Sumtime_search)
    # response_data = json.loads(response.content)
    # print(f"Received response from server: {response_data['message']}")
  else:
    print("Error: server did not respond successfully")