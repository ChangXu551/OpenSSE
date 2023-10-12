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
GLOBAL_MATRIX = {}

class searchServer:
  def __init__(self, dataset, encMatrix, trapMatrix, ma):
    self.dataset = dataset
    self.encMatrix = encMatrix
    self.trapMatrix = trapMatrix
    self.AESKey = '123456'
    self.fidKey = 'password'
    self.keywordLength = 22
    self.timeLength = 15
    self.lenCount = self.keywordLength + self.timeLength
    self.m_size = self.lenCount + 3
    self.k = 0
    self.ma = ma

  def encID(self, fidKey, AESKey, count):  # 加密ID
    value = encAlgo().encrypt_oracle(AESKey, count)
    key = encAlgo().F2(fidKey, count)[-10:]
    return key, value

  def test2(self):
    _processes = []
    for index in range(10):
      _process = multiprocessing.Process(target=self.long_running_function, args=(index,))
      _process.start()
      _processes.append(_process)
    for _process in _processes:
      _process.join()
    # pool = mp.Pool(mp.cpu_count())
    # pool.map(self.long_running_function, [i for i in self.encMatrix.keys()])
    # pool.close()

  def long_running_function(self, t):
    t = t * self.ma
    for i in range(self.ma):
      m = t + i
      for j in self.trapMatrix:
        resultMatrix = np.dot(self.encMatrix[str(m)], j)
        tril = np.ndarray.trace(resultMatrix)

        # if (tril > 0):
        #     key = str(int(tril)).zfill(10)
        #     return key
      # print(m)
    return 0

  def search(self, file_data):

    sum_time_matrix = 0
    # k = 0
    begin_time_matrix = time.time()
    begin_time_process = time.time()
    # A = np.zeros((self.m_size, self.m_size))
    # for i in self.encMatrix.keys():
    #     A = np.concatenate([A, self.encMatrix[i]], 0)
    # for j in self.trapMatrix:
    #     resultMatrix = np.dot(A, j)
    #     sub_matrices = [resultMatrix[i:i + self.m_size] for i in range(0, len(resultMatrix), self.m_size)]
    #     for t in sub_matrices:
    #         tril = np.ndarray.trace(t)
    #         if (tril < 0):
    #             k = k +1

    # for i in self.encMatrix.keys():
    #     if i != 'Subject':
    #         flag = 0
    #         for j in self.trapMatrix:
    #             resultMatrix = np.dot(self.encMatrix[i], j)
    #             tril = np.ndarray.trace(resultMatrix)
    #             if (tril > 0):
    #                 flag = 1
    #                 key = str(int(tril)).zfill(10)
    #                 break
    #         if (flag == 1):
    #             break
    #         k = k + 1
    #         if(k == 50000):
    #             break

    self.test2()
    # print(len(self.trapMatrix))
    end_time_process = time.time()
    print("time_process", end_time_process - begin_time_process)

    i = 'Subject'
    for j in self.trapMatrix:
      resultMatrix = np.dot(self.encMatrix[i], j)
      tril = np.ndarray.trace(resultMatrix)
      if (tril > 0):
        key = str(int(tril)).zfill(10)
        break

    end_time_matrix = time.time()
    sum_time_matrix = end_time_matrix - begin_time_matrix
    idList = []
    msgKey, msgValue = self.encID(self.fidKey, self.AESKey, '10000000')

    while key != '0000000000':
      # if num == 64000:
      #     break
      # num = num + 1
      key_ = encAlgo().get_str_sha1_secret_str(key + '0')[:10]
      value_ = self.dataset[key_]
      mask = encAlgo().get_str_sha1_secret_str(key + '1')[:20]
      encValue = encAlgo().x_o_r(mask, value_).zfill(20)[-20:]
      idKey = encValue[-20:-10]
      key = encValue[-10:]
      idValue = self.dataset[idKey]
      if idValue != msgValue:
        id = encAlgo().decrypt_oralce(self.AESKey, idValue)
        idList.append(int(id))
      if len(idList) == file_data:
        break
    return idList, sum_time_matrix


def add_impl(data, wfile):
  wfile.write(f"add to database {data}".encode())


def delete_impl(data, wfile):
  wfile.write(f"delete {data} from database".encode())

def search_impl(data, wfile):
  # print('2')

  wfile.write(f"search_impl".encode('utf-8'))


class RequestHandlerImpl(BaseHTTPRequestHandler):
  # def do_GET(self):
  #
  #   print(self.path)
  #
  #   self.send_response(200)
  #   self.send_header("Content-Type", "text/html; charset=utf-8")
  #   self.end_headers()
  #
  #   self.wfile.write("Hello World\n".encode("utf-8"))

  # self.wfile.write(f"{eval(self.path[1:])}\n".encode("utf-8"))

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
          add_impl(data, self.wfile)

          # parse the received data as JSON
          post_body = json.loads(post_body)
          dataset = post_body[0]

          Matrix = post_body[1]
          for key in Matrix:
            Matrix[key] = np.array(Matrix[key])
          # print(dataset)
          # print(Matrix)
          global GLOBAL_DATASET, GLOBAL_MATRIX
          GLOBAL_DATASET = dataset
          GLOBAL_MATRIX = Matrix


        elif operation == "delete":
          delete_impl(data, self.wfile)


      elif sender == 'data_user':
        response_data = {'message': 'Hello, {}! We have received your messages!'.format(sender)}
        response = json.dumps(response_data).encode()
        self.wfile.write(response)
        if operation == "search":
          matrix = json.loads(post_body)
          for i in range(len(matrix)):
            matrix[i] = np.array(matrix[i])
          # print(type(matrix))
          # print(type(matrix[0]))

          ma = 100
          count = 0
          total_consump = 0.0
          counter = 1
          while count < counter:
            Sumtime_search = 0
            begin_time_search = time.time()
            idList, sum_time_matrix = searchServer(GLOBAL_DATASET, GLOBAL_MATRIX, matrix, ma).search(int(data))
            end_time_search = time.time()
            Sumtime_search += (end_time_search - begin_time_search)
            # print(Sumtime_search)
            total_consump += Sumtime_search
            count += 1

          avg = (total_consump / counter)
          print("avg_search_time:" + str(avg))
          print("matrix_time: "+ str(sum_time_matrix))

          search_impl(data, self.wfile)


if __name__ == '__main__':
  server_address = ("", 8082)

  httpd = HTTPServer(server_address, RequestHandlerImpl)

  httpd.serve_forever()
