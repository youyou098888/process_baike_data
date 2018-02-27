# coding=utf-8
import codecs
import sys
import gl
import time
import mention_id
import jieba
reload(sys)
sys.setdefaultencoding('utf-8')


class KnowledgeBase:
    def __init__(self):
        self.knowledge_about = {}
        self.mention_about = {}
        self.stop_words = ['电视剧', '关于', '怎样', '书', '哪个', '有', '谁', '知道', '大家', '一', '本', '一本',
                           '叫', '到', '你', '比较', '好', '的', '做', '有人', '那', '新', '买', '过', '问', '下',
                           '什么', '了解', '能', '告诉', '我', '没', '没有', '呃', '…', '想', '电影', '游戏', '音乐',
                           '小说', '过', '去', '请教', '一下', '你们', '玩', '给', '大家', '你们', '玩', '给', '怎么',
                           '首', '认识', '还有', '与', '人', '家', '啥', '把', '有人', '请问', '时候', '很', '好奇',
                           '考', '考考', '考你', '是', '记得', '的', '得', '这是', '哪里', '意思', '如何', '使用',
                           '是什么']

    def load_knowledge_base(self, knowledge_file_name=gl.knowledge_base_file_name):
        # Typically, it takes ~1630s 30min to load baike.triples.kb this file.
        t1 = time.time()
        fh = codecs.open(knowledge_file_name, 'r', encoding='utf-8')
        total_line_number, skipped = 0, 0
        for line_no, line in enumerate(fh.readlines()):
            # if line_no > 101840:
            #     print 'line content:', line.rstrip()
            total_line_number += 1
            if line_no % 1000000 == 0:
                print 'Processed', line_no, 'lines'
            try:
                entity1, predicate, entity2 = line.rstrip().split('\t')
                entity1 = entity1.replace('"', '')
                entity2 = entity2.replace('"', '')
            except ValueError:
                skipped += 1
                continue
                # print line.rstrip()
                # print 'Split by |||:'
                # for item in line.rstrip().split('|||'):
                #     print item
                # print 'Split by < >|||< >:'
                # for item in line.rstrip().split(' ||| '):
                #     print item
                # print 'Error at line', line_no
                # exit(1)
            try:
                self.knowledge_about[entity1].append((predicate, entity2))
            except KeyError:
                self.knowledge_about[entity1] = [(predicate, entity2)]
        fh.close()
        print 'total line number:', total_line_number
        print 'skipped:', skipped

        for entity in self.knowledge_about.keys():
            self.knowledge_about[entity] = set(self.knowledge_about[entity])
        t2 = time.time()
        print 'Loading knowledge base consumed', t2 - t1, 'seconds'

    def show(self, first_n=20):
        for i, entity in enumerate(self.knowledge_about.keys()):
            # print entity, len(entity)
            print entity
            for predicate, entity2 in self.knowledge_about[entity]:
                # print predicate, len(predicate), type(predicate), entity2, len(entity2), type(entity2)
                print '\t', predicate, entity2
            if i > first_n:
                break

    def show_entity(self, entity):
        if entity in self.knowledge_about:
            print entity, 'in knowledge base! attributes:'
            for item in self.knowledge_about[entity]:
                predicate, entity2 = item
                print predicate, entity2
            pass
        else:
            print 'Unfortunately,' + entity + 'not found!'

    def generate_mention2id(self):
        # this might take about ~1800s, 30min
        print 'begin to generate mention2id file'
        t1 = time.time()
        mention_2_id_file = open(gl.knowledge_base_mention_file_name, 'w')
        for entity in self.knowledge_about.keys():
            entity_seg_tmp = jieba.cut(entity, cut_all=False)
            for mentionid in entity_seg_tmp:
                if (mentionid in self.stop_words) or (len(mentionid) < 2):
                    continue
                try:
                    self.mention_about[mentionid].append(entity)
                except KeyError:
                    self.mention_about[mentionid] = [entity]
        for mentionid in self.mention_about.keys():
            mention_2_id_file.write(mentionid + ' ||| ')
            mention_2_id_file.write('\t'.join(self.mention_about[mentionid]) + '\n')
        mention_2_id_file.close()
        t2 = time.time()
        print 'Generate mention2id file consumed', t2 - t1, 'seconds'


if __name__ == '__main__':
    kb = KnowledgeBase()
    kb.load_knowledge_base()
    kb.generate_mention2id()
    mid = mention_id.MentionID()
    mid.load_mention_2_id()
    while True:
        s = raw_input()
        s = s.decode('utf-8')
        print type(s), s
        t1 = time.time()
        possible_ids = {s} | mid.show_id_set(s)
        for pid in possible_ids:
            print 'Possible id:', pid
            kb.show_entity(pid)
        t2 = time.time()
        print 'Query on string', s, 'consumed', t2 - t1, 'seconds'
        if s == 'EXIT':
            break
