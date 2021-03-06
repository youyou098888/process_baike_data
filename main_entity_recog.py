# -*- coding: utf-8 -*-
import codecs
import sys
import os
import gl
import query
import similarity
import time
import mention_id
import knowledge_base
import multiprocessing
from string import ascii_lowercase
reload(sys)
sys.setdefaultencoding('utf-8')
'''
    usage: python main_entity_recog.py
    处理文件夹/data/Baike/process/中的数据，对分词的Q，找到KB中对应的实体。实体完全包含Q中的关键词。
    根据答案与KB中subject的关系，排序三元组。
    处理后文件夹/data/res/kbqa/
'''
def entity_recog_thread(threadName, threadNo):
    for fidx in xrange(20):
        if fidx % 20 != threadNo:
            continue
        folder_idx = 's_' + str("%04d" % fidx) + '/'
        for x in ascii_lowercase:
            question_file_name = gl.processed_data_split_file_folder + folder_idx + 'zhidao_xa' + x + '.process-data'
            if not os.path.isfile(question_file_name):
                continue
            if not os.path.exists(gl.res_data_file_folder + folder_idx):
                os.makedirs(gl.res_data_file_folder + folder_idx)
            result_file_name = gl.res_data_file_folder + folder_idx + 'zhidao_xa' + x + '.res-data'
            result_not_match_file_name = gl.res_data_file_folder + folder_idx + 'not_match.zhidao_xa' + x + '.res-data'
            if os.path.isfile(result_file_name):
                continue
            query_list = query.QueryList()
            query_list.read_query_file(question_file_name)
        
            fh = codecs.open(result_file_name, 'w', encoding='utf-8')
            fh_nomatch = codecs.open(result_not_match_file_name, 'w', encoding='utf-8')

            sim = similarity.Similarity()
            for qid, qry in enumerate(query_list.query_list):
                if qid % 100 == 0:
                    print threadName, 'Processed', qid, 'questions'
                # print '||||'.join(qry.tokens)
                # print 'entity:' + entity + 'len(entity):' + str(len(entity))
                # print 'rest_token:', '----'.join(rest_token)
                # input('Press a digit to continue\n')
                qry_possible_id_dict = {}
                for entity in qry.tokens:
                    possible_ids = mid.find_id_set(entity)
                    for pid in possible_ids:
                        # print 'possible id:(' + pid + ')' + str(len(pid))
                        if not qry.valid_pid(pid):
                            continue
                        try:
                            qry_possible_id_dict[qid+1].append(pid)
                        except KeyError:
                            qry_possible_id_dict[qid+1] = [pid]

                if (qid+1) not in qry_possible_id_dict:
                    # print 'Unfortunately,' + qry.query_origin + ' does not match any kb entity'
                    fh_nomatch.write('<question id=' + str(qid + 1) + '>\t')
                    fh_nomatch.write(qry.query_origin + '\n')
                    continue
                # remove duplicate possible_ids because different entities might have the same possible_id
                possible_ids = list(set(qry_possible_id_dict[qid+1]))
                tokens = ''.join(qry.tokens)
                scores = [(len(set(pid)), pid) for pid in possible_ids]
                scores = sorted(scores, key=lambda s: -s[0])
                # for item in scores:
                #     print 'Score for ' + item[1] + ':', item[0]
                # raw_input('*****************\n')

                if len(scores) == 0:
                    scores = [(0, tokens[0])]

                total_answer_scores = []
                for rank in xrange(min(len(scores), 30)):
                    pid = scores[rank][1]
                    # pid = scores[0][1]
                    try:
                        info = kb.knowledge_about[pid]
                    except KeyError:
                        # print 'Unfortunately,' + pid + 'not fount in the knowledge base'
                        # return something
                        fh.write('<question id=' + str(qid + 1) + '>\t')
                        fh.write(qry.query_origin + '\n')
                        fh.write('<answer id=' + str(qid + 1) + '>\t')
                        fh.write('[THIS-IS-AN-ANSWER.]\n')
                        print qid+1, '[THIS-IS-AN-ANSWER.]'
                        fh.write('==================================================\n')
                        continue
                
                    if len(info) == 0:
                        fh.write('---------------------------------------------\n')
                        fh.write('<subject id=' + str(qid + 1) + '-' + str(rank) + '>\t')
                        fh.write(pid + '\n')
                        # fh.write('---------------------------------------------\n')
                    possile_answers = []
                    for idx, obj in enumerate(info):
                        attr, entity2 = obj
                        if 1:
                        # if attr == 'BaiduCARD': # only extract BaiduCard relation
                            possile_answers.append({'pid': pid, 'answer': entity2, 'relation': attr})
                            if idx > 30:
                                break;

                    answer_scores = [(sim.similarity_customize_overlap(item['answer'], qry.answer), item) for item in possile_answers]
                    # print 'pid', pid
                    # for item in answer_scores:
                    #     print 'Score for ' + item[1]['answer'] + ':', item[0]
                    answer_scores = sorted(answer_scores, key=lambda s: -s[0])
                    total_answer_scores = total_answer_scores + answer_scores

                best_match, best_match_score = '[THIS-IS-AN-ANSWER.]', 0.0
                if len(total_answer_scores) != 0:
                    best_match = total_answer_scores[0][1]['answer']
                    best_match_score = total_answer_scores[0][0]

                fh.write('<question id=' + str(qid + 1) + '>\t')
                fh.write(qry.query_origin + '\n')
                
                if len(total_answer_scores) != 0 and best_match_score !=0:
                    for idx, candidate in enumerate(total_answer_scores):
                        fh.write('---------------------------------------------\n')
                        fh.write('<subject id=' + str(qid + 1) + '-' + str(idx) + '>\t')
                        fh.write(candidate[1]['pid'] + '\n')
                        fh.write('<relation id=' + str(qid + 1) + '-' + str(idx) + '>\t')
                        fh.write(candidate[1]['relation'] + '\n')
                        fh.write('<object id=' + str(qid + 1) + '-' + str(idx) + '>\t')
                        fh.write(candidate[1]['answer'] + '\n')

                    # fh.write('<best match subject id=' + str(qid + 1) + '>\t')
                    # fh.write(total_answer_scores[0][1]['pid'] + '\n')
                    # fh.write('<best match answer id=' + str(qid + 1) + '>\t')
                
                    # fh.write(best_match + '\n')
                    # fh.write('<best match score id=' + str(qid + 1) + '>\t')
                    # fh.write(str(best_match_score) + '\n')
                else:
                    fh.write('---------------------------------------------\n')
                    fh.write('[NO-SUBJECT.]' + '\n')
                
                # print qid+1, best_match[1]
                fh.write('==================================================\n')

            print 'closing file', result_file_name 
            fh.close()
            fh_nomatch.close()




if __name__ == '__main__':
    # Step1: load knowledge base
    print 'begin to load kb'
    kb = knowledge_base.KnowledgeBase()
    kb.load_knowledge_base()
    print 'finish loading kb'

    # Step2: load mention2id
    print 'begin to load mention2id'
    mid = mention_id.MentionID()
    mid.load_mention_2_id()
    print 'finish loading mention2id'

    # training phase


    # Step3: load questions
    print 'begin to load questions'
    pool = multiprocessing.Pool()
    cpus = multiprocessing.cpu_count()
    results = []
    # 创建cpus个线程
    for i in xrange(0, cpus):
        result = pool.apply_async(entity_recog_thread, args=("Thread-" + str(i+1), i,))
        results.append(result)
    pool.close()
    pool.join()