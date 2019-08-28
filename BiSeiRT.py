import json #標準のjsonモジュール
import sys
import codecs
from requests_oauthlib import OAuth1Session #OAuthのライブラリの読み込み
from datetime import datetime
from time import sleep

CK = ""
CS = ""
AT = ""
ATS = ""
twitter = OAuth1Session(CK, CS, AT, ATS) #認証処理

url = "https://api.twitter.com/1.1/statuses/home_timeline.json" #タイムライン取得エンドポイント
params ={'count' : 600, 'tweet_mode' : 'extended'} #取得数
res = twitter.get(url, params = params)

if res.status_code == 200: #正常通信出来た場合
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    timelines = json.loads(res.text) #レスポンスからタイムラインリストを取得
    f = codecs.open('test.json', 'w','utf-8')
    json.dump(timelines, f, ensure_ascii=False)
    counter = 0 #検索ヒット回数の記録
    for line in timelines: #タイムラインリストをループ処理
        content = line['full_text'].translate(non_bmp_map)
        print(line['user']['name'].translate(non_bmp_map) + '::' + content)
        print(line['created_at'])
        print('---------------------------------')
        if line['user']['name'] != 'Bi_Sei_Streaming': #自分自身のつぶやきを除外
            tag1 = content.find('#BeatSaber') > 0
            tag2 = content.find('#Beatsaber') > 0
            tag3 = content.find('#beatsaber') > 0
            if tag1 or tag2 or tag3:
                counter = counter + 1
                print ('HIT ' + line['id_str'] + '\n')
                url = 'https://api.twitter.com/1.1/statuses/retweet/' + line['id_str'] + '.json'
                res = twitter.post(url, params = params) #post送信                 
else: #正常通信出来なかった場合
    print("Failed: %d" % res.status_code)

if counter > 0:
    print('hit' + str(counter))
else:
    print('no hit')
