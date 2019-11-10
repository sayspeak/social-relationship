import os
import codecs
def convert(file_name,file, in_code="GB2312", out_code="UTF-8"):
    """
    该程序用于将目录下的文件从指定格式转换到指定格式，默认的是GBK转到UTF-8
    :param file:    文件路径
    :param in_code:  输入文件格式
    :param out_code: 输出文件格式
    :return:
    """
    out_path='输出文件路径'
    try:
        with codecs.open(file_name, 'r', in_code) as f_in:
            new_content = f_in.read()
            f_out = codecs.open(os.path.join(out_path,file), 'w', out_code)
            f_out.write(new_content)
            f_out.close
    except IOError as err:
        print("I/O error: {0}".format(err))
if __name__ == '__main__':
    convert('课程出勤详情.csv','/Users/apple/PycharmProjects/Apriori/python3-fp-growth-master/课程出勤详情.csv')