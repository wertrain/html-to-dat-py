# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import re

def check_version(html):
    u"""dt の有無で html の形式を判定する。
    0 は dt/dd の閉じタグがあるもの、1 は dt/dd の閉じタグがないもの。
    2 は そもそも dt/dd の形で書かれていないものになる。
    """
    html = unicode(html, 'shift-jis', 'ignore')
    if html.count('dt') > 0:
            return 0 if html.count('/dt') > 0 else 1
    else:
        return 2

class __Perser:
    u"""バージョンごとのパースを行う。
    正規表現でまとめれば、0と1は同じ処理が可能なので、実質2種類のパースを行う。
    """
    def perse_0(self, html):
        r = re.compile('<dt.*?>([0-9]+).+?(?:"mailto:(.+?)">)?<b>(.*?)</b>(?:</font>|</a>)?(?:.){2}(.+?)(?:</dt>)*(?:<dd>) ?(.*?)<br><br>')
        responses = []
        for line in html.splitlines():
            match = r.search(line)
            if match is not None:
                number = int(match.group(1))
                mail = match.group(2)
                name = match.group(3)
                date_time_id = match.group(4)
                body = match.group(5)
                # 1001以降ではシステムの投稿の可能性がある
                # 同時投稿で1001以上でもユーザーの投稿である場合があるので、変換して失敗するかで判定する
                try:
                    tmp = date_time_id.split(' ')
                    at = datetime.strptime(tmp[0][:10] + ' ' + tmp[1][:11], '%Y/%m/%d %H:%M:%S.%f')
                    id = tmp[2][3:] if len(tmp) > 2 else None
                except:
                    continue
                responses.append({
                    'number': number,
                    'mail': mail if mail is not None else '',
                    'name': name,
                    'date_time_id': date_time_id,
                    'body': body,
                })
        return responses
        
    def perse_1(self, html):
        return self.perse_0(html)
    
    def perse_2(self, html):
        return

def __responses2dat(responses):
    u"""__Perserクラスでパースしたデータをdatの形式にして返す。"""
    if responses is None:
        return
    dat = ''
    separator = '<>'
    for response in responses:
        dat += response['name'] + separator + response['mail'] + separator + response['date_time_id'] + separator + response['body'] + '\n'
    return dat

def perse(html):
    u"""html を突っ込むといい感じに dat にして返してくれる関数"""
    version = check_version(html)
    perser = getattr(__Perser(), 'perse_' + str(check_version(html)))
    #for line in html.splitlines():
    #    print line
    print __responses2dat(perser(html))
