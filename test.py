# coding=utf-8
import knowledge_base
import mention_id
import jieba
import jieba.posseg as pseg
import similarity
import editdistance

__author__ = 'yuyang'

# kb = knowledge_base.KnowledgeBase()
# kb.load_knowledge_base()
# # kb.show()

# mid = mention_id.MentionID()
# mid.load_mention_2_id()
# mid.show()

for item in pseg.cut(u'干酪菌属属于什么亚纲？'):
    print type(item), item
    # token, pos = item
    token, pos = item.word, item.flag
    print token, pos

# 什么<体裁>吗，<A>还是<B>
# sent = u'江陵	之	战	是	哪	一	年	爆发	的'.split('\t')
# for token in sent:
#     print token
print editdistance.eval('中国铁路网的五纵三横', '中国家庭教育的关键是什么')
print editdistance.eval('中国铁路网的五纵三横', '中国铁路走向市场的理论和实践')
print editdistance.eval('进修学校', '进修学校')
