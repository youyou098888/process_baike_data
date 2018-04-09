# coding=utf-8
import sys
import os
import gl
import codecs
import time
import re
# import requests
from string import ascii_lowercase
import json
from py2neo import Node, Relationship
from py2neo import Graph
import jieba
# reload(sys)
# sys.setdefaultencoding('utf-8')

def request_data_from_url(url):
    try:
        r = requests.get(url)
        return expand_weighted_data(json.loads(r.text, encoding='utf-8'))
    except Exception as e:
    	print(e)
    	print('failed to get data from %s' % url)
        # exit(1)

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
        # dup = int(row.get('weight', 1))
        # for i in xrange(dup):
        result.append(row)
    return result

fact_word = ['是什么', '什么是', '什么叫', '是谁', '什么人', '谁是', '什么意思']
	
def process_middle_data(data, filter_fact_word=False):
	result = []
	if filter_fact_word:
		for line in data:
			flag = False
			for f in fact_word:
				if f in line['text']:
					flag = True
			if flag:
				result.append(line['text'])
	else:
		for line in data:
			result.append(line['text'])
	return result

def divide_word(text, fr):
	for f in fact_word:
		if f in text:
			arr = text.replace(f, '\t')
			fr.write(arr + '\t' + text + '\n')

def process_slots(item_dict_list):
	noun_list = []
	verb_list = []
	ensemble_list = []
	for idx, item_dict in enumerate(item_dict_list):
		item_dict = json.loads(item_dict)
		if idx % 1000 == 0:
			print('processed %d lines' % idx)
		if not '空调' in item_dict['text']:
			continue
		verb, noun = '', ''
		for slot in item_dict['slots']['data']:
			key = slot[0]
			value = slot[1]
			
			if key == 'operation':
				verb = value
			else:
				noun = value
			verb_list.append(verb)
			noun_list.append(noun)
		for name in ensemble_list:
			if not verb or not noun:
				continue # prevent sub_of itself
			# sub_of relationship
			a1 = graph.find_one(label=domain_label, property_key='name', property_value=noun)
			if not a1:
				a1 = Node(domain_label, name=noun)
			b1 = graph.find_one(label=domain_label, property_key='name', property_value=(verb + noun))
			if not b1:
				b1 = Node(domain_label, name=(verb + noun))
			a1b1 = Relationship(b1, 'sub_of', a1)
			graph.create(a1b1)

			# semantic_of relationship
			a2 = graph.find_one(label=domain_k, property_key='name', property_value=item_dict['text'])
			if not a2:
				a2 = Node(domain_k, name=item_dict['text'])
			b1a2 = Relationship(b1, 'semantic_of', a2)
			graph.create(b1a2)

			# instance_of relationship
			sub_a1_list = jieba.cut(noun)
			for sub_a1_txt in sub_a1_list:
				if sub_a1_txt == noun:
					continue
				sub_a1 = graph.find_one(label=domain_label, property_key='name', property_value=sub_a1_txt)
				if sub_a1:
					a1suba1 = Relationship(a1, 'instance_of', sub_a1)
					graph.create(a1suba1)


		ensemble_list = ensemble_list + [{'s': (verb + noun), 'k': item_dict['text']}, 
										 {'s': (noun + verb), 'k': item_dict['text']}]
	verb_list = list(set(verb_list))
	noun_list = list(set(noun_list))
	ensemble_set = {}
	new_ensemble_list = []
	for item in ensemble_list:
		if item['s'] in ensemble_set:
			continue
		ensemble_set[item['s']] = 1
		new_ensemble_list.append(item)
	# ensemble_list = list(set(ensemble_list))
	return noun_list, verb_list, new_ensemble_list

def write_to_file(target, filename):
	with open(filename, 'w') as f:
		for x in target:
			if type(x) == 'dict':
				f.write(json.loads(x))
			f.write('\n')

graph = Graph(password='123456')	
domain_label = 'semantic_entity'
domain_k = 'knowledge_entity'

if __name__ == '__main__':
	# 从url读取数据
	# url_template = 'http://10.111.128.18:8899/dataset/training_data?params=%s&stg_merge=%s&token=wa_mt_Review_1511748614_7e65e603daaa79921644ae4626ff13bf53eeda1e26c2f7879e83a25e26865c63'
	# manual_url = url_template % ('user_manual', '')
	# middle_data = request_data_from_url(manual_url)
	# fm = codecs.open('user_manual.middle', 'w', encoding='utf-8')
	# for t in middle_data:
	# 	fm.write(json.dumps(t) + '\n')
	# fm.close()
	graph.delete_all()
	fm = codecs.open('user_manual.middle', 'r', encoding='utf-8')
	noun_list, verb_list, ensemble_list = [], [], []
	noun_list, verb_list, ensemble_list = process_slots([x.strip('\n') for x in fm.readlines()])

	# write_to_file(noun_list, 'noun_list.txt')
	# write_to_file(verb_list, 'verb_list.txt')
	# write_to_file(ensemble_list, 'ensemble_list.txt')

	
	
