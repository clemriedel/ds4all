from __future__ import print_function
import pandas as pd
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
import csv
import numpy as np
import pandas as pd
import seaborn as sns
import textmining
import lda
import textmining
import nltk.corpus
import os






def clemlda(a):

	prev_num = 0
	for f in os.listdir('static'):
		if f[0:4] == 'hist':
			num = int(f.split('_')[-1].split('.')[0])
			if num > prev_num:
				prev_num = num
	f_name = 'hist_{}.png'.format(prev_num+1)
	#t_name ='topic_table_{}.csv'.format(prev_num+1)

	with open(a) as f:
		Header = f.next().split(',')
	number_name = Header[0]
	text_name = Header[1][:-1]

	#Read the input file
	input_file = csv.DictReader(open(a))

	text = []
	number = []

	for row in input_file:
	    number.append(row[number_name])
	    text.append(row[text_name])

	d = len(text)
	n_topics = 25

	text_stop = []
	stop = set(stopwords.words('english'))
	stop |= {'new', 'made', 'use'}

	for i in range(len(text)):
	    sentence = text[i].lower()
	    A = [i for i in sentence.replace('<br/>',' ').split() if i not in stop]
	    A = [i[:-1] for i in A  if i[-1] == 's']
	    text_stop.append(' '.join(A))

	tdm = textmining.TermDocumentMatrix()

	for i in range(d):
	    tdm.add_doc(text_stop[i])

	# # create a temp variable with doc-term info
	temp = list(tdm.rows(cutoff=1))

	# get the vocab from first row
	vocab = tuple(temp[0])

	# # get document-term matrix from remaining rows
	X = np.array(temp[1:])


	#tdm.write_csv('matrix.csv', cutoff=1)
	topics = []

	model = lda.LDA(n_topics, n_iter=500, random_state=2)
	model.fit(X)  # model.fit_transform(X) is also available
	topic_word = model.topic_word_  # model.components_ also works
	n_top_words = 8
	for i, topic_dist in enumerate(topic_word):
	    topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words+1):-1]
	    topics.append('Topic {}: {}'.format(i+1, ' '.join(topic_words)))
	    #print('Topic {}: {}'.format(i+1, ' '.join(topic_words)))

	# get results
	topic_word = model.topic_word_ 
	doc_topic = model.doc_topic_


	# with open('static/{}'.format(t_name), 'w') as f:
	#     # create header
	#     #header = 'document'
	#     #for k in range(n_topics):
	#     #   header += ', pr_topic_{}'.format(k)
	#     #f.write(header + '\n')

	#     # write one row for each document
	#     # col 1 : document number
	#     # cols 2 -- : topic probabilities
	#     for k in range(d):
	#         # format probabilities into string
	#         str_probs = ','.join(['{:.5e}'.format(pr) for pr in doc_topic[k,:]])
	#         # write line to file
	#         #f.write('{}, {}\n'.format(k, str_probs))
	#         f.write('{}\n'.format(str_probs))
	
		
	# dat = np.genfromtxt ('static/{}'.format(t_name), delimiter=",")

	M_ = []
	for i in range(len(number)):
    		M_.append(doc_topic[i,:]*float(number[i]))

	M = sum(M_)
	Total = sum(M)


	x=np.arange(1, n_topics+1, 1)


	ax = sns.barplot(x, M, color='Blue')
	ax.set(xlabel='Topics', ylabel=number_name)
	ax.set_title('Total: {} {}'.format(int(Total), number_name))
	num = 1
	sns.plt.savefig('static/{}'.format(f_name), dpi=300)
	plt.clf()

	del ax, M, M_, Total


	return topics, text_name, f_name



