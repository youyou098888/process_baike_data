#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from time import time
import gl
from string import ascii_lowercase
import codecs
import re

reload(sys)
sys.setdefaultencoding('utf8')

class ProcessResMerge:
    def __init__(self):
        self.question_no = 0

    def get_qa_pairs(self, fq_file_name, fa_file_name):
        print 'processing file', fq_file_name
        fq = codecs.open(fq_file_name, 'r', encoding='utf-8')
        fa = codecs.open(fa_file_name, 'r', encoding='utf-8')

        fq_document = ''.join([x for x in fq.readlines()])
        fq_pairs = fq_document.split('==================================================')

        fa_document = ''.join([x for x in fa.readlines()])
        fa_pairs = fa_document.split('====================================')
        fa_pair_dict = {}
        for idx, fa in enumerate(fa_pairs):
            tmp = fa.split('\n')
            for tt in tmp:
                am = re.search('<answer id=(\d+)>\t(.*)', tt)
                if am:
                    fa_pair_dict[am.groups()[0]] = {'answer': tt}
        # for test in xrange(1, 1700):
        #     print fa_pair_dict[str(test)]
        
        fnew = codecs.open(fq_file_name + '-format', 'w', encoding='utf-8')
        self.question_no += len(fq_pairs)
        for qa in fq_pairs:
            triples = qa.split('---------------------------------------------')
            if len(triples) == 0 or triples[0] == '':
                continue
            # print triples[0]
            m = re.search('<question id=(\d+)>\t(.*)', triples[0].strip('\n'))
            if m:
                question_idx = m.groups()[0]
                question_txt = m.groups()[1]
                try:
                    # fnew.write(triples[0])
                    # fnew.write(fa_pair_dict[str(question_idx)]['answer'] + '\n')
                    triples = triples[1:11] 
                    for triple in triples:
                        # fnew.write('---------------------------------------------')
                        # fnew.write(triple)
                        # pass
                        threearr = triple.split('\n')
                        print fa_pair_dict[str(question_idx)]['answer'].split('\t')
                        answer_txt = fa_pair_dict[str(question_idx)]['answer'].split('\t')[1]
                        fnew.write(question_txt + '\t' + 
                                   answer_txt + '\t' + 
                                   threearr[1].split('\t')[1] + '\t' + 
                                   threearr[2].split('\t')[1] + '\t' + 
                                   threearr[3].split('\t')[1] + '\n')
                    
                    fnew.write('==================================================\n')
                except Exception as e:
                    
                    print e
                    print 'no answer found', question_idx
            else:
                print triples[0]
                print 'no'
        print 'generating file', fq_file_name + '-format'
            

if __name__ == '__main__':
    prm = ProcessResMerge()
    for fidx in xrange(20):
        folder_idx = 's_' + str("%04d" % fidx) + '/'
        for x in ascii_lowercase:
            res_file_name = gl.res_data_file_folder + folder_idx + 'zhidao_xa' + x + '.res-data'
            ques_file_name = gl.zhidao_testing_data_folder_name + folder_idx + 'zhidao_xa' + x + '.fact.testing-data'
            if not os.path.isfile(res_file_name):
                continue
            if not os.path.isfile(ques_file_name):
                continue
            prm.get_qa_pairs(res_file_name, ques_file_name)
            # break