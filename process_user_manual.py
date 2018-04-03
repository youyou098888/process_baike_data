# coding=utf-8
import sys
import os
import gl
import codecs
import time
import re
import requests
from string import ascii_lowercase
import json
reload(sys)
sys.setdefaultencoding('utf-8')

def request_data_from_url(url):
    try:
        r = requests.get(url)
        return expand_weighted_data(json.loads(r.text, encoding='utf-8'))
    except Exception as e:
    	print e
        print 'failed to get data from ', url
        exit(1)

def post_data(url, text):
	payload = json.dump({
			"query": text,
			"property" : "<blank> <blank>"
		})
	headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
	r = requests.post(url, data=payload, headers=headers)
	return r

def expand_weighted_data(data):
    result = []
    for row in data:
        dup = int(row.get('weight', 1))
        for i in xrange(dup):
            result.append(row)
    return result

def filter_fact_word(data):
	fact_word = ['是什么', '什么是', '什么叫', '是谁', '什么人', '谁是', '什么意思']
	result = []
	for line in data:
		flag = False
		for f in fact_word:
			if f in line['text']:
				flag = True
		if flag:
			result.append(line['text'])
	return result


if __name__ == '__main__':
	url_template = 'http://10.111.128.18:8899/dataset/training_data?params=%s&stg_merge=%s&token=wa_mt_Review_1511748614_7e65e603daaa79921644ae4626ff13bf53eeda1e26c2f7879e83a25e26865c63'
	manual_url = url_template % ('user_manual', '')
	middle_data = request_data_from_url(manual_url)
	data = filter_fact_word(middle_data)
	final_result = []
	for text in data:
		request_txt = ' '.join(jieba.cut(text, cut_all=True))
		url = 'http://127.0.0.1:12090/joint'
		r = post_data(url, request_txt)
		final_result.append(r)
	for r in final_result:
		print r
	print len(final_result)
	
