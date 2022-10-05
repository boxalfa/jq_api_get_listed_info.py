# -*- coding: utf-8 -*-
# 2022.10.03 coded by yo.
# MIT License
# Python 3.6.8 / centos7.4

import urllib3
import requests
import datetime
import json
import sys
from datetime import datetime as dt


# ---------------------------------------------
# 機能 : 起動したディレクトリでファイルに書き込む。
# 引数1: 出力ファイル名（string型）
# 引数2: 出力文字列（string型）
# 返値 : 無し
# ---------------------------------------------
def func_read_from_file(str_fname):
    str_read = ''
    try:
        with open(str_fname, 'r', encoding = 'utf_8') as fin:
            while True:
                line = fin.readline()
                if not len(line):
                    break
                str_read = str_read + line
        return str_read

    except IOError as e:
        print('Can not Write!!!')
        print(type(e))



# ---------------------------------------------
# 機能 : 起動したディレクトリでファイルに書き込む。
# 引数1: 出力ファイル名（string型）
# 引数2: 出力文字列（string型）
# 返値 : 無し
# ---------------------------------------------
def func_write_to_file(str_fname_output, str_text):
    try:
        with open(str_fname_output, 'w', encoding = 'utf_8') as fout:
            fout.write(str_text)     

    except IOError as e:
        print('Can not Write!!!')
        print(type(e))



# =============================================
# 機能 : 保存してあるIDトークンを使い、銘柄リストを取得し、コード順にソートして保存する。
# 引数 : 無し
# 返値 : 無し
# 備考 : 銘柄リストのファイル名、IDトークンを保存してあるファイル名は適宜変更してください。
# ---------------------------------------------


# 銘柄リスト出力ファイル名
str_fname_output = 'jq_listed_info.csv'

# ＩＤトークン保存ファイル名
str_fname_idtoken = 'jq_idtoken.json'


# ＩＤトークンの読み出し
str_id_json = func_read_from_file(str_fname_idtoken)
dic_idtoken = json.loads(str_id_json)
str_idtoken = dic_idtoken.get('idToken')
# ＩＤトークンを取得できない場合
if str_idtoken is None :
    print('ＩＤトークンが取得できません。')
    quit()

# ＩＤトークンの取得時間を表示
str_time_idtoken = dic_idtoken.get('time_idToken')
time_idtoken = dt.strptime(str_time_idtoken, '%Y-%m-%d %H:%M:%S.%f')
print('id token')
print('time stamp :', time_idtoken)

# ＩＤトークンの有効期限を表示（有効期限24時間）
span_expire = datetime.timedelta(days=1)
time_expire = time_idtoken + span_expire
print('expiry date:', time_expire)
time_remain = time_expire - datetime.datetime.now()
print('remaining time:', time_remain)
if time_remain > datetime.timedelta(days=0) :
    print('IDトークンの有効期間は２４時間です。')
else :
    print('IDトークンは、無効です。有効期間を過ぎました。')
print()



# 銘柄情報取得
idToken = str_idtoken
headers = {'Authorization': 'Bearer {}'.format(idToken)}
req_info = requests.get("https://api.jpx-jquants.com/v1/listed/info", headers=headers)
dic_info = json.loads(req_info.text)    # jsonをパースして辞書型に変換
if req_info.status_code == 200 :
    # 正常に銘柄情報を取得
    list_info = dic_info.get('info')       # "info"のvalueを取り出す。リスト型。
else :
    # info を取得できなかった場合
    # --- Message -----------------------------
    # infoのエラーで、403の場合のmessageは'M'と大文字になっているので注意。
    # エラーは400,401,403と3種類有る
    # 400: 未確認。これは何で起こるのしょう。
    # 401: {"message":"The incoming token has expired"}
    # 403: {"Message":"Access Denied"}
    # -----------------------------------------
    print('status_code:', req_info.status_code)
    if req_info.status_code == 401 :
        print('message    :', dic_info.get('message'))
    elif req_info.status_code == 403 :
        print('message    :', dic_info.get('Message'))
    else :
        print(req_info.text)

    quit()  # 終了


# 銘柄コード順にソート
sorted_list = sorted(list_info, key=lambda x:x['Code'])

# csvで保存
try:
    with open(str_fname_output, 'w', encoding = 'utf_8') as fout:
        print('file open at w, "fout": ', str_fname_output )

        # 1行目 タイトル行
        str_text = ''
        str_text = str_text + '"' + 'Code' + '",'
        str_text = str_text + '"' + 'CompanyName' + '",'
        str_text = str_text + '"' + 'CompanyNameFull' + '",'
        str_text = str_text + '"' + 'CompanyNameEnglish' + '",'
        str_text = str_text + '"' + 'MarketCode' + '",'
        str_text = str_text + '"' + 'SectorCode' + '",'
        str_text = str_text + '"' + 'UpdateDate' + '"\n'
        fout.write(str_text)     

        # データ行
        for i in range(len(sorted_list)):
            str_text = ''
            str_text = str_text + '"' + sorted_list[i].get('Code') + '",'
            str_text = str_text + '"' + sorted_list[i].get('CompanyName') + '",'
            str_text = str_text + '"' + sorted_list[i].get('CompanyNameFull') + '",'
            str_text = str_text + '"' + sorted_list[i].get('CompanyNameEnglish') + '",'
            str_text = str_text + '"' + sorted_list[i].get('MarketCode') + '",'
            str_text = str_text + '"' + sorted_list[i].get('SectorCode') + '",'
            str_text = str_text + '"' + sorted_list[i].get('UpdateDate') + '"\n'
            fout.write(str_text)     

        fout.close
        print('file close: ', str_fname_output)
        print('銘柄数: ', i + 1 )  # 0からカウントしているので1加算       

except IOError as e:
    print('Can not Write!!!')
    print(type(e))
    #print(line)
