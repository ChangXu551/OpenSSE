import numpy as np
from encAlgo import *
import  time
import random
import copy
np.set_printoptions(suppress=True)
np.set_printoptions(precision=3)
import multiprocessing

class genIndex:
    def __init__(self, ma):
        self.dic = []
        self.dataset = {}
        self.AESKey = '123456'
        self.fidKey = 'password'
        self.keywordLength = 22
        self.timeLength = 15
        self.lenCount = self.keywordLength + self.timeLength
        self.m_size = self.lenCount +3
        self.encMatrix = {}
        self.ma = ma

    def initKey(self):
        self.keywordList = self.readDict()
        self.M1 = np.zeros((self.m_size, self.m_size))
        self.M2 = np.zeros((self.m_size, self.m_size))
        for i in range(self.m_size):
            self.M1[i][i] = 1
            self.M2[i][i] = 1
        self.inverse_M1 = np.linalg.pinv(self.M1)
        self.inverse_M2 = np.linalg.pinv(self.M2)

    def readDict(self):  #读取关键字
        f1 = open('./ID_dict.txt')  # 打开名为matrix1的TXT数据文件
        lines1 = f1.readlines()  # 把全部数据文件读到一个列表lines1中
        List = []
        for line in lines1:  # 把lines1中的数据逐行读出来
            list1 = line.strip('\n')  # 处理逐行数据；strip表示把头尾的'\n'去掉，split表示以空格来分割行数据，然后把处理后的数据返回到list列表中
            List.append(list1)
        self.dic = List
        return List

    def encID(self, fidKey, AESKey, count):   #加密ID
        value = encAlgo().encrypt_oracle(AESKey, count)
        key = encAlgo().F2(fidKey, count)[-10:]
        return key,value

    def indexTrans(self, list1): #转换为二进制向量
        for i in range(len(list1)):
            if list1[i] == '0':
                list1[i] = 1
            elif list1[i] == '1':
                list1[i] = -1
        list1.append(1)
        return list1


    def genTrilMatrix(self): #生成下三角随机矩阵
        A1 = np.random.randint(1, 100, size=(self.m_size, self.m_size)) #矩阵元素的大小
        I = np.tril(A1)  # 下三角矩阵
        for i in range(self.m_size):
            I[i][i] = 1
        return I

    def enc(self, X, k1, k2, k3, k4):  #矩阵乘法
        X = np.diag(X)  # 1维数组：形成一个以一维数组为对角线元素的矩阵 二维矩阵：输出矩阵的对角线元素
        first = np.dot(k3, k1)
        second = np.dot(first, X)
        third = np.dot(second, k2)
        return np.dot(third, k4)

    def initIndexVector(self, keyword, r, timeList):  #索引key使用矩阵加密

        keywordCon = self.keywordList.index(keyword)
        binaryCount = bin(keywordCon)[2:].zfill(self.keywordLength)  # [2:]是为了去掉0b, bin二进制, oct八进制, hex十六进制

        indexCountList = list(binaryCount)
        transIndexvecotr = self.indexTrans(indexCountList)
        rtransIndexArray = np.array(transIndexvecotr, dtype=np.float64) * 100000  #随机数大小
        Indexvector = rtransIndexArray.tolist()

        timeList1 = copy.deepcopy(timeList)
        transTimeVecotr = self.indexTrans(timeList1)
        rtimeStampArray = np.array(transTimeVecotr, dtype=np.float64) * 100000   #随机数大小
        rtimevector = rtimeStampArray.tolist()


        indexVector = Indexvector + rtimevector + [r]  #三个元素拼接

        indexVector = list(map(int, indexVector))

        key_I = self.genTrilMatrix()
        arrayIndexVector = np.array(indexVector, dtype=np.float64)
        encIndex = self.enc(arrayIndexVector, key_I, key_I, self.M1, self.M2)  #是用矩阵加密
        return encIndex



    def chain(self, universal_dict, number_folder ,ctr):  #生成链
        Dw = {}
        self.readDict()

        msgKey, msgValue = self.encID(self.fidKey, self.AESKey, '10000000')   #msg的大小要根据文件总数调节
        self.dataset[msgKey] = msgValue

        if ctr == 1:
            for i in universal_dict:
                Dw[i] = '0000000000'    #初始key
        else:
            for i in universal_dict:
                enc = encAlgo().F1(str(ctr), i)[:10]    #先生成上一次更新的Dw
                Dw[i] = str(int(enc, 16) % 10000000000).zfill(10)
        for keyword in universal_dict:
            for i in range(10000):
                count = universal_dict[keyword][number_folder + i]


                idKey, idValue = self.encID(self.fidKey, self.AESKey, count)  # 将文件id加密
                self.dataset[idKey] = idValue

                r = random.getrandbits(32)
                str_r = str(r).zfill(10)
                key_ = encAlgo().get_str_sha1_secret_str(str_r + '0')[:10]
                mask = encAlgo().get_str_sha1_secret_str(str_r + '1')[:20]
                rPrev = Dw[keyword]
                value = idKey + rPrev
                encValue = encAlgo().x_o_r(mask, value).zfill(20)[-20:]
                self.dataset[key_] = encValue
                Dw[keyword] = str_r

        ctr = ctr + 1

        time1 = ctr * 36

        timeStr = bin(time1)[2:].zfill(self.timeLength)  # [2:]是为了去掉0b, bin二进制, oct八进制, hex十六进制
        timeList = list(timeStr)

        for i in universal_dict:
            rPrev = Dw[i]
            enc = encAlgo().F1(str(ctr), i)[:10]  # 32位密文取前10位
            str_r = str(int(enc, 16) % 10000000000).zfill(10)
            key_ = encAlgo().get_str_sha1_secret_str(str_r + '0')[:10]
            mask = encAlgo().get_str_sha1_secret_str(str_r + '1')[:20]

            value = msgKey + rPrev  # 将id加密值和上一个索引拼接
            encValue = encAlgo().x_o_r(mask, value).zfill(20)[-20:]  # 求异或值
            self.dataset[key_] = encValue
            Dw[i] = str_r
            matrix = self.initIndexVector(i, Dw[i], timeList)  # 将每个关键字对应的key使用矩阵加密发送给服务器
            self.encMatrix[i] = matrix

    def test2(self):
        _processes = []
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        for index in range(10):
            _process = multiprocessing.Process(target=self.long_running_function, args=(index, return_dict))
            _process.start()
            _processes.append(_process)
        for _process in _processes:
            _process.join()
        self.encMatrix = {**self.encMatrix, **return_dict}
        # pool = mp.Pool(mp.cpu_count())
        # pool.map(self.long_running_function, [i for i in self.encMatrix.keys()])
        # pool.close()

    def long_running_function(self, t, return_dict):
        timeList = ['0' for _ in range(self.timeLength)]
        mydict = {}
        t = t * self.ma
        for i in range(self.ma):
            m = t + i
            matrix = self.initIndexVector(str(m), '12312412412', timeList)  # 将每个关键字对应的key使用矩阵加密发送给服务器
            return_dict[str(m)] = matrix

                # if (tril > 0):
                #     key = str(int(tril)).zfill(10)
                #     return key
            # print(m)


    def Index(self, universal_dict, file_data):  #这个是运行的总出口~~
        self.initKey()
        i = 0
        ctr = 1
        while i < file_data:
            self.chain(universal_dict, i, ctr)
            ctr = ctr + 1
            i = i + 10000

        time1 = ctr * 36

        timeStr = bin(time1)[2:].zfill(self.timeLength)  # [2:]是为了去掉0b, bin二进制, oct八进制, hex十六进制
        timeList = list(timeStr)
        begin_time_process = time.time()
        self.test2()
        end_time_process = time.time()
        print("time_gen_matrix", end_time_process - begin_time_process)

        # for i in self.dic:
        #     if i != 'Subject':
        #         matrix = self.initIndexVector(i, '12312412412', timeList)  # 将每个关键字对应的key使用矩阵加密发送给服务器
        #         self.encMatrix[i] = matrix

        return self.dataset, self.encMatrix

