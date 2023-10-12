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

  def CSearch(self, EDB, CLen, ctr, stw):
    res = []
    j = ctr
    while j <= CLen:
      key = self.encAlgo.get_str_sha1_secret_str(stw + '0')[:20]
      value = EDB.get(key, 'NULL')
      if value != 'NULL':
        mask = self.encAlgo.get_str_sha1_secret_str(stw + '1')[:40]
        msgr = self.encAlgo.x_o_r(value, mask).zfill(40)

        msg = msgr[-40:-20]
        rt = msgr[-20:]

        while rt != '00000000000000000000':
          idValue = EDB[msg]
          AESvalue = encAlgo().decrypt_oralce(self.AESKey, idValue)
          id = AESvalue[:-1]
          op = AESvalue[-1]
          if op == '1':
            res.append(int(id))

          key = self.encAlgo.get_str_sha1_secret_str(rt + '0')[:20]
          value1 = EDB[key]
          mask1 = self.encAlgo.get_str_sha1_secret_str(rt + '1')[:40]
          msgr1 = self.encAlgo.x_o_r(value1, mask1).zfill(40)
          msg = msgr1[-40:-20]
          rt = msgr1[-20:]

        idValue = EDB[msg]
        AESvalue = encAlgo().decrypt_oralce(self.AESKey, idValue)
        id = AESvalue[:-1]
        op = AESvalue[-1]
        if op == '1':
          res.append(int(id))
      j = j + 1
      stw = self.encAlgo.get_str_sha1_secret_str(stw)[:20]

    return res




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
          ctr, stw = post_body


          counter = 1
          count = 0
          total_consump = 0.0
          while count < counter:
            Sumtime_search = 0
            begin_time_search = time.time()
            list = searchServer().CSearch(GLOBAL_DATASET, 1200, ctr, stw)

            end_time_search = time.time()
            Sumtime_search += (end_time_search - begin_time_search)
            total_consump += Sumtime_search
            count += 1

          avg = (total_consump / counter)
          print(list)
          print(len(list))
          print(avg)
          response = json.dumps(list).encode()
          self.wfile.write(response)
if __name__ == '__main__':
  server_address = ("", 8100)

  httpd = HTTPServer(server_address, RequestHandlerImpl)

  httpd.serve_forever()
