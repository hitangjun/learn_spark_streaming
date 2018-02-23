#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'John Tang'

import os, re, time, base64, hashlib, logging

import markdown2

from transwarp.web import get, post, ctx, view, interceptor, seeother, notfound

from apis import api, Page, APIError, APIValueError, APIPermissionError, APIResourceNotFoundError
from config import configs

import requests
import sys
import tushare as ts
import json

def df2Json(df):
    columns = [str(e).replace('\'','').replace('u','') for e in df.columns]

    data_list = []
    for x in df.index:
        tmp_list = []
        for y in df.columns:
            tmp = df[y][x]
            tmp_list.append(str(tmp).decode('utf-8'))
        data_list.append(tmp_list)
    data_list_str = str(data_list).replace('u\'','\'')

    data_list_str = data_list_str.decode("unicode-escape")

    retdata = dict(data=data_list_str,category=columns)
    retdata= json.dumps(retdata,ensure_ascii=False)
    return retdata

def df2DictList(df,need_decode=False):
    data_list = []
    for x in df.index:
        tmp_dict = {}
        for y in df.columns:
            tmp = df[y][x]
            if need_decode:
                tmp_dict[y] = (str(tmp).decode('utf-8'))
            else:
                tmp_dict[y] = tmp
        data_list.append(tmp_dict)
    return data_list

@view('stock/stock.html')
@get('/api/stock')
def show_stock_home():
    df= ts.get_today_all()
    market_stock = df2DictList(df)
    """大盘股票数据"""
    return dict(list=market_stock)

@view('stock/index.html')
@get('/api/stats')
def show_stats_home():
    """大盘指数"""
    df= ts.get_index()
    market_index = df2DictList(df,True)

    """自选股数据"""
    df= ts.get_realtime_quotes(['000002','300122','002230','300166','603189','000005'])
    self_stock = df2DictList(df)

    """新闻数据"""
    df = ts.get_latest_news()
    news = df2DictList(df)

    """电影票房"""
    df = ts.realtime_boxoffice()
    boxoffice = df2DictList(df)
    return dict(market_index=market_index,self_stock=self_stock,news=news,boxoffice=boxoffice)

@view('stock/news.html')
@get('/api/stocknews')
def show_news():
    """新闻数据"""
    df = ts.get_latest_news(top=20,show_content=True)
    news = df2DictList(df)
    return dict(news=news)

@view('stock/charts.html')
@get('/api/chart/:stock_code')
def show_charts(stock_code):
    return ts_hist_data(stock_code)

@api
@get('/api/stock/today/:stock_code')
def show_today_charts(stock_code):
    return get_today_ticks(stock_code)

@api
@get('/api/stock/real/:stock_code')
def show_real_charts(stock_code):
    return get_today_realtime_price(stock_code)

def ts_hist_data(stock_code):
    """
    历史行情K线图
    """
    #r = requests.get()
    if not stock_code:
        stock_code = '300122'
    df = ts.get_hist_data(stock_code,start='2015-01-01') #一次性获取全部日k线数据
    # df = df.sort_index(axis=1,ascending=True)
    df = df.T

    columns = df.columns.tolist()
    columns.reverse()

    '''
    修改字符集
    '''
    reload(sys)
    sys.setdefaultencoding('utf-8')

    category = [str(x).replace('\'','').replace('u','') for x in columns]

    data_list = []
    for x in category:
        tmp = df[x]
        tmp_list = [tmp['open'],tmp['close'],tmp['low'],tmp['high']]
        ele_list = [float(e) for e in tmp_list]
        data_list.append(ele_list)

    today,today_data_frame=get_realtime_quotes([stock_code])

    today_data_frame = today_data_frame.T
    today_data = today_data_frame[stock_code]
    category.append(str(today_data['date']).replace('u',''))

    data_list.append([float(str(x).replace('\'','').replace('u',''))
                      for x in
                      [today_data['open'],today_data['price'],today_data['low'],today_data['high']]]);

    retdata = dict(category=category,data=data_list,today=today)
    return retdata
