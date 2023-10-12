import requests
import time
import json

import numpy as np
from encAlgo import *
import  time

class genTrapdoor:
  def __init__(self):
    self.dic = {}
    self.AESKey = '123456'
    self.fidKey = 'password'
    self.Count = {}
    self.CDB = {}
    self.GRP = {}
    self.encAlgo = encAlgo()
    self.lam = 20
    self.slam = 21

  def client_search1(self, keyword, c_update, c_search):


    str_c_search = str(int(c_search)).zfill(5)
    K_w = self.encAlgo.F1(self.fidKey, keyword + str_c_search)[:20]
    K_w_2 = self.encAlgo.F1(self.fidKey, keyword + str(-1).zfill(5))[:20]

    I_grp_w = self.encAlgo.F2(K_w_2, '000000000')
    return c_update, K_w, I_grp_w

  def client_search2(self, keyword, GRP):
    idList = []
    for i in GRP:
      for key in i:
        dec = i[key]
        id = self.encAlgo.decrypt_oralce(self.AESKey, dec)
        idList.append(id)

    return idList
def getCount(url0, keyword):
  headers = {'content-type': 'text/plain'}
  response = requests.post(url0, data=keyword, headers=headers)
  if response.status_code == 200:
    print(f"Received response from server: {response.content}")
    Count = json.loads(response.content.decode('utf-8'))
    print(type(Count))
    print(Count)
    c_update = Count[0]
    c_search = Count[1]
    # print(c_update)
    # print(c_search)
    return c_update, c_search
  else:
    print("Error: server did not respond successfully")
    return 0, 0


if __name__=='__main__':
  url0 = 'http://localhost:8001/data_user/search/10000'
  c_update, c_search = getCount(url0, 'Subject')

  url1 = 'http://localhost:8000/data_user/search/10000'

  Sumtime_search = 0
  begin_time_search = time.time()
  c_update, K_w, I_grp_w = genTrapdoor().client_search1('Subject', int(c_update), int(c_search))

  headers = {'content-type': 'application/json'}
  response = requests.post(url1, data=json.dumps([c_update, K_w, I_grp_w]), headers=headers)

  # print(response)
  if response.status_code == 200:
    keyword = 'Subject'
    print(response.text)
    GRP = json.loads(response.content.decode('utf-8'))
    # print(GRP)
    idList = genTrapdoor().client_search2(keyword, GRP)
    print(idList)
    # print(response.text)
    end_time_search = time.time()
    Sumtime_search += (end_time_search - begin_time_search)

    print( Sumtime_search)
    # response_data = json.loads(response.content)
    # print(f"Received response from server: {response_data['message']}")
  else:
    print("Error: server did not respond successfully")