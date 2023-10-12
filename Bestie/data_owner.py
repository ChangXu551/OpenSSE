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
COUNT ={}
class Client:
    def __init__(self):
        self.dic = {}
        self.AESKey = '123456'
        self.fidKey = 'password'
        self.Count = {}
        self.CDB ={}
        self.GRP ={}
        self.encAlgo = encAlgo()
        self.lam = 20
        self.slam = 21

    def add_file(self, data):
        # self.keyList = self.readDict()
        for i in range(data):
            self.update(1,'Subject',i)
        return self.dic, self.Count


    def update(self, op, keyword, id):
        value = self.Count.get(keyword, 'NULL')
        if value == 'NULL':
            self.Count[keyword] = [0, 0]
            c_update = 0
            c_search = 0
        else:
            c_update = self.Count[keyword][0]
            c_search = self.Count[keyword][1]

        self.Count[keyword][0] = c_update + 1
        c_update = c_update + 1
        str_c_search = str(int(c_search)).zfill(5)
        K_w = self.encAlgo.F1(self.fidKey, keyword + str_c_search)[:20]
        K_w_2 = self.encAlgo.F1(self.fidKey, keyword + str(-1).zfill(5))[:20]

        value0 = self.encAlgo.F3(K_w, str(c_update))[:41]
        G_Kw_id = self.encAlgo.F2(K_w_2, str(id))[:20]
        mask = '000000000000000' + str(op) + G_Kw_id
        value1 = self.encAlgo.x_o_r(value0, mask).zfill(41)[-41:]
        L = value1[:self.lam]
        D = value1[-1*(self.slam):]

        C =  self.encAlgo.encrypt_oracle(self.AESKey, str(id))

        self.dic[L] = [D, C]

    def delete_file(self, keyword, ind):
        self.update(0, keyword, ind)


def gen_index(data):

    filename = "inverted_index_" + data + ".txt"
    universal_dict = {}
    with open(filename, "r") as f:
        for line in f:
            values = line.split(" ")
            universal_dict[values[0]] = []
            for i in values[1:len(values)]:
                universal_dict[values[0]].append(i)  # 所有的关键字对应文件
    counter = 1
    keyword = 'Subject'
    count = 0
    total_consump1 = 0.0

    while count < counter:
        Sumtime_index = 0
        begin_time_index = time.time()
        c = Client()

        dataset, Count = c.add_file(int(data))

        end_time_index = time.time()
        Sumtime_index += (end_time_index - begin_time_index)
        total_consump1 += Sumtime_index
        count = count + 1
    global COUNT
    COUNT = Count
    avg1 = (total_consump1 / counter)
    print("avg_index_time:" + str(avg1))
    return dataset

def add_impl(data):
  dataset = gen_index(data)
  # print(dataset)
  headers = {"Content-type": "application/json"}
  x = requests.post(f"http://localhost:8000/data_owner/add/{data}", data=json.dumps(dataset), headers=headers)
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
                  response_data =COUNT[post_body]
                  print(type(response_data))
                  print(response_data)
                  response = json.dumps(response_data).encode()
                  self.wfile.write(response)

if __name__=='__main__':
    server_address = ("", 8001)
    httpd = http.server.HTTPServer(server_address, RequestHandlerImpl)
    httpd.serve_forever()
