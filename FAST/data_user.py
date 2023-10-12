import requests
import time
import json

import numpy as np
from encAlgo import *
import  time

class genTrapdoor:
  def __init__(self, Count):
    self.dic = {}
    self.AESKey = '123456'
    self.fidKey = 'password'
    self.Count = Count
    self.CDB = {}
    self.GRP = {}
    self.encAlgo = encAlgo()
    self.lam = 20
    self.slam = 21

  def client_search(self, keyword):
    hw = self.encAlgo.get_str_sha1_secret_str(keyword)[:20]
    tw = self.encAlgo.F1(self.fidKey, hw)[:20]
    st = self.Count.get(keyword, 'NULL')
    if st == 'NULL':
      return 0
    else:
      return tw, st[0], st[1]

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
  Count = getCount(url0, 'Subject')

  url1 = 'http://localhost:8100/data_user/search/10000'

  Sumtime_search = 0
  begin_time_search = time.time()
  tw, stc, c = genTrapdoor(Count).client_search('Subject')

  headers = {'content-type': 'application/json'}
  response = requests.post(url1, data=json.dumps([tw, stc, c]), headers=headers)

  # print(response)
  if response.status_code == 200:
    # print(GRP)
    # print(response.text)
    end_time_search = time.time()
    Sumtime_search += (end_time_search - begin_time_search)

    print( Sumtime_search)
    # response_data = json.loads(response.content)
    # print(f"Received response from server: {response_data['message']}")
  else:
    print("Error: server did not respond successfully")