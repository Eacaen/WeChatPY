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

import pylibmc as memcache

import sys
reload(sys)
sys.setdefaultencoding('utf8')


def choose_lang(word = 'EN'):
    flag = 0
    if word == '日' or word == 'jp' or word == 'ja':
        flag = 1
        word = 'ja'
    elif word == '英' or word == 'en' or word == 'EN':
        flag = 1
        word == 'EN'
    elif word == '韩' or word == 'ko' :
        flag = 1
        word == 'ko'
    elif word == '法' or  word == 'fr':
        flag = 1
        word = 'fr'
    elif word == '俄' or word == 'ru':
        flag = 1
        word = 'ru'
    elif word == '葡萄牙' or word == 'pt':
        flag = 1
        word = 'pt'
    elif word == '西班牙' or word == 'es' :
        flag = 1
        word = 'es'
    else:
        flag = 0
        word = 'EN'
    return  word , flag

def youdao_translate(q, to_Lang = 'EN' ):
    appKey = '091e7e55b4abf0b9'
    secretKey = 'Kug4XT8Zv11q5baczuc9PLDfWFwcIvlI'

    httpClient = None
    myurl = '/api'

    toLang = to_Lang
    fromLang = 'zh-CHS'
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


def youdao(word , to_Lang = 'EN' ):
    fanyi = youdao_translate(word , to_Lang = to_Lang) 
    fanyi = json.loads(fanyi, encoding='utf-8')

    if fanyi['errorCode'] == u'0':
        prounc = ''
        if 'basic' in fanyi.keys():
            if 'uk-phonetic' in fanyi['basic']:
                prounc = u'英式发音：%s\n'%(fanyi['basic']['uk-phonetic']) 
                
            if 'us-phonetic' in fanyi['basic']:
                prounc = prounc +  u'美式发音：%s\n'%(fanyi['basic']['us-phonetic'])
                
            trans = u'%s:\n%s\n基本翻译:\n%s\n网络释义：\n%s'%(word,''.join(fanyi['translation']),' '.join(fanyi['basic']['explains']),''.join([i+' ; ' for i in fanyi['web'][0]['value'] ]))
            return  prounc + trans
        else:
            trans =u'%s:\n基本翻译:%s\n'%(word,''.join(fanyi['translation']))
            return trans
        
    elif fanyi['errorCode'] == u'103':
        return u'对不起，要翻译的文本过长'
    elif fanyi['errorCode'] == u'102':
        return u'对不起，不支持的语言类型'
    else:
        return u'对不起，您输入的单词%s无法翻译,请检查拼写'% word

language_list =\
'_______________________\n' + \
'| 语言        | 代码     \n' +\
'| 中文        | zh-CHS \n'+\
'| 日文        | ja          \n'+\
'| 英文        | EN        \n'+\
'| 韩文        | ko         \n'+\
'| 法文        | fr           \n'+\
'| 俄文        | ru         \n'+\
'| 葡萄牙文| pt          \n'+\
'| 西班牙文| es          \n'+\
'_______________________\n' 

language_dir = {'ja':'日文' ,'EN':'英文','ja':'日文','ko':'韩文','fr':'法文','ru':'俄文','pt':'葡萄牙文' ,'es' : '西班牙文'  }

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

        mc = memcache.Client()
        # mc = memcache.Client()
        change_language = 0

        language_chosen = mc.get( fromUser+'_language_chosen'  )
        mc.set(fromUser+'_language_chosen' , language_chosen)

        end_hour = time.localtime( time.time() ).tm_hour
        end_min = time.localtime( time.time() ).tm_min
        end_sec = time.localtime( time.time() ).tm_sec

        if msgType == 'text':
            replayText_list = [ ]
            pic_list = [ 'https://github.com/Eacaen/WeChatPY/blob/master/language.png']
            content=xml.find("Content").text
            if content == 'help':
                replayText = u'''1.输入语言代码进入中文互译（默认英语）\n2.输入m随机来首音乐听，建议在wifi下听\n'''
                return self.render.reply_text(fromUser,toUser,int(time.time()),replayText + language_list)
            
            if content == 'm':
                music_list =[
                [u'http://music.163.com/#/song?id=27534134', u'老司机带带我', u'云南山歌']
                ]
                musicTitle = music_list[0][1]
                musicDes = music_list[0][2]
                musicURL = music_list[0][0]
                return self.render.reply_music(fromUser,toUser,int(time.time()) ,musicTitle,musicDes,musicURL)

            if content in language_dir.keys() :
                language_chosen , change_language = choose_lang(content)
                mc.set(fromUser+'_language_chosen' ,language_chosen )

            if change_language == 1:
                change_language = 0

                mc.set(fromUser+'_TIME_S' , '1')
                start_hour = time.localtime( time.time() ).tm_hour
                start_min = time.localtime( time.time() ).tm_min
                start_sec = time.localtime( time.time() ).tm_sec

                mc.set(fromUser + '_start_min' , start_min )

                replayText = u'进入<' + language_dir[language_chosen] + u'>翻译环境\n' +\
                str(start_hour)+':'+str(start_min)+':'+str(start_sec)+'\n' + \
                u'\n输入 EXIT 退出翻译 ; 2分钟自动退出\n'
                return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)

        if language_chosen != 'EN' and mc.get(fromUser+'_TIME_S'):
            if content == 'EXIT' or  end_min - int ( mc.get(fromUser + '_start_min' ) ) > 2 :
                replayText = u'退出< '+ language_dir[language_chosen] + u' >翻译环境\n' +\
                str(end_hour)+':'+str(end_min)+':'+str(end_sec)+'\n' 
                language_chosen = 'EN'
                mc.set(fromUser+'_language_chosen' ,language_chosen )

                mc.delete(fromUser+'_TIME_S')

                return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)

        if type(content).__name__ == "unicode":
            content = content.encode('UTF-8')
        
        language_chosen = mc.get( fromUser+'_language_chosen'  )
        #默认英语环境
        Nword = youdao(content , to_Lang = language_chosen ) 
        return self.render.reply_text(fromUser,toUser,int(time.time()),Nword)