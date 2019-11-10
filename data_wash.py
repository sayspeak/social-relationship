'''import pandas as pd
from pandas.tseries.offsets import Second
import time
df = pd.read_csv('/Users/apple/PycharmProjects/Apriori/python3-fp-growth-master/课程出勤详情.csv',encoding = 'UTF-8')
df = df.dropna(subset = ['face_area'])
df = df.dropna(subset = ['auto_signed_time'])
df.groupby(['auto_signed_time'])
df = df.sort_values(by = "auto_signed_time" , ascending = True)
df.reset_index(drop = True ,inplace = True)
df = df.set_index('auto_signed_time')
#print(df['2019-03-14 08:00:16':'2019-03-14 09:00:15'][['student_id','attention','face_area','real_name','gender']])


df['auto_signed_time'] = pd.to_datetime(df['auto_signed_time'],format = '%Y-%m-%d %H:%M:%S')
frequency = 1800
time_range = pd.date_range(df['auto_signed_time'][0],df['auto_signed_time'][df.shape[0]-1]+frequency*Second(),freq = '%sS'%frequency)
df = df.set_index('auto_signed_time')
for i in range(0,len(time_range) - 1):
    print(df.loc[time_range[i]:time_range[i+1]-1*Second()]['student_id'])
'''
import pandas as pd
from pandas.tseries.offsets import Second

df = pd.read_csv('/Users/apple/PycharmProjects/Apriori/python3-fp-growth-master/课程出勤详情.csv',encoding = 'UTF-8')
df = df.dropna(subset = ['face_area'])
df = df.dropna(subset = ['auto_signed_time'])
df = df.dropna(subset=['student_id'])
df.groupby(['auto_signed_time'])
df = df.sort_values(by = "auto_signed_time" , ascending = True)
df.reset_index(drop = True ,inplace = True)
df['auto_signed_time'] = pd.to_datetime(df['auto_signed_time'] , format = '%Y-%m-%d %H:%M:%S')
frequency = 300
time_range = pd.date_range(df['auto_signed_time'][0],
                           df['auto_signed_time'][df.shape[0]-1]+frequency*Second(),freq = '%sS'%frequency)
df = df.set_index('auto_signed_time')
for i in range(0,len(time_range) - 1):
    Series = df.loc[time_range[i]:time_range[i+1]-1*Second()]['student_id']