'''
    indexL =  df.index.values.tolist()
    indexL.reverse() #列表反转
    category = [str(x).replace('\'','').replace('u','') for x in indexL]

    value_str = df.to_json(orient='values').replace('[[','[').replace(']]',']')
    target_list = [str(x).replace('[','').replace(']','') for x in value_str.split('],')]
    data_list = []
    for x in target_list:
        tmpList = [float(y) for y in x.split(",")]
        data_list.append(tmpList)
    data_list.reverse() #列表反转
'''
    # for i,ele in enumerate(data_list):
    #     ele.insert(0,category[i])


''
def get_realtime_quotes(stock_code_list):
    """
    实时行情
    """
    if not stock_code_list:
        stock_code_list = ['300122','000005']
    ret_df = ts.get_realtime_quotes(stock_code_list)

    df = ret_df.set_index('code')
    columns = [str(e).replace('\'','').replace('u','') for e in df.columns]

    data_list = []
    # print sys.stdin.encoding
    # reload(sys)
    # sys.setdefaultencoding('utf-8')

    for x in stock_code_list:
        tmp_list = []
        for y in df.columns:
            tmp = df[y][x]#.decode('utf-8')
            tmp_list.append(tmp)
        data_list.append(tmp_list)
    data_list_str = str(data_list).replace('u\'','\'')

    '''
    json解析中文处理
    '''
    data_list_str = data_list_str.decode("unicode-escape")

    retdata = dict(stock_code_list=stock_code_list,columns=columns,data=data_list_str)
    retdata= json.dumps(retdata,ensure_ascii=False)

    return retdata,df

def get_today_ticks(stock_code):
    """获取当日分笔明细数据"""
    df = ts.get_today_ticks(stock_code)

    # df = df.head(10)
    time_list = df['time'].tolist()
    time_list.reverse()

    price_list = [float(x) for x in df['price'].tolist()]
    price_list.reverse()
    return dict(time_list=time_list,price_list=price_list)

def get_today_realtime_price(stock_code):
    """实时价格"""
    ret_df = ts.get_realtime_quotes(stock_code)

    df = ret_df.set_index('code')

    price = df['price'][0]
    time = df['time'][0]
    # data_list = []
    # tmp_list = []
    # for y in df.columns:
    #     tmp = df[y][stock_code]
    #     tmp_list.append(tmp)
    # print tmp_list
    # data_list.append(tmp_list)
    # data_list_str = str(data_list).replace('u\'','\'')
    # data_list_str = data_list_str.decode("unicode-escape")
    # retdata = dict(stock_code_list=stock_code_list,columns=columns,data=data_list_str)
    # retdata= json.dumps(retdata,ensure_ascii=False)

    return dict(time=time,price=price)

def get_today_all():
    """获取单日电影票房数据"""
    df = ts.day_boxoffice()
    print df


from sdk.weibo_simple_sdk import Client

def to_chinese(unicode_str):
    x = json.loads('{"chinese":"%s"}' % unicode_str)
    return x['chinese']

@api
@get('/api/weibo/statuses/:since_id')
def statuses(since_id):
    """获取微博数据流"""
    API_KEY = ''            # app key
    API_SECRET = ''      # app secret
    REDIRECT_URI = 'http://hitangjun.com'
    WEIBO_USERNAME = ''
    WEIBO_PASSWORD = ''
    c = Client(API_KEY, API_SECRET, REDIRECT_URI,
               username=WEIBO_USERNAME, password=WEIBO_PASSWORD)

    """
    since_id 	若指定此参数，则返回ID比since_id大的微博（即比since_id时间晚的微博），默认为0。
    max_id	 若指定此参数，则返回ID小于或等于max_id的微博，默认为0。
    count 	单页返回的记录条数，最大不超过100，默认为20。
    page	 返回结果的页码，默认为1。
    feature 	过滤类型ID，0：全部、1：原创、2：图片、3：视频、4：音乐，默认为0。
    trim_user 	返回值中user字段开关，0：返回完整user字段、1：user字段仅返回user_id，默认为0。
    """
    statuses = c.get('statuses/home_timeline',since_id=since_id,
                     max_id=0,count=20)
    # statuses = str(statuses).decode("utf-8")
    return statuses

def test():
    df = ts.get_h_data('000001')
    df.to_csv('d:/000001.csv',columns=['open','close','high','low','turnover','volume','ma5','ma10','ma20','v_ma5','v_ma10','v_ma20'])

if __name__=='__main__':
    import doctest
    test()
    doctest.testmod()
