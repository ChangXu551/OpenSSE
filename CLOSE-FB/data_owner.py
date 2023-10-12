import http.server
import requests
import numpy as np
from encAlgo import *
import  time
import json
import random
import copy
np.set_printoptions(suppress=True)
np.set_printoptions(precision=3)
import multiprocessing
# file_data_arr =  [i for i in range(10000, 110000, 10000)]
CTR = 0
CIRCLE = 0
class CUpdate:
    def __init__(self):
        self.dic = {}
        self.dataset = {}
        self.AESKey = '123456'
        self.fidKey = 'password'
        self.CLen = 1200
        self.KW = {}
        self.encAlgo = encAlgo()

    def Hd(self, ctr, h):
        for i in range(ctr):
            h = self.encAlgo.get_str_sha1_secret_str(h)[:20]
        return h

    def encID(self, fidKey, AESKey, count):   #加密ID
        value = encAlgo().encrypt_oracle(AESKey, count)
        key = encAlgo().F2(fidKey, count)[-20:]
        return key,value

    def Update(self,stw,dicw,ind):
        key = self.encAlgo.get_str_sha1_secret_str(stw+'0')[:20]
        value = dicw.get(key,'NULL')
        if value == 'NULL':
            mask = self.encAlgo.get_str_sha1_secret_str(stw+'1')[:40]

            idKey, idValue = self.encID(self.fidKey, self.AESKey, str(ind)+'1')  # msg的大小要根据文件总数调节
            dicw[idKey] = idValue

            # str_ind = str(ind).zfill(10)
            eva = idKey +'00000000000000000000'
            value = self.encAlgo.x_o_r(mask, eva).zfill(40)
            dicw[key] = value
        else:
            r = random.getrandbits(32)
            str_r = str(r).zfill(20)
            mask = self.encAlgo.get_str_sha1_secret_str(stw+'1')[:40]

            idKey, idValue = self.encID(self.fidKey, self.AESKey, str(ind) + '1')  # msg的大小要根据文件总数调节
            dicw[idKey] = idValue


            value3 = self.encAlgo.x_o_r(mask, idKey +str_r)
            dicw[key] = value3
            key1 = self.encAlgo.get_str_sha1_secret_str(str_r+'0')[:20]
            mask1 = self.encAlgo.get_str_sha1_secret_str(str_r+'1')[:40]
            mask2 = self.encAlgo.get_str_sha1_secret_str(stw + '1')[:40]
            value1 = self.encAlgo.x_o_r(mask1, mask2).zfill(40)
            value2 = self.encAlgo.x_o_r(value, value1).zfill(40)
            dicw[key1] = value2
        return dicw


    def Merge(self, dict1, dict2):
        res = {**dict1, **dict2}
        return res

    def chain(self,  universal_dict, file_data ):  #生成链
        dic = {}
        ctr = self.CLen
        number_circle = 1


        for keyword in universal_dict:
            i = 0
            while i < file_data:
                if ctr == 0:
                    1
                    # ctr = self.CLen
                    # list = searchServer().search(keyword, self.dataset, 1, number_circle)
                    # number_circle = number_circle + 1
                    # self.dataset = {}
                    # ktw = self.encAlgo.F1(self.fidKey, keyword + str(number_circle))[:20]
                    # stw = self.Hd(ctr, ktw)
                    # self.KW[keyword] = stw
                    # dic[keyword] = {}
                    # for j in list:
                    #     dic[keyword] = self.Update(stw, dic[keyword], j)
                    #     self.dataset = self.Merge(self.dataset, dic[keyword])
                    # ctr = ctr - 1
                    # self.KW.pop(keyword)
                else:
                    for j in range(10000):
                        count = universal_dict[keyword][i + j]

                        stw = self.KW.get(keyword, 'NULL')
                        if stw == 'NULL':
                            ktw = self.encAlgo.F1(self.fidKey, keyword + str(number_circle))[:20]
                            stw = self.Hd(ctr, ktw)
                            self.KW[keyword] = stw
                            dic[keyword] = {}
                        dic[keyword] = self.Update(stw, dic[keyword], count)
                        self.dataset = self.Merge(self.dataset, dic[keyword])
                    ctr = ctr - 1
                    self.KW.pop(keyword)
                    i = i + 10000

        return self.dataset, ctr, number_circle



def gen_index(data):
    counter = 1
    keyword = 'Subject'

    count = 0
    total_consump = 0.0

    filename = "inverted_index_" + data + ".txt"
    universal_dict = {}
    with open(filename, "r") as f:
        for line in f:
            values = line.split(" ")
            universal_dict[values[0]] = []
            for i in values[1:len(values)]:
                universal_dict[values[0]].append(i)  # 所有的关键字对应文件

    while count < counter:
        Sumtime_index = 0
        begin_time_index = time.time()
        a = CUpdate()
        dictw, ctr, number_circle = a.chain(universal_dict, int(data))
        global CTR
        CTR = ctr
        global CIRCLE
        CIRCLE = number_circle

        end_time_index = time.time()
        Sumtime_index += (end_time_index - begin_time_index)
        total_consump += Sumtime_index
        count += 1
    avg = (total_consump / counter)
    print("avg_index_time:" + str(avg))
    return dictw


def add_impl(data):
  dictw = gen_index(data)
  # print(dataset)
  headers = {"Content-type": "application/json"}
  x = requests.post(f"http://localhost:8100/data_owner/add/{data}", data=json.dumps(dictw), headers=headers)
  print(x.text)

def delete_impl(data, wfile):
  wfile.write(f"delete {data} from database".encode("utf-8"))


class RequestHandlerImpl(http.server.BaseHTTPRequestHandler):
  def do_GET(self):
      self.send_response(200)
      self.send_header("Content-Type", "text/html; charset=utf-8")
      self.end_headers()
      self.wfile.write("Hello World from sever2\n".encode("utf-8"))
      _split = self.path.split("/")
      # print(_split)
      if len(_split) == 4:
          _, sender, operation, data = _split
          if sender == 'data_owner':
              if operation == "add":
                  add_impl(data)
              elif operation == "delete":
                  delete_impl(data, self.wfile)
          elif sender == 'data_user':
              response_data = {'message': 'Hello, {}! We have received your messages!'.format(sender)}
              response = json.dumps(response_data).encode()
              self.wfile.write(response)

  def do_POST(self):
      content_length = int(self.headers['Content-Length'])
      post_body = self.rfile.read(content_length).decode()
      print(f"Received data from client: {post_body}")

      self.send_response(200)
      self.send_header('Content-type', 'application/json')
      self.end_headers()

      # parse the received data as JSON
      _split = self.path.split("/")
      # print(len(_split))
      if len(_split) == 4:
          _, sender, operation, data = _split
          if sender == 'data_owner':
              received_data = json.loads(post_body)
              print(received_data)
              if operation == "add":
                  add_impl(data)
              elif operation == "delete":
                  delete_impl(data, self.wfile)
          elif sender == 'data_user':
              if operation == "search":
                  response_data =[CTR, CIRCLE]
                  print(type(response_data))
                  print(response_data)
                  response = json.dumps(response_data).encode()
                  self.wfile.write(response)

if __name__=='__main__':
    server_address = ("", 8001)
    httpd = http.server.HTTPServer(server_address, RequestHandlerImpl)
    httpd.serve_forever()
