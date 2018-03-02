#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from time import time
import gl
from string import ascii_lowercase
import codecs
import operator

reload(sys)
sys.setdefaultencoding('utf8')

class ExtractRelation:
    def __init__(self):
        self.relations = {}
        self.filtered_relations = {}
        self.question_no = 0
        self.sorted_relations = []

    def merge_two_dicts(self, x, y):
        z = x.copy()   # start with x's keys and values
        z.update(y)    # modifies z with y's keys and values & returns None
        return z


    def extract_relation(self, file_name):
        print 'extract_relation', file_name
        fh = codecs.open(file_name, 'r', encoding='utf-8')
        document = ''.join([x for x in fh.readlines()])
        qa_pairs = document.split('==================================================')
        self.question_no += len(qa_pairs)
        for qa in qa_pairs:
            triples = qa.split('---------------------------------------------')
            if len(triples) == 0:
                continue
            for x in xrange(1, min(4, len(triples))):
                # print triples[x].split('\n')
                if '[NO-SUBJECT.]' == triples[x].split('\n')[1]:
                    continue
                relation = triples[x].split('\n')[2].split('\t')[1]
                try:
                    self.relations[relation] += 1
                except:
                    self.relations[relation] = 1
    
    def filter_relation(self):
        for key, val in self.relations.items():
            if val < 30:
                continue
            try:
                self.filtered_relations[key] += val
            except:
                self.filtered_relations[key] = val
        self.relations = {}
        

    def save_relations(self, file_name):
        print 'processing ', self.question_no, 'questions'
        self.sorted_relations = sorted(self.filtered_relations.items(), key=operator.itemgetter(1), reverse=True)
        
        with open(file_name, 'w') as f:
            for relation in self.sorted_relations:
                f.write(relation[0] + '\t' + str(relation[1]) + '\n')
            

if __name__ == '__main__':
    er = ExtractRelation()
    for fidx in xrange(20):
        folder_idx = 's_' + str("%04d" % fidx) + '/'
        for x in ascii_lowercase:
            res_file_name = gl.res_data_file_folder + folder_idx + 'zhidao_xa' + x + '.res-data'
            if not os.path.isfile(res_file_name):
                continue
            er.extract_relation(res_file_name)
    er.filter_relation()
    er.save_relations('relations.txt')
            # break