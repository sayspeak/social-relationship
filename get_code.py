import chardet
#解析文件编码格式
def code(self,path):
    f = open(path, 'rb')
    f_read = f.read()
    f_charInfo = chardet.detect(f_read)
    print(f_charInfo)
    return f_charInfo
if __name__ == '__main__':
    code(self='1',path='/Users/apple/PycharmProjects/Apriori/python3-fp-growth-master/课程出勤详情.csv')