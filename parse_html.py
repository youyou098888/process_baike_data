# coding=utf-8
import sys
import gl
import codecs
import time
import re
reload(sys)
sys.setdefaultencoding('utf-8')
from bs4 import BeautifulSoup

class HtmlFileProcess:
	def __init__(self):
		self.qa_pairs = []
		self.fact_word = ['是什么', '什么是', '什么叫', '是谁']
		self.non_fact_word = ['什么歌', '为什么', '怎么']

	def check_factoid(self, question):
		factoid = False
		for x in self.fact_word:
			if x in question:
				factoid = True
		for x in self.non_fact_word:
			if x in question:
				factoid = False
		return factoid

	def parse_file(self, file_name):
		print 'begin to parse file ', file_name
		t1 = time.time()
		fh = codecs.open(file_name, 'r', encoding='utf-8')
		document = ''.join([x.strip('\n') for x in fh.readlines()])
		t2 = time.time()
		print 'Loading html file consumed', t2 - t1, 'seconds'
		question_raw = document.split('end raw')
		for question_no, question_web in enumerate(question_raw):
			if question_no % 100 == 0:
				print 'Processed', question_no, 'lines'
			soup = BeautifulSoup(question_web, "html.parser")
			if soup.title is None:
				continue
			question_title_txt = soup.title.string
			best_answers_div = soup.findAll("div", {"class": "wgt-best"})
			best_answer_txt = 'No Best Answer Found'
			found = False
			for answer_div in best_answers_div:
				for answer in answer_div.findAll("pre", {"class": 'best-text'}):
					best_answer_txt = answer.get_text()
					found = True
			if not found:
				best_answers_div = soup.findAll("div", {"class": "wgt-recommend"})
				for answer_div in best_answers_div:
					for answer in answer_div.findAll("pre", {"class": 'recommend-text'}):
						best_answer_txt = answer.get_text()
						found = True
			if self.check_factoid(question_title_txt):
				self.qa_pairs.append({'question': question_title_txt, 'answer': best_answer_txt})
		t3 = time.time()
		print 'Processing html file consumed', t3 - t2, 'seconds'
		

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

if __name__ == '__main__':
	hfp = HtmlFileProcess()
	hfp.parse_file(file_name=gl.parse_html)
	# hfp.show_first_n()
	hfp.generate_qa_file(file_name=gl.zhidao_testing_data_file_name_factoid)
