#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from time import time
import gl
from string import ascii_lowercase
import codecs
import re
import json
import operator
import random
'''
    usage: python trans2relationmodel.py
    把标注好的文件zhidao_question.txt转变为可以用于训练的数据文件json/zhidao_question_0x.json
    json文件夹下的文件可以放到118上的qa/processed_data/zhidao/目录下，直接用python process_data.py文件处理后，
    输出模型训练关系,主要区别是可以生成db_match_signal.txt文件，这个文件是训练关系模型必须的文件。

'''
reload(sys)
sys.setdefaultencoding('utf8')

class Trans2ModelData:
    def __init__(self):
        self.train_data_list = []
        self.test_data_list = []
        self.relation_dict = {}
        # self.init_test_data()

    def init_test_data(self):
        fq = codecs.open(gl.zhidao_relation_foler + 'zhidao_question_test.txt', 'r', encoding='utf-8')
        contents = [x.strip('\n') for x in fq.readlines()]
        questions = [content.split('\t')[0] for content in contents]
        for idx, line in enumerate(contents):
            self.test_data_list.append(self.format_line(line, idx))
        self.test_data_questions = questions

    def format_line(self, line, idx):
        # transform a line to json
        arr = line.split('\t')
        if len(arr) < 6:
            return
        question = arr[0]
        if not question:
            return None
        subject = arr[2]
        relation = arr[3]
        match_signal = 1 if (arr[5] == '是') else 0
        
        train_dict = {
            'text': question,
            'relation': '意思',
            'match': match_signal,
            'rwt_options': '',
            'domain_name': 'information',
            'slots': {
                'data': [
                    
                ]
            },
            'set_name': '',
            'id': idx,
            'ques_type': 'statement',
            'intent_name': [
                ''
            ],
            'slots_rw': '',
            'weight': 1
        }
        return json.dumps(train_dict)

    def get_train_data(self, fq_file_name):
        self.train_data_list = []
        print 'processing file', fq_file_name
        fq = codecs.open(fq_file_name, 'r', encoding='utf-8')
        doc = ''.join([x for x in fq.readlines()])
        contents = doc.split('==================================================')
        result_contents = []
        for line in contents:
            questions = line.split('\n')
            if not questions or len(questions) < 2:
                continue
            
            flag = False
            negative_ques = []
            for ques in questions:
                if len(ques.split('\t')) == 6 and ques.split('\t')[5] == '是':
                    flag = True
                    positive_ques = ques
                else:
                    negative_ques.append(ques)
                
            if flag:
                result_contents.append(positive_ques)
                random.shuffle(negative_ques)
                result_contents = result_contents + negative_ques[:4]
        for idx, line in enumerate(result_contents):
            r = self.format_line(line, idx)
            if r is not None:
                self.train_data_list.append(r)
        print 'generating ', len(self.train_data_list), 'questions'
        fq.close()

    def save_train_data(self, ft_file_name):
        ft = codecs.open(ft_file_name, 'w', encoding='utf-8')
        for line in self.train_data_list:
            if line:
                ft.write(line + '\n')
        ft.close() 

    def save_test_data(self, ft_file_name):
        ft = codecs.open(ft_file_name, 'w', encoding='utf-8')
        for line in self.test_data_list:
            if line:
                ft.write(line + '\n')
        ft.close()

    def save_relation(self, fr_file_name):
        self.sorted_relations = sorted(self.relation_dict.items(), key=operator.itemgetter(1), reverse=True)
        ft = codecs.open(fr_file_name, 'w', encoding='utf-8')
        for line in self.sorted_relations:
            ft.write(line[0] + '\t' + str(line[1]) + '\n')
        ft.close() 

if __name__ == '__main__':
    t2md = Trans2ModelData()
    for fidx in xrange(0, 7):
        fq_file_name = gl.zhidao_relation_foler + 'zhidao_question_' + str("%02d" % fidx) + '.txt'
        if not os.path.isfile(fq_file_name):
            continue
        t2md.get_train_data(fq_file_name)
        t2md.save_train_data(gl.zhidao_relation_foler + 'json/zhidao_question_' + str("%02d" % fidx) + '.json')
    