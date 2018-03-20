#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from time import time
import gl
import jieba
import jieba.posseg as pseg
from string import ascii_lowercase
'''
    usage: python pre_process_question.py
    处理文件夹/data/Baike/testing/中的QA对，保留原始QA，对Q分词。
    处理后文件夹/data/Baike/process/
    格式为:
            word自动恢复信息时间是什么意思
            这个应该是如果WORD意外崩溃，而你未对文档做保存，安会自动给你恢复。相当于每10分钟做一个镜像。如果崩溃了，就恢复到最后一次镜像。好像是这样理解的。呵呵。
            word    自动  恢复  复信  信息  时间  是   什么  意思
            word    自动  恢复  信息  时间  是   什么  意思
            ==================================================
    程序中断后可以重跑（续跑），对于已经生成的文件，不再重新生成
'''
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