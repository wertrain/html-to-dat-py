# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import re
import traceback

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
        #html = unicode(html, 'shift-jis', 'ignore').encode('utf-8')
        soup = BeautifulSoup(html.decode('shift_jisx0213'), 'html.parser')
        number_list = soup.find_all('div', class_='number')
        name_list = soup.find_all('div', class_='name')
        date_list = soup.find_all('div', class_='date')
        message_list = soup.find_all('div', class_='message')
        
        rname = re.compile('<b>(?:<a href="mailto:(.+?)">)?(.*?)(?:</font>|</a>)?</b>')
        rdate = re.compile('<div class="date">(.+?)</div>')
        rbody = re.compile('<div class="message"> (.+?)(</br>)*</div>?')
        responses = []
        for i, number in enumerate(number_list):
            match = rname.search(name_list[i].encode('cp932'))
            mail = match.group(1)
            name = match.group(2)
            match = rdate.search(date_list[i].encode('cp932'))
            date_time_id = match.group(1)
            match = rbody.search(message_list[i].encode('cp932'))
            body = match.group(1)
            responses.append({
               'number': number,
               'mail': mail if mail is not None else '',
               'name': name,
               'date_time_id': date_time_id,
               'body': body,
            })
        return responses

def __perse_thread(html):
    soup = BeautifulSoup(html.decode('shift_jisx0213'), 'html.parser')
    url = ''
    for a in soup.find_all('a'):
        if a.string == u'全部':
            url = a.get('href')
            break
    # 相対パスであった場合、 meta に URL が書いているかチェックする
    if url.startswith('..'):
        metaurl = soup.find('meta', attrs={'property': 'og:url'})
        if metaurl is not None:
            url = metaurl['content']
        else:
            logging.info('not found url: ' + title)
    id = url.split('/')[-2 if (url.rindex('/') == len(url) - 1) else -1]
    return {
        'id': id,
        'title': soup.find('title').string,
        'url': url
    }

def __responses2dat(responses):
    u"""__Perserクラスでパースしたデータを dat の形式にして返す。"""
    if responses is None:
        return ''
    dat = ''
    separator = '<>'
    for response in responses:
        dat += (response['name'] + separator + response['mail'] + separator + response['date_time_id'] + separator + response['body'] + separator + '\n')
    return dat

def perse(html):
    u"""html を突っ込むといい感じに dat にして返してくれる。"""
    try:
        version = check_version(html)
        perser = getattr(__Perser(), 'perse_' + str(check_version(html)))
        return __responses2dat(perser(html))
    except Exception as e: # ざっくりとしすぎたエラー処理
        logging.error(traceback.format_exc())
        return None

def get_thread(html):
    u"""html を突っ込むとスレッド情報を返してくれる。"""
    try:
        return __perse_thread(html)
    except Exception as e: # ざっくりと(ry
        logging.error(traceback.format_exc())
        return None