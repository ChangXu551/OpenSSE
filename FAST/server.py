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
    self.encAlgo = encAlgo()  # H1 H2:sha256 F P:AES
    self.Count = {}

  def server_search(self, tw, stc, c):
    delete = []
    idList = []
    i = c
    while i > 0:
      u = self.encAlgo.H1(tw + stc)[:20]
      e = self.dic[u]
      mask = self.encAlgo.H2(tw + stc)[:38]

      value = self.encAlgo.x_o_r(e, mask).zfill(38)
      ind = int(value[:5])
      op = value[5:6]
      ki = value[-32:]
      if op == '0':
        delete.append(ind)
      else:
        if ind in delete:
          delete.remove(ind)
        else:
          idList.append(ind)
      stc = self.encAlgo.decrypt_oralce(ki, stc)
      i = i - 1
    return idList


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
          tw, stc, c = post_body
          idList = searchServer(GLOBAL_DATASET).server_search(tw, stc, c)
          print(idList)
          response = json.dumps(idList).encode()
          self.wfile.write(response)
if __name__ == '__main__':
  server_address = ("", 8100)

  httpd = HTTPServer(server_address, RequestHandlerImpl)

  httpd.serve_forever()
