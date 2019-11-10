import csv
import pandas as pd
def get_num(n,path):
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        column1 = [row[n] for row in reader]
        # list()方法是把字符串str或元组转成数组
        List1 = list(set(column1))
        print(len(List1) - 1)