def gen_index(data):
  # maL = [i for i in range(100, 1100, 100)]
  maL = [100]
  file_data_arr = [10000]
  for ma in maL:
    for file_data in file_data_arr:
      counter = 1

      filename = "inverted_index_" + str(file_data) + ".txt"
      universal_dict = {}
      with open(filename, "r") as f:
        for line in f:
          values = line.split(" ")
          universal_dict[values[0]] = []
          for i in values[1:len(values)]:
            universal_dict[values[0]].append(i)  # 所有的关键字对应文件
      count = 0
      total_consump = 0.0
      while count < counter:
        Sumtime_index = 0

        begin_time_index = time.time()

        dataset, Matrix = genIndex(ma).Index(universal_dict, file_data)

        end_time_index = time.time()
        Sumtime_index += (end_time_index - begin_time_index)
        total_consump += Sumtime_index
        count += 1

      avg = (total_consump / counter)
      print("avg_index_time:" + str(avg))
    return dataset, Matrix

if __name__=='__main__':
    # maL = [i for i in range(100, 1100, 100)]
    maL = [100]
    file_data_arr = [10000]
    # maL = [i for i in range(100, 200, 100)]
    for ma in maL:
        for file_data in file_data_arr:
            counter = 1

            filename = "inverted_index_" + str(file_data) + ".txt"
            universal_dict = {}
            with open(filename, "r") as f:
                for line in f:
                    values = line.split(" ")
                    universal_dict[values[0]] = []
                    for i in values[1:len(values)]:
                        universal_dict[values[0]].append(i)  # 所有的关键字对应文件
            count = 0
            total_consump = 0.0
            while count < counter:
                Sumtime_index = 0

                begin_time_index = time.time()

                dataset, Matrix = genIndex(ma).Index(universal_dict, file_data)

                end_time_index = time.time()
                Sumtime_index += (end_time_index - begin_time_index)
                total_consump += Sumtime_index
                count += 1

            avg = (total_consump / counter)
            print("avg_index_time:" + str(avg))