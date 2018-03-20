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
'''
    usage: python trans2model.py
    把标注好的文件zhidao_question.txt转变为可以用于训练的数据文件json/zhidao_question_0x.json
    同时会生成关系文件zhidao_question.relation
    此文件可以放到processed_data目录下，直接用process_data.py文件处理后，输出模型训练

'''
reload(sys)
sys.setdefaultencoding('utf8')

class Trans2ModelData:
    def __init__(self):
        self.train_data_list = []
        self.relation_dict = {}

    def format_line(self, line, idx):
        # transform a line to json
        arr = line.split('\t')
        if len(arr) < 4:
            return
        question = arr[0]
        subject = arr[1]
        relation = arr[2]
        q_word = arr[3]
        subject_index = -1
        relation_index = -1
        q_word_index = -1
        try:
            subject_index = question.index(subject)
            relation_index = question.index(relation)
            q_word_index = question.index(q_word)
        except:
            pass
        train_dict = {
            'text': question,
            'rwt_options': '',
            'domain_name': 'information',
            'slots': {
                'data': [
                    [
                        'subject',
                        subject,
                        '',
                        subject_index
                    ],
                    [
                        'q_word',
                        q_word,
                        '',
                        q_word_index
                    ]
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
        if relation_index != -1:
            train_dict['slots']['data'].append([
                'relation',
                relation,
                '',
                relation_index
            ])
            if relation != '':
                try:
                    self.relation_dict[relation] += 1
                except:
                    self.relation_dict[relation] = 1
        return json.dumps(train_dict)

    def get_train_data(self, fq_file_name):
        self.train_data_list = []
        print 'processing file', fq_file_name
        fq = codecs.open(fq_file_name, 'r', encoding='utf-8')
        contents = [x.strip('\n') for x in fq.readlines()]
        for idx, line in enumerate(contents):
            self.train_data_list.append(self.format_line(line, idx))
        print 'generating ', len(self.train_data_list), 'questions'
        fq.close()

    def save_train_data(self, ft_file_name):
        ft = codecs.open(ft_file_name, 'w', encoding='utf-8')
        for line in self.train_data_list:
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
    for fidx in xrange(0, 6):
        fq_file_name = gl.zhidao_labeled_foler + 'zhidao_question_' + str("%02d" % fidx) + '.txt'
        if not os.path.isfile(fq_file_name):
            continue
        t2md.get_train_data(fq_file_name)
        t2md.save_train_data(gl.zhidao_labeled_foler + 'json/zhidao_question_' + str("%02d" % fidx) + '.json')
    t2md.save_relation(gl.zhidao_labeled_foler + 'zhidao_question.relation')