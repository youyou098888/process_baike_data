import codecs
import sys
import gl
import query
import similarity
import time
import mention_id
import knowledge_base
reload(sys)
sys.setdefaultencoding('utf-8')


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
    query_list = query.QueryList()
    query_list.read_query_file(gl.testing_data_split_file_name)
    
    fh = codecs.open(gl.testing_data_result_file_name, 'w', encoding='utf-8')
    fh_nomatch = codecs.open(gl.testing_data_not_match_result_file_name, 'w', encoding='utf-8')

    sim = similarity.Similarity()
    for qid, qry in enumerate(query_list.query_list):
        # print 'query id:', qid+1

        # print '||||'.join(qry.tokens)
        # print 'entity:' + entity + 'len(entity):' + str(len(entity))
        # print 'rest_token:', '----'.join(rest_token)
        # input('Press a digit to continue\n')
        qry_possible_id_dict = {}
        for entity in qry.tokens:
            possible_ids = mid.find_id_set(entity)
            for pid in possible_ids:
                # print 'possible id:(' + pid + ')' + str(len(pid))
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
        scores = [(sim.similarity(tokens, pid), pid) for pid in possible_ids]
        scores = sorted(scores, key=lambda s: -s[0])
        # for item in scores:
        #     print 'Score for ' + item[1] + ':', item[0]
        # raw_input('*****************\n')

        if len(scores) == 0:
            scores = [(1.0, tokens[0])]

        pid = scores[0][1]
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
        # best_match, best_match_score = ('[ATTRIBUTE]', '[THIS-IS-AN-ANSWER.]'), 0.0
        # for attr, entity2 in info:
        #     for token in rest_token:  # tokens
        #         tmp_score = sim.similarity(attr, token)
        #         # print 'For pair (' + token + ', '+ attr + '), similarity = ', tmp_score
        #         if tmp_score > best_match_score:
        #             best_match_score = tmp_score
        #             best_match = (attr, entity2)

        # for attr, entity2 in info:
        #     if attr in rest_token:
        #         best_match = (attr, entity2)
        #         break

        fh.write('<question id=' + str(qid + 1) + '>\t')
        fh.write(qry.query_origin + '\n')
        fh.write('---------------------------------------------\n')
        for idx, score in enumerate(scores):
            fh.write('<subject id=' + str(qid + 1) + '-' + str(idx) + '>\t')
            fh.write(score[1] + '\n')
        fh.write('---------------------------------------------\n')
        possile_answers = []
        for idx, obj in enumerate(info):
            attr, entity2 = obj
            possile_answers.append(entity2)
            fh.write('<predicate id=' + str(qid + 1) + '-' + str(idx) + '>\t')
            fh.write(attr + '\n')
            fh.write('<object id=' + str(qid + 1) + '-' + str(idx) + '>\t')
            fh.write(entity2 + '\n')

        scores = [(sim.similarity(qry.answer, answer), answer) for answer in possile_answers]
        scores = sorted(scores, key=lambda s: -s[0])
        fh.write('<answer id=' + str(qid + 1) + '>\t')
        best_match, best_match_score = ('[ATTRIBUTE]', '[THIS-IS-AN-ANSWER.]'), 0.0
        if len(scores) != 0:
            best_match = scores[0][1]
            best_match_score = scores[0][0]
        fh.write(best_match + '\n')
        # print qid+1, best_match[1]
        fh.write('==================================================\n')

        
    fh.close()
    fh_nomatch.close()
