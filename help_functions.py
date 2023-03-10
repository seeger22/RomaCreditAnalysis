import pandas
import pymysql

def __count_useable_id(id_list):  #判断列表中可用的ID数量
    num=0
    for i in id_list:
        if i.isdigit():
            num+=1
    return num


def __get_data(id_list_flag,id_list,source,test_flag):  #根据用户的要求，从数据库爬数据并返回
    if test_flag:
        host_web = 'bj-cdb-p7kzp41s.sql.tencentcdb.com'  # 服务器信息，测试
        port_num = 61843
        user_id = 'root'
        pswd = 'Roma123o))!@#*)'
        db = 'luoma_kc_sit'
        char = 'utf8'
        use_uni = True

    elif not test_flag:
        host_web = 'bj-cdb-fu5gl04c.sql.tencentcdb.com'  # 服务器信息，生产*
        port_num = 63665
        user_id = 'OperGuest'
        pswd = 'GuestLuoma!@#12'
        db = 'luoma_kc'
        char = 'utf8'
        use_uni = True

    _source_list = __get_sources(host_web,port_num,user_id,pswd,db,char,use_uni,test_flag)  # 这个列表包含所有线索源 e.g.淘金，58，che300
    data=None
    if id_list_flag:
        try:
            id_list = id_list.split(',')
            num=__count_useable_id(id_list)
            if num == 0:
                return None,False
        except Exception as e:
            print(e)
            return None,False
    if not source in _source_list and id_list_flag:
        data = __get_data_by_id(host_web,port_num,user_id,pswd,db,char,use_uni,id_list,test_flag)
        if len(data)==0:
            return None, False
    elif not id_list_flag and source in _source_list:

        data = __DB_access(host_web,port_num,user_id,pswd,db,char,use_uni,source,test_flag)

    elif source in _source_list and id_list_flag:
        data = __get_data_by_id(host_web,port_num,user_id,pswd,db,char,use_uni,id_list,test_flag)
        data = data[data['source'] == source]
        #print('******'+str(len(data))+'******')
        if len(data)==0:
            return None, False

    else:
        return None,False

    return data,True

def __get_tags(data):  #获取dataframe中的列名
    _dic = {}
    _list = data.columns
    #print(_list)
    for i in range(len(_list)):
        _dic.update({_list[i]: i})
    return _dic

def __write_data(path, data_ALL):  #写入数据到excel文件中，测试时候用的
    df = pandas.DataFrame()
    df.to_excel(path)
    writer = pandas.ExcelWriter(path)
    data = pandas.DataFrame(data_ALL).set_index(["id"])
    data.to_excel(writer, sheet_name='test1')
    writer.save()


def __DB_access(host_web,port_num,user_id,pswd,db,char,use_uni,source:str,test_flag:bool):   #从mysql爬数据，传入参数为线索源，返回为pandas.dataframe格式，该线索源的全部数据
    connect_luoma_kc = pymysql.connect(   #默认访问测试库
        host=host_web,
        port=port_num,
        user=user_id, password=pswd,
        database=db,
        charset=char, use_unicode=use_uni)

    if not test_flag:  #非测试
        connect_luoma_kc = pymysql.connect(
            host=host_web,
            port=port_num,
            user=user_id, password=pswd,
            database=db,
            charset=char, use_unicode=use_uni)

    sql = "select * from kc_clues where source="+"'"+source+"'"
    data = pandas.read_sql(sql, con=connect_luoma_kc)
    connect_luoma_kc.close()
    return data

def __get_data_by_id(host_web,port_num,user_id,pswd,db,char,use_uni,_list,test_flag:bool): #传入参数为包含id的列表，返回为pandas.dataframe格式，传入id的全部线索数据
    connect_luoma_kc = pymysql.connect(  #默认测试库
        host=host_web,
        port=port_num,
        user=user_id, password=pswd,
        database=db,
        charset=char, use_unicode=use_uni)

    if not test_flag:    #生产库
        connect_luoma_kc = pymysql.connect(
            host=host_web,
            port=port_num,
            user=user_id, password=pswd,
            database=db,
            charset=char, use_unicode=use_uni)

    sql = "select * from kc_clues where id in ("
    for id in _list[0:-1]:
        if not id.isdigit():
            continue
        sql+=str(id)+','
    sql+=str(_list[-1])+')'

    if len(_list)==1: #只有一个id
        sql="select * from kc_clues where id = "+str(_list[0])
    data=pandas.read_sql(sql, con=connect_luoma_kc)
    connect_luoma_kc.close()
    return data

def __get_sources(host_web,port_num,user_id,pswd,db,char,use_uni,test_flag:bool): #获取全部线索源，返回列表，用来检测接口传入的线索源是否存在
    connect_luoma_kc = pymysql.connect(  #测试库
        host=host_web,
        port=port_num,
        user=user_id, password=pswd,
        database=db,
        charset=char, use_unicode=use_uni)
    if not test_flag:  #生产库
        connect_luoma_kc = pymysql.connect(
            host=host_web,
            port=port_num,
            user=user_id, password=pswd,
            database=db,
            charset=char, use_unicode=use_uni)

    sql='select distinct source from kc_clues'
    data = pandas.read_sql(sql, con=connect_luoma_kc)
    connect_luoma_kc.close()
    return data.values
