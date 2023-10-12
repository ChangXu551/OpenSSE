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
        self.encAlgo = encAlgo()  # H1 H2:sha256 F P:AES
        self.Count = {}

    def Update(self, ind, keyword, op):
        hw = self.encAlgo.get_str_sha1_secret_str(keyword)[:20]
        tw = self.encAlgo.F1(self.fidKey, hw)[:20]
        st = self.Count.get(keyword, 'NULL')
        if st == 'NULL':
            r1 = random.getrandbits(90)
            stc = str(r1).zfill(32)
            c = 0
        else:
            stc = st[0]
            c = st[1]

        r2 = random.getrandbits(90)
        kc1 = str(r2).zfill(32)
        stc1 = self.encAlgo.encrypt_oracle(kc1, stc)
        self.Count[keyword] = [stc1, c + 1]

        mask = self.encAlgo.H2(tw + stc1)[:38]

        value = str(ind).zfill(5) + str(op) + kc1
        e = self.encAlgo.x_o_r(mask, value).zfill(38)[-38:]
        u = self.encAlgo.H1(tw + stc1)[:20]
        self.dic[u] = e

    def add_file(self, universal_dict):
        for keyword in universal_dict:
            for ind in universal_dict[keyword]:
                self.Update(ind, keyword, 1)
        return self.dic, self.Count

    def delete_file(self, keyword, ind):
        self.Update(ind, keyword, 0)
        return self.dic


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

        dataset, Count = c.add_file(universal_dict)
        print(type(Count))
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
  x = requests.post(f"http://localhost:8100/data_owner/add/{data}", data=json.dumps(dataset), headers=headers)
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
                  response_data =COUNT
                  print(type(response_data))
                  print(response_data)
                  response = json.dumps(response_data).encode()
                  self.wfile.write(response)

if __name__=='__main__':
    server_address = ("", 8001)
    httpd = http.server.HTTPServer(server_address, RequestHandlerImpl)
    httpd.serve_forever()
