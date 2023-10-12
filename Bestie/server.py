from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import numpy as np
from encAlgo import *
import  time
import numpy as np

import multiprocessing
from encAlgo import *

np.set_printoptions(suppress=True)
np.set_printoptions(precision=3)

GLOBAL_DATASET = {}

class searchServer:
  def __init__(self,GLOBAL_DATASET):
    self.dic = GLOBAL_DATASET
    self.AESKey = '123456'
    self.fidKey = 'password'
    self.Count = {}
    self.CDB = {}
    self.GRP = {}
    self.encAlgo = encAlgo()
    self.lam = 20
    self.slam = 21

  def server_search(self, c_update, K_w, I_grp_w):
    DD = []
    self.GRP[I_grp_w] = []
    i = c_update
    while i > 0:
      LD = self.encAlgo.F3(K_w, str(i))[:41]
      L = LD[:self.lam]
      Ds = LD[-1 * (self.slam):]
      D = self.dic[L][0]
      C = self.dic[L][1]
      value0 = self.encAlgo.x_o_r(D, Ds).zfill(21)[-21:]
      op = value0[: 1]
      X = value0[1 - 1 * self.slam:]
      if op == '0':
        DD.append(X)
        for item in self.GRP[I_grp_w]:
          for item in item.items():
            if item[0] == X:
              self.GRP[I_grp_w].pop(item)
              break

      else:
        if X not in DD:
          dict = {}
          dict[X] = C
          self.GRP[I_grp_w].append(dict)
      i = i - 1
    self.dic = {}
    return self.GRP[I_grp_w]


def delete_impl(data, wfile):
  wfile.write(f"delete {data} from database".encode())


class RequestHandlerImpl(BaseHTTPRequestHandler):
  def do_POST(self):

    content_length = int(self.headers['Content-Length'])
    post_body = self.rfile.read(content_length).decode()
    print(f"Received data from client: {post_body}")

    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()

    # determine which client sent the request based on the URL
    # sender = 'data_owner' if '/data_owner' in self.path else 'data_user'

    _split = self.path.split("/")
    # print(len(_split))
    
    if len(_split) == 4:
      _, sender, operation, data = _split
      if sender == 'data_owner':
        response_data = {'message': 'Hello, {}! We have received your messages!'.format(sender)}
        response = json.dumps(response_data).encode()
        self.wfile.write(response)

        if operation == "add":
          post_body = json.loads(post_body)
          dataset = post_body

          print(dataset)
          print(len(dataset))
          # print(Matrix)

          global GLOBAL_DATASET
          GLOBAL_DATASET = dataset

        elif operation == "delete":
          delete_impl(data, self.wfile)


      elif sender == 'data_user':
        if operation == "search":
          post_body = json.loads(post_body)
          c_update, K_w, I_grp_w = post_body
          GRP = searchServer(GLOBAL_DATASET).server_search(c_update, K_w, I_grp_w)
          print(GRP)
          response = json.dumps(GRP).encode()
          self.wfile.write(response)
if __name__ == '__main__':
  server_address = ("", 8000)

  httpd = HTTPServer(server_address, RequestHandlerImpl)

  httpd.serve_forever()
