from nltk.stem.snowball import SnowballStemmer
import sys
import os,glob
import re
import math
import pathlib
from decimal import Decimal

def NBpredict(probWHam,probWSpam,mail,type,pHam,pSpam,totalHam,totalSpam):
	
	K = 1
	ZeroHam = float(0+K)/(totalHam+len(probWHam))
	ZeroSpam =float(0+K)/(totalSpam+len(probWSpam))
	
	accuracy = 0
	for text in mail:
		prediction = ""
		probHamText = math.log(pHam)
		probSpamText = math.log(pSpam)
		
		for word in text:
			#Get P(Word|Class)
			ham = ZeroHam #Assume word not in list of words of ham emails
			spam = ZeroSpam  #Assume word not in list of words of spam emails
				
			if word in probWHam.keys():
				ham = probWHam[word]
			if word in probWSpam.keys():
				spam = probWSpam[word]
			
			#Accumalate to get get P(Class|Text) with log to avoid underflow
			probHamText += math.log(ham)
			probSpamText += math.log(spam)
		
		
		if (probHamText>probSpamText):
			prediction = "ham"
		elif(probHamText<=probSpamText):
			prediction = "spam"
		
		if (type == prediction or (type=="spam1" and prediction == "spam")):
			accuracy+=1
	
	return (float(accuracy)/len(mail))
		

def multNB(ham,spam):

	#Get prob of class ie ham/spam
	numHam = len(ham)
	numSpam = len(spam)
	P_ham = float(numHam)/(numHam+numSpam)
	P_spam = float(numSpam)/(numHam+numSpam)

	#Variables
	spamwords = {}
	totalspam = 0
	hamwords = {}
	totalham = 0
	K = 1

	#Count number of occurences of each word in each text
	for text in ham:
		for word in text:
			totalham+=1
			if word in hamwords:
				hamwords[word]+=1
			else:
				hamwords[word] = 0

	for text in spam:
		for word in text:
			totalspam+=1
			if word in spamwords:
				spamwords[word]+=1
			else:
				spamwords[word] = 0

	#Change value from occurences to probability of that word given class
	for word in hamwords:
		hamwords[word] = float(hamwords[word]+K)/(totalham+(len(hamwords)*K))

	for word in spamwords:
		spamwords[word]= float(spamwords[word]+K)/(totalspam+(len(spamwords)*K))

	return hamwords,spamwords,P_ham,P_spam,totalham,totalspam


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
	
	#Get probability of each text for each class
	hamwords,spamwords,pHam,pSpam,totalHam,totalSpam = multNB(train_hamemails,train_spamemails)
	
	hamTrainPredict = NBpredict(hamwords,spamwords,train_hamemails,"ham",pHam,pSpam,totalHam,totalSpam)
	spamTrainPredict = NBpredict(hamwords,spamwords,train_spamemails,"spam",pHam,pSpam,totalHam,totalSpam)
	totalTrainPredict = float(hamTrainPredict+spamTrainPredict)/2
	
	#Read in test data w/stopwords
	test_hamemails = reading(path+'/test/ham',False)
	test_spamemails = reading(path+'/test/spam',False)
	
	#Get Test prediction results w/stopwords
	hamTestPredict = NBpredict(hamwords,spamwords,test_hamemails,"ham",pHam,pSpam,totalHam,totalSpam)
	spamTestPredict = NBpredict(hamwords,spamwords,test_spamemails,"spam",pHam,pSpam,totalHam,totalSpam)
	totalTestPredict = float(hamTestPredict+spamTestPredict)/2

	#TEST w/o STOPWORDS
	#Get probability of each text for each class
	test_hamemailsSTOP = reading(path+'/test/ham',True)
	test_spamemailsSTOP = reading(path+'/test/spam',True)
	
	hamTestPredictSTOP = NBpredict(hamwords,spamwords,test_hamemailsSTOP,"ham",pHam,pSpam,totalHam,totalSpam)
	spamTestPredictSTOP = NBpredict(hamwords,spamwords,test_spamemailsSTOP,"spam",pHam,pSpam,totalHam,totalSpam)
	totalTestPredictSTOP = float(hamTestPredictSTOP+spamTestPredictSTOP)/2
	
	print("Training\t\t Test_with_stopwords\t Test_without_stopwords")
	print(totalTrainPredict,"\t",spamTestPredict,"\t",totalTestPredictSTOP)
	
main()
