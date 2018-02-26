# coding=utf-8
import sys
import gl
import codecs
import time
reload(sys)
sys.setdefaultencoding('utf-8')
from bs4 import BeautifulSoup

class HtmlFileProcess:
	def __init__(self):
		self.qa_pairs = []

	def parse_file(self, file_name):
		t1 = time.time()
		fh = codecs.open(file_name, 'r', encoding='utf-8')
		document = fh.read()
		t2 = time.time()
		print 'Loading html file consumed', t2 - t1, 'seconds'
		question_raw = document.split('end raw')
		for question_no, question_web in enumerate(question_raw):
			if question_no % 1000 == 0:
                print 'Processed', question_no, 'lines'
			soup = BeautifulSoup(question_web, "html.parser")
			if soup.title is None:
				continue
			question_title_txt = soup.title.string
			best_answers_div = soup.findAll("div", {"class": "quality-content-detail"})
			for answer in best_answers_div:
				best_answer_txt = answer.get_text()
			self.qa_pairs.append({'question': question_title_txt, 'answer': best_answer_txt})
		t3 = time.time()
		print 'Processing html file consumed', t3 - t2, 'seconds'
		

	def show_first_n(self, first_n=20):
		for i in xrange(first_n):
			print 'question : ', self.qa_pairs[i]['question']
			print 'best answer : ', self.qa_pairs[i]['answer']

	def generate_qa_file(self, file_name=gl.zhidao_testing_data_file_name):
		fh = codecs.open(file_name, 'w', encoding='utf-8')
		for idx, obj in enumerate(self.qa_pairs):
			fh.write('<question id=' + str(idx+1) + '>\t' + obj['question'] + '\n')
			fh.write('<answer id=' + str(idx+1) + '>\t' + obj['answer'])
			fh.write('====================================')
		fh.close()

if __name__ == '__main__':
	hfp = HtmlFileProcess()
	hfp.parse_file(gl.test_html)
	# hfp.show_first_n()
	hfp.generate_qa_file()
