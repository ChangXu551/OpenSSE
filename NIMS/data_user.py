import requests
import time
import json

import numpy as np
from encAlgo import *
import  time

class genTrapdoor:
  def __init__(self, keyword):
    self.dic = []
    self.dataset = {}
    self.AESKey = '123456'
    self.keywordLength = 22
    self.timeLength = 15
    self.lenCount = self.keywordLength + self.timeLength
    self.m_size = self.lenCount + 3
    self.encMatrix = {}
    self.keyword = keyword

  def initTrapkey(self):
    self.keywordList = self.readDict()
    self.M1 = np.zeros((self.m_size, self.m_size))
    self.M2 = np.zeros((self.m_size, self.m_size))
    for i in range(self.m_size):
      self.M1[i][i] = 1
      self.M2[i][i] = 1
    self.inverse_M1 = np.linalg.pinv(self.M1)

  def readDict(self):  # 读取关键字
    f1 = open('./ID_dict.txt')  # 打开名为matrix1的TXT数据文件
    lines1 = f1.readlines()  # 把全部数据文件读到一个列表lines1中
    List = []
    for line in lines1:  # 把lines1中的数据逐行读出来
      list1 = line.strip('\n')  # 处理逐行数据；strip表示把头尾的'\n'去掉，split表示以空格来分割行数据，然后把处理后的数据返回到list列表中
      List.append(list1)
    self.dic = List
    return List

  def enc(self, X, k1, k2, k3, k4):
    X = np.diag(X)  # 1维数组：形成一个以一维数组为对角线元素的矩阵 二维矩阵：输出矩阵的对角线元素
    first = np.dot(k3, k1)
    second = np.dot(first, X)
    third = np.dot(second, k2)
    return np.dot(third, k4)

  def decID(self, AESKey, text):  # 加密ID
    value = encAlgo().decrypt_oralce(AESKey, text)
    return value

  def trapdoorTrans(self, list):
    for i in range(len(list)):
      if list[i] == '0':
        list[i] = 1
      elif list[i] == '1':
        list[i] = -1
    list.append(-1 * (len(list)))
    return list

  def wildTrans_Range(self, list):
    k = 0
    for i in range(len(list)):
      if list[i] == '0':
        list[i] = 1
        k = k + 1
      elif list[i] == '1':
        list[i] = -1
        k = k + 1
      elif list[i] == '*':
        list[i] = 0
    list.append(-1 * (k))
    return list

  def Serach_Prefix(self, begin, end):
    vec = []
    len1 = len(begin)
    tmp = ['*'] * len1
    k = 0
    for i in range(len1):
      if begin[k] == end[k]:
        tmp[k] = begin[k]
        k = k + 1
      else:
        break
    if k == len1:
      vec.append(begin)
      return vec
    bTrue = 1
    for l in range(len1 - k):
      if (begin[l + k] == '0') & (end[l + k] == '1'):
        1
      else:
        bTrue = 0
    if bTrue == 1:
      vec.append(tmp)
      return vec
    offset = k + 1
    lef = len1 - offset
    nBegin = ['0'] * lef
    nEnd = ['1'] * lef
    Set_prefixA = self.Serach_Prefix(begin[-1 * lef:], nEnd)
    Set_prefixB = self.Serach_Prefix(nBegin, end[-1 * lef:])

    for i in range(len(Set_prefixA)):
      Atmp = []
      Atmp[:k] = tmp[:k]
      Atmp = Atmp + ['0']
      Atmp = Atmp + Set_prefixA[i]
      vec.append(Atmp)
    for i in range(len(Set_prefixB)):
      Atmp = []
      Atmp[:k] = tmp[:k]
      Atmp = Atmp + ['1']
      Atmp = Atmp + Set_prefixB[i]
      vec.append(Atmp)
    return vec

  def genTimeRange(self):

    ts = '2021-1-1 00:00:00'
    # 转为时间数组
    timeArray = time.strptime(ts, "%Y-%m-%d %H:%M:%S")

    initimeStamp = int(time.mktime(timeArray))
    time1 = int(time.time()) - initimeStamp
    time2 = 0

    timeStr1 = bin(time1)[2:].zfill(self.timeLength)  # [2:]是为了去掉0b, bin二进制, oct八进制, hex十六进制
    timeStr2 = bin(time2)[2:].zfill(self.timeLength)

    timeList1 = list(timeStr1)
    timeList2 = list(timeStr2)

    return timeList1, timeList2

  def genTrilMatrix(self):
    A1 = np.random.randint(1, 1000, size=(self.m_size, self.m_size))
    I = np.tril(A1)  # 下三角矩阵
    for i in range(self.m_size):
      I[i][i] = 1
    return I

  def initIndexVector(self, keyword):

    keywordCon = self.keywordList.index(keyword)
    binaryCount = bin(keywordCon)[2:].zfill(self.keywordLength)  # [2:]是为了去掉0b, bin二进制, oct八进制, hex十六进制

    trapdoorCountList = list(binaryCount)
    transTrapdoorVector = self.trapdoorTrans(trapdoorCountList)
    rtransTrapdoorArray = np.array(transTrapdoorVector, dtype=np.float64) * 100002
    rtransTrapdoorVector = rtransTrapdoorArray.tolist()

    timeList1, timeList2 = self.genTimeRange()
    vec = self.Serach_Prefix(timeList2, timeList1)

    trapGen = []
    for i in range(len(vec)):
      timeRangeTrans = self.wildTrans_Range(vec[i])
      rtimeRangeTransArray = np.array(timeRangeTrans, dtype=np.float64) * 100002
      rtimeRangeTransVector = rtimeRangeTransArray.tolist()
      trapdoorVector = rtransTrapdoorVector + rtimeRangeTransVector + [1]
      trapdoorVector = list(map(int, trapdoorVector))

      key_Q = self.genTrilMatrix()
      arrayTrapVector = np.array(trapdoorVector, dtype=np.float64)
      encTrap = self.enc(arrayTrapVector, key_Q, key_Q, self.M1, self.M2)
      trapGen.append(encTrap)
    return trapGen

  def genTrap(self):
    self.initTrapkey()
    matrix = self.initIndexVector(self.keyword)
    return matrix

url = 'http://localhost:8082/data_user/search/20000'

Matrix = genTrapdoor('Subject').genTrap()
for i in range(len(Matrix)):
  Matrix[i] = Matrix[i].tolist()

headers = {'content-type': 'application/json'}
response = requests.post(url, data=json.dumps(Matrix), headers=headers)

# print(response)
if response.status_code == 200:
    print(response.text)
    # response_data = json.loads(response.content)
    # print(f"Received response from server: {response_data['message']}")
else:
    print("Error: server did not respond successfully")