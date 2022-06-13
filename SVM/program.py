from nltk.stem.snowball import SnowballStemmer
import sys
import os,glob
import re
import math
import pathlib
import random

def prediction(w_t,mail,classType):
	#Spam = 1 and Ham =-1
	accuracy = 0
	for text in mail:
		#Calculate prediction
		sum = output(text,w_t)
		#If pos+ve ==> spam else if neg-ve ==> ham
		if (sum==1 and classType == "spam"):
			accuracy+=1
		elif (sum==-1 and classType == "ham"):
		
			accuracy+=1
	return float(accuracy)/len(mail)
	
def output(text,w_t):
	output = w_t["BIAS"]
	for word in text:
		if word in w_t:
			output+=(text[word]*w_t[word])
	perceptron = -1
	if (output>0):
		perceptron = 1
	return perceptron

#Update weight vector
def updateWeight(w_t,ham,spam,rate,iterations):
	#Set class type where ham = -1 and spam = 1
	
	#Mix the two in order to avoid skewing to one side
	j = max(len(ham),len(spam))
	
	for i in range(j):
		if i<len(ham):
			text = ham[i]
			o = output(text,w_t)
			for word in text:
				if word in w_t:
					change = rate*text[word]*(-1-o)
					w_t[word]+= change
		if i<len(spam):
			text = spam[i]
			o = output(text,w_t)
			for word in text:
				if word in w_t:
					change = rate*text[word]*(1-o)
					w_t[word]+= change


			
	if (iterations>1):
		w_t = updateWeight(w_t,ham,spam,rate,iterations-1)
	return w_t
	
#0 Weight vector
def initialWeight(hamemails,spamemails):
	wVector = {}
	wVector["BIAS"] = 1
	
	for text in hamemails:
		for word in text:
			if not word in wVector:
				wVector[word] = random.uniform(-0.1,0.1)
		
	for text in spamemails:
		for word in text:
			if not word in wVector:
				wVector[word] = random.uniform(-0.1,0.1)

	return wVector

def featureTables(hamemails,spamemails):
	spamtable = []
	hamtable = []
	
	for text in hamemails:
		textCount = {}
		for word in text:
			if not word in textCount:
				textCount[word] = 1
			else:
				textCount[word] += 1
		hamtable.append(textCount)
		
	for text in spamemails:
		textCount = {}
		for word in text:
			if not word in textCount:
				textCount[word] = 1
			else:
				textCount[word] += 1
		spamtable.append(textCount)
		
	return hamtable,spamtable
	
def stopwords():
	stopwordList =[]
	with open("stopwords.txt",'r') as File:
		for line in File:
			for word in line.split():
				stopwordList.append(word.lower())
		
	return stopwordList
	
	
def reading(folderpath,stopBool):
	#Open file
	mail =[]
	stemmer = SnowballStemmer("english")
	stopwordList = stopwords()
	
	#Get clean text files from the folder
	for filename in glob.glob(os.path.join(folderpath,'*.txt')):
		with open(filename,'r',errors='ignore') as f:
			text = []
			for line in f.readlines():
				for word in line.split():
					word = word.lower()
					cleanword = re.sub(r'\W','',word)
					stemcleanword = stemmer.stem(cleanword)
					if(not stopBool):
						if (stemcleanword != ''):
							text.append(stemcleanword)
					else:
						if ((stemcleanword != '') and (not word in stopwordList)):
							text.append(stemcleanword)
					
						
			mail.append(text)
			
	return mail
	

def main():
	#Requires 2 folders in current directory:
		#one folder called train with ham+spam folders
		#one folder called test with ham+spam folders
	
	#Get path
	path = str(pathlib.Path().absolute())
	
	#Read in training data
	train_hamemails = reading(path+'/train/ham',False)
	train_spamemails = reading(path+'/train/spam',False)
	hamtable,spamtable = featureTables(train_hamemails,train_spamemails)
	
	#Read in test data w/stopwords
	test_hamemails = reading(path+'/test/ham',False)
	test_spamemails = reading(path+'/test/spam',False)
	hamtableTest,spamtableTest = featureTables(test_hamemails,test_spamemails)

	#TEST w/o STOPWORDS
	#Get probability of each text for each class
	test_hamemailsSTOP = reading(path+'/test/ham',True)
	test_spamemailsSTOP = reading(path+'/test/spam',True)
	hamtableTestS,spamtableTestS = featureTables(test_hamemailsSTOP,test_spamemailsSTOP)
	
	print("Rate\tIterations\tTraining\t\t Test_with_stopwords\t Test_without_stopwords")
	
	rates = [0.005,0.02,0.05,0.06,0.08]
	iterations = [4,5,6,7]
	for r in rates:
		for i in iterations:
			weightVector = initialWeight(train_hamemails,train_spamemails)
			weightVector = updateWeight(weightVector,hamtable,spamtable,r,i)
			train_result = (prediction(weightVector,hamtable,"ham")+prediction(weightVector,spamtable,"spam"))/2
			test_result =(prediction(weightVector,hamtableTest,"ham")+prediction(weightVector,spamtableTest,"spam"))/2
			testSTOP_result =(prediction(weightVector,hamtableTestS,"ham")+prediction(weightVector,spamtableTestS,"spam"))/2
			print(r,'\t',i,'\t\t',train_result,'\t',test_result,'\t',testSTOP_result)
	

main()
