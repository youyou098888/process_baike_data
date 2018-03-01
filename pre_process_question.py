#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from time import time
import gl
import jieba
import jieba.posseg as pseg
from string import ascii_lowercase

reload(sys)
sys.setdefaultencoding('utf8')

class PreProcessQuery:
    def __init__(self):
        self.query_list = []

    def get_chinese(self, word):
        index = word.find('>')
        res = word[index+1:].replace(' ', '').strip('\t').strip('\r')
        res = res.replace('_百度知道', '')
        # print res
        return res

    def get_precise_tokens(self, word):
        return jieba.cut(word, cut_all=True)

    def get_mentions(self, word):
        return jieba.cut_for_search(word)

    def process_question_answer_pairs(self, file_name):
        print 'begin to process file ', file_name
        start = time()
        content = []
        with open(file_name, 'r') as f:
            content = f.readlines()
            content = [x.strip('\n') for x in content]
        total_len = len(content)
        result = []
        for idx in range(0,total_len-2,3):
            ques = self.get_chinese(content[idx])
            answ = self.get_chinese(content[idx+1])
            tokens = self.get_precise_tokens(ques)
            mentions = self.get_mentions(ques)
            result.append([ques, answ, '\t'.join(tokens), '\t'.join(mentions)])
        # print result
        stop = time()
        print("process question using " + str(stop - start) + "s")
        return result

if __name__ == '__main__':
    ppq = PreProcessQuery()
    for fidx in xrange(20):
        folder_idx = 's_' + str("%04d" % fidx) + '/'
        for x in ascii_lowercase:
            factoid_file_name = gl.zhidao_testing_data_folder_name + folder_idx + 'zhidao_xa' + x + '.fact.testing-data'
            processed_file_name = gl.processed_data_split_file_folder + folder_idx + 'zhidao_xa' + x + '.process-data'
            if not os.path.isfile(factoid_file_name):
                continue
            if os.path.isfile(processed_file_name):
                continue
            if not os.path.exists(gl.processed_data_split_file_folder + folder_idx):
                os.makedirs(gl.processed_data_split_file_folder + folder_idx)
            testing_question_answer_pairs = ppq.process_question_answer_pairs(file_name=factoid_file_name)
            
            with open(processed_file_name, 'w') as f:
                for pair in testing_question_answer_pairs:
                    f.write(pair[0] + '\n')
                    f.write(pair[1] + '\n')
                    f.write(pair[2] + '\n')
                    f.write(pair[3] + '\n')
                    f.write("==================================================\n")