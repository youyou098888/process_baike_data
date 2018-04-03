# coding=utf-8
import sys
import os
import gl
import codecs
import time
import re
from string import ascii_lowercase
reload(sys)
sys.setdefaultencoding('utf-8')
from bs4 import BeautifulSoup
import multiprocessing
'''
	usage: python parse_html.py
	开启cpus个线程并行处理原始的html文档(/data/Baike/zhidao/)，从中提取出问题和答案
	问题长度超过30个字的去掉
	factoid=True: 忽略fact_word，处理后文件夹为/data/Baike/testing-factword/
	factord=False: 只处理包含fact_word的问题，处理后文件夹为/data/Baike/testing/
	程序中断后可以重跑（续跑），对于已经生成qa对的文件，不再重新生成
'''
class HtmlFileProcess:
	def __init__(self):
		self.qa_pairs = []
		self.fact_word = ['是什么', '什么是', '什么叫', '是谁', '什么人', '谁是', '什么意思']
		self.non_fact_word = ['什么歌', '为什么', '怎么', '什么关系', '什么区别', '最著名', 
							  '最快', '最近', '最好', '最新', '原因是', '什么原因', '区别是']

	def check_factoid(self, question):
		if len(question) > 90:
			return False
		factoid = True # 是否只处理包含fact_word的问题
		for x in self.fact_word:
			if x in question:
				factoid = True 
		for x in self.non_fact_word:
			if x in question:
				factoid = False
		return factoid

	def parse_file(self, file_name, thread_name):
		self.qa_pairs = []
		print thread_name, 'begin to parse file ', file_name
		t1 = time.time()
		fh = codecs.open(file_name, 'r', encoding='utf-8')
		document = ''.join([x.strip('\n') for x in fh.readlines()])
		t2 = time.time()
		print 'Loading html file consumed', t2 - t1, 'seconds'
		question_raw = document.split('**END**')
		print 'file ', file_name, 'contains ', len(question_raw), 'raw questions'
		for question_no, question_web in enumerate(question_raw):
			if question_no % 100 == 0:
				print thread_name, 'Processed', question_no, 'pages'
			soup = BeautifulSoup(question_web, 'html.parser')
			if soup.title is None:
				continue
			question_title_txt = soup.title.string
			best_answers_div = soup.findAll('div', {'class': 'wgt-best'})
			best_answer_txt = 'No Best Answer Found'
			found = False
			for answer_div in best_answers_div:
				for answer in answer_div.findAll('pre', {'class': 'best-text'}):
					best_answer_txt = answer.get_text()
					found = True
			if not found:
				best_answers_div = soup.findAll('div', {'class': 'wgt-recommend'})
				for answer_div in best_answers_div:
					for answer in answer_div.findAll('pre', {'class': 'recommend-text'}):
						best_answer_txt = answer.get_text()
						found = True
			if not found:
				quality_answer_div = soup.findAll('div', {'class': 'quality-content-detail'})
				for answer_div in quality_answer_div:
					best_answer_txt = answer_div.get_text()
					found = True
			if not found:
				ordinary_answer_div = soup.findAll('div', {'class': ['bd', 'answer']})
				for answer_div in ordinary_answer_div:
					for answer in answer_div.findAll('pre', {'class': 'answer-text'}):
						best_answer_txt = answer.get_text()
						found = True
			if self.check_factoid(question_title_txt):
				self.qa_pairs.append({'question': question_title_txt, 'answer': best_answer_txt})
				if best_answer_txt == 'No Best Answer Found':
					try:
						with open('../bad/' + question_title_txt + '.txt', 'w') as ff:
							ff.write(question_web)
					except Exception as e:
						print e
						pass

		t3 = time.time()
		print thread_name, 'Processing html file consumed', t3 - t2, 'seconds'
		

	def show_first_n(self, first_n=20):
		for i in xrange(first_n):
			print 'question : ', self.qa_pairs[i]['question']
			print 'best answer : ', self.qa_pairs[i]['answer']

	def generate_qa_file(self, file_name=gl.zhidao_testing_data_file_name_factoid):
		print 'genrating qa file ', file_name
		fh = codecs.open(file_name, 'w', encoding='utf-8')
		for idx, obj in enumerate(self.qa_pairs):
			fh.write('<question id=' + str(idx+1) + '>\t' + obj['question'] + '\n')
			fh.write('<answer id=' + str(idx+1) + '>\t' + obj['answer'] + '\n')
			fh.write('====================================\n')
		fh.close()

def parse_thread(threadName, threadNo):
	hfp = HtmlFileProcess()
	for fidx in xrange(20):
		if fidx % 20 == threadNo:
			folder_idx = 's_' + str("%04d" % fidx) + '/'
			print threadName, 'processing' , folder_idx, 'folder'
			for x in ascii_lowercase:
				html_file_name = gl.parse_html_folder + folder_idx + 'xa' + x
				target_file_name = gl.zhidao_testing_data_folder_name + folder_idx + 'zhidao_xa' + x + '.fact.testing-data'
				
				if os.path.isfile(html_file_name):
					if not os.path.exists(gl.zhidao_testing_data_folder_name + folder_idx):
						os.makedirs(gl.zhidao_testing_data_folder_name + folder_idx)
					if os.path.isfile(target_file_name):
						# already generate this file pass
						continue
					print html_file_name, target_file_name
					hfp.parse_file(file_name=html_file_name, thread_name=threadName)
					# hfp.show_first_n()
					hfp.generate_qa_file(file_name=target_file_name)
				else:
					pass
					# print html_file_name, 'not exit'


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print 'usage: \n' + 'python parse_html.py single\n' + 'python knowledge_base.py multiple\n'
		quit()
	if sys.argv[1] == 'single':
		html_file_name = '../zhidao.data.sample'
		target_file_name = '../zhidao.data.sample.target'
		hfp = HtmlFileProcess()
		hfp.parse_file(file_name=html_file_name, thread_name='single thread')
		hfp.generate_qa_file(file_name=target_file_name)
	else:
		pool = multiprocessing.Pool()
		cpus = multiprocessing.cpu_count()
		results = []
		# 创建cpus个线程
		for i in xrange(0, cpus):
			result = pool.apply_async(parse_thread, args=("Thread-" + str(i+1), i,))
			results.append(result)
		pool.close()
		pool.join()