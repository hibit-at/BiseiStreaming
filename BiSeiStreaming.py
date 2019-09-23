import json
import sys
import codecs
from requests_oauthlib import OAuth1Session #OAuthのライブラリの読み込み
from datetime import datetime
import re

CK = ""
CS = ""
AT = ""
ATS = ""
twitter = OAuth1Session(CK, CS, AT, ATS) #認証処理

url = "https://api.twitter.com/1.1/statuses/home_timeline.json" #タイムライン取得エンドポイント
params ={'count' : 50} #取得数
res = twitter.get(url, params = params)

namelist = []
idlist = []

if res.status_code == 200: #正常通信出来た場合
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    timelines = json.loads(res.text) #レスポンスからタイムラインリストを取得
    f = codecs.open('test.json', 'w','utf-8')
    json.dump(timelines, f, ensure_ascii=False)
    counter = 0 #検索ヒット回数の記録
    for line in timelines: #タイムラインリストをループ処理
        
        content = line['text'].translate(non_bmp_map)
        print(line['user']['name'].translate(non_bmp_map) + '::' + content)
        print(line['created_at'])
        print('---------------------------------')

        URL = line['entities']['urls']
        isSelf = line['user']['name'] == 'Bi_Sei_Streaming' #自分自身の発言か？
        isRT = (content.find('RT @')) >= 0 #ただのリツイートか？
        isNoURL = URL == [] #URLを含まないツイートか？
        if isSelf or isRT or isNoURL: #上の3つのどれでもなければ続行
            continue
        URL = URL[0]['expanded_url']
        print (URL)
        if URL.find('twitch.tv')  == -1: #twitchでなければ次ループ
            continue
        pattern = '.*?twitch.tv/([^/]*)'
        repatter = re.compile(pattern)
        tid = repatter.match(URL).group(1)
        print (tid)
        if tid == 'videos': #アーカイブ動画であれば次ループ
            continue
        counter = counter + 1
        idlist.append(tid)
        namelist.append(line['user']['name'].translate(non_bmp_map))
        
else: #正常通信出来なかった場合
    print("Failed: %d" % res.status_code)
    
if counter > 0:
    print('hit' + str(counter))
    print (idlist)
    idlist_unique = list(set(idlist))
    idlist_unique.sort()
    print (idlist_unique)
    
    #URLリストを作成
    cURL = 'http://multitwitch.tv/'
    for ids in idlist_unique:
        cURL = cURL + ids + '/'
    if len(idlist_unique) == 1: #idが一個だけなら複数窓じゃなく純正twitch
        cURL = 'https://www.twitch.tv/' + idlist_unique[0]

    #名前リストを作成
    print (namelist)
    namelist_unique = list(set(namelist))
    namelist_unique.sort()
    print (namelist_unique)
    namestr = ''
    for ids in namelist_unique:
        namestr = namestr + ids + 'さん、'
    namestr = namestr[:-1]
    
    print (cURL) 
    print (namestr)
    
    url = "https://api.twitter.com/1.1/statuses/update.json" #ツイートポストエンドポイント
    params = {"status" : namestr + 'が配信しているかも！' + cURL}
    res = twitter.post(url, params = params) #post送信

else:
    print('no hit')

