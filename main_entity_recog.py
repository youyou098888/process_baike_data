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
    print 'begin to load questions'
    query_list = query.QueryList()
    query_list.read_query_file(gl.testing_data_split_file_name)
    
    fh = codecs.open(gl.testing_data_result_file_name, 'w', encoding='utf-8')
    fh_nomatch = codecs.open(gl.testing_data_not_match_result_file_name, 'w', encoding='utf-8')

    sim = similarity.Similarity()
    for qid, qry in enumerate(query_list.query_list):
        if qid % 100 == 0:
            print 'Processed', qid, 'questions'
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
        scores = [(sim.edit_distance(tokens, pid), pid) for pid in possible_ids]
        scores = sorted(scores, key=lambda s: s[0])
        # for item in scores:
        #     print 'Score for ' + item[1] + ':', item[0]
        # raw_input('*****************\n')

        if len(scores) == 0:
            scores = [(0, tokens[0])]

        fh.write('<question id=' + str(qid + 1) + '>\t')
        fh.write(qry.query_origin + '\n')
        # fh.write('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
        possile_answers = []
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
            
            for idx, obj in enumerate(info):
                attr, entity2 = obj
                if 1:
                # if attr == 'BaiduCARD': # only extract BaiduCard relation
                    possile_answers.append({'pid': pid, 'answer': entity2})
                    fh.write('---------------------------------------------\n')
                    fh.write('<subject id=' + str(qid + 1) + '-' + str(rank) + '>\t')
                    fh.write(pid + '\n')
                    fh.write('<predicate id=' + str(qid + 1) + '-' + str(idx) + '>\t')
                    fh.write(attr + '\n')
                    fh.write('<object id=' + str(qid + 1) + '-' + str(idx) + '>\t')
                    fh.write(entity2 + '\n')
                    if idx > 30:
                        break;

        answer_scores = [(sim.similarity(qry.answer, item['answer']), item) for item in possile_answers]
        # for item in answer_scores:
        #     print 'Score for ' + item[1]['answer'] + ':', item[0]
        answer_scores = sorted(answer_scores, key=lambda s: -s[0])
        fh.write('---------------------------------------------\n')
        fh.write('<best match subject id=' + str(qid + 1) + '>\t')
        if len(answer_scores) != 0:
            fh.write(answer_scores[0][1]['pid'] + '\n')
        else:
            fh.write('[NO-SUBJECT.]' + '\n')
        fh.write('<best match answer id=' + str(qid + 1) + '>\t')
        best_match, best_match_score = '[THIS-IS-AN-ANSWER.]', 0.0
        if len(answer_scores) != 0:
            best_match = answer_scores[0][1]['answer']
            best_match_score = answer_scores[0][0]
        fh.write(best_match + '\n')
        fh.write('<best match score id=' + str(qid + 1) + '>\t')
        fh.write(str(best_match_score) + '\n')
        # print qid+1, best_match[1]
        fh.write('==================================================\n')

    print 'closing file'  
    fh.close()
    fh_nomatch.close()
