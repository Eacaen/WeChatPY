# -*- coding: utf-8 -*-
import hashlib
import web
import lxml
import time
import os
import urllib2,json
from lxml import etree


import httplib
import md5
import urllib
import random
import json

import sys
reload(sys)
sys.setdefaultencoding('utf8')

def youdao_translate(q):
    appKey = '091e7e55b4abf0b9'
    secretKey = 'Kug4XT8Zv11q5baczuc9PLDfWFwcIvlI'

    httpClient = None
    myurl = '/api'

    fromLang = 'EN'
    toLang = 'zh-CHS'
    salt = random.randint(1, 65536)

    sign = appKey+q+str(salt)+secretKey
    m1 = md5.new()
    m1.update(sign)
    sign = m1.hexdigest()
    myurl = myurl+'?appKey='+appKey+'&q='+urllib.quote(q)+'&from='+fromLang+'&to='+toLang+'&salt='+str(salt)+'&sign='+sign
 
    try:
        httpClient = httplib.HTTPConnection('openapi.youdao.com')
        httpClient.request('GET', myurl)
 
        #response是HTTPResponse对象
        response = httpClient.getresponse()
        return response.read()
    except Exception, e:
        return e
    finally:
        if httpClient:
            httpClient.close()


def youdao(word):
    fanyi = youdao_translate(word) 
    fanyi = json.loads(fanyi, encoding='utf-8')

    if fanyi['errorCode'] == u'0':
        prounc = ''
        if 'basic' in fanyi.keys():
            if 'uk-phonetic' in fanyi['basic']:
                prounc = u'英式发音：%s\n'%(fanyi['basic']['uk-phonetic']) 
                
            if 'us-phonetic' in fanyi['basic']:
                prounc = prounc +  u'美式发音：%s\n'%(fanyi['basic']['us-phonetic'])
                
            trans = u'%s:\n%s\n基本翻译:\n%s\n网络释义：\n%s'%(fanyi['query'],''.join(fanyi['translation']),' '.join(fanyi['basic']['explains']),''.join([i+' ; ' for i in fanyi['web'][0]['value'] ]))
            return  prounc + trans
        else:
            trans =u'%s:\n基本翻译:%s\n'%(fanyi['query'],''.join(fanyi['translation']))
            return trans
        
    elif fanyi['errorCode'] == u'103':
        return u'对不起，要翻译的文本过长'
    elif fanyi['errorCode'] == u'102':
        return u'对不起，不支持的语言类型'
    else:
        return u'对不起，您输入的单词%s无法翻译,请检查拼写'% word



class WeixinInterface:

    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root, 'templates')
        self.render = web.template.render(self.templates_root)

    def GET(self):
        #获取输入参数
        data = web.input()
        signature=data.signature
        timestamp=data.timestamp
        nonce=data.nonce
        echostr=data.echostr
        #自己的token
        token="yangyanxing" #这里改写你在微信公众平台里输入的token
        #字典序排序
        list=[token,timestamp,nonce]
        list.sort()
        sha1=hashlib.sha1()
        map(sha1.update,list)
        hashcode=sha1.hexdigest()
        #sha1加密算法        

        #如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            return echostr

    def POST(self):        
        str_xml = web.data() #获得post来的数据
        xml = etree.fromstring(str_xml)#进行XML解析
        content=xml.find("Content").text#获得用户所输入的内容
        msgType=xml.find("MsgType").text
        fromUser=xml.find("FromUserName").text
        toUser=xml.find("ToUserName").text

        if msgType == 'text':
            replayText_list = [ ]
            content=xml.find("Content").text
            if content == 'help':
                replayText = u'''1.输入中文或者英文返回对应的翻译\n2.输入m随机来首音乐听，建议在wifi下听\n'''
                replayText_list.append(replayText)
                return self.render.reply_pictxt(fromUser,toUser,int(time.time()),replayText_list , , 1)
                # return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
            
            if content == 'm':
                music_list =[
                [u'http://music.163.com/#/song?id=27534134', u'老司机带带我', u'云南山歌']
                ]

                musicTitle = music_list[0][1]
                musicDes = music_list[0][2]
                musicURL = music_list[0][0]
                return self.render.reply_music(fromUser,toUser,int(time.time()) ,musicTitle,musicDes,musicURL)


        if msgType == "event":
            mscontent = xml.find("Event").text
            if mscontent == "subscribe":
                replayText = u'''欢迎关注本微信， 输入help查看帮助文档'''
                return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
            if mscontent == "unsubscribe":
                replayText = u' see you '
                return self.render.reply_event(fromUser,toUser,int(time.time()),replayText)
    
        if type(content).__name__ == "unicode":
            content = content.encode('UTF-8')
        Nword = youdao(content)        
        return self.render.reply_text(fromUser,toUser,int(time.time()),Nword)
 