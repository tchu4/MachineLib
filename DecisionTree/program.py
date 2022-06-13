import sys
import csv
from csv import reader
import math
from decimal import Decimal

class Node:
	def __init__(self,attr,decision,rowsamples,value,valueName=""):
		#Left and right nodes
		self.branches = []
		
		#Attributes of the node and place in the set given
		self.attr = attr
		self.decision = decision
		self.samples = rowsamples
		self.value = value
		self.valueName = valueName
	
	#Check if node is leaf node
	def isLeafNode(self):
		if (len(self.branches) ==0):
			return True
		else:
			return False
	
	#Used to print Tree based on instructions
	def printNodeClass(self,numSpaces):
		printclass = ""
		printname = self.attr
		if (self.isLeafNode()):
			printname=""
			printclass = self.decision
		print(" | "*numSpaces,end="")
		print(printname," ",self.valueName,":",printclass)

	#Used to print to check to ensure that values of this node are correct
	def printNodeInfo(self,numSpaces):
		if(self.attr != "NONE"):
			print(" | "*numSpaces,end="")
			print("Best Attribute: ",self.attr)
		if(self.valueName != " "):
			print(" | "*numSpaces,end="")
			print("Attribute Value: ",self.valueName)
		print(" | "*numSpaces,end="")
		print("Class: ",self.decision)
		print(" | "*numSpaces,end="")
		print("Sample Number: ",len(self.samples))
		print(" | "*numSpaces,end="")
		print("Value: ",self.value)
	
	
	#Used to print the entire tree of a node
	def printTree(self,numSpaces):
		printclass = ""
		printname = self.attr
		for x in self.branches:
			print(" | "*numSpaces,end="")
			if (printname != "NONE"):
				if (len(x.branches) != 0):
					print(printname,"=",x.valueName,":")
				else:
					print(printname,"=",x.valueName,":",x.decision)
			x.printTree(numSpaces+1)
	
#Function to find #samples of each class
def findValues(data,rowSamples):
	classcol = len(data[0])-1
	classvalues = [0,0];
	
	for x in rowSamples:
		if(data[x][classcol]=='0'):
			classvalues[0]+=1
		elif(data[x][classcol]=='1'):
			classvalues[1]+=1
	return classvalues

#Calculate impurity
def impurity(set,testingrows,classcolumn,heuristic):
	#testing rows = list containing examples being tested
	classzero = 0
	classone = 0
	
	#Go through examples to get the class values
	for rownum in testingrows:
		if (set[rownum][classcolumn] == '0'):
			classzero+=1
		elif (set[rownum][classcolumn] == '1'):
			classone+=1
	
	no = classzero/float(len(testingrows))
	yes = classone/float(len(testingrows))

	
	#Calculate VI depending on heuristic
	VI=0
	if (heuristic == "H1"):
		if (no!=0 and yes!= 0):
			VI = (-no*math.log2(no))-(yes*math.log2(yes))
	elif (heuristic == "H2"):
		VI=no*yes
		
	return VI

#Function to calculate gain/impurity heuristic
def Gain(set,attr,samples,heuristic):

	#Variables
	accum = 0
	attrList={}
	attrRows={}
	classcolum = len(set[0])-1
	
	#Find Attribute
	attrIndex = set[0].index(attr)
	
	#Samples contain the row index #s for the current sample
	#For loop to seperate the values in the attribute column
	for row in samples:
		key = set[row][attrIndex]
		if key in attrList.keys():
			attrList[key]+=1
			attrRows[key].append(row)
		else:
			attrList[key] = 1
			attrRows[key] = [row]
			
	for attrKey in attrList:
		attrKeyIG = impurity(set,attrRows[attrKey],classcolum,heuristic)
		accum+=(float(attrList[attrKey])/len(samples))*attrKeyIG
	
	TotalSet = impurity(set,samples,classcolum,heuristic)
	gain = TotalSet - accum
	return gain

#Build rest of tree starting from the root node
def recursivelybuildTree(parent,notSelected,rowSamples,data,attrValue,heuristic):
	#Base Case: No more Attributes in selection or in sample
	if (len(notSelected) == 0 or len(rowSamples) == 0):
		#Get the number of samples belonging to each class ie 0 or 1
		values = findValues(data,rowSamples)
		decision =  "0"
		if (values[1]>=values[0]):
			decision = "1"
		return Node("NONE",decision,rowSamples,values,attrValue)
	
	else:
		#If all examples belong to a class then a decision is made and it is a leaf node
		values = findValues(data,rowSamples)
		if (values.count(0) == len(values)-1):
			decision = "0"
			if (values[0]==0):
				decision = "1"
			return Node("NONE",decision,rowSamples,values,attrValue)
			
		#Otherwise go through List of best Attributes for this next node
		bestgain = -1
		bestattr = ""
	
		bestAttribute={}
	
		#Go through list of Attributes and find each of their gain
		for y in notSelected:
			infogain = Gain(data,data[0][y],rowSamples,heuristic)
			bestAttribute[data[0][y]] = infogain
			if (infogain>bestgain):
				bestgain=infogain
				bestattr = data[0][y]
	
		#Get the decision of the node
		decision = "0"
		if (values[1]>values[0]):
			decision = "1"
	
		#Remove Best attribute from list and seperate row samples
		bestattrIndex = data[0].index(bestattr)
		newlist = [attrNS for attrNS in notSelected if attrNS!=bestattrIndex]

		rowSamplePerAttr = {}
		rowindex = 0
	
		for index in rowSamples:
			key = data[index][bestattrIndex]
			if key in rowSamplePerAttr.keys():
				rowSamplePerAttr[key].append(index)
			else:
				rowSamplePerAttr[key] = [index]
		
		#If sample attr has no cases add in that sample attr
		if (len(rowSamplePerAttr) ==1):
			keyInBranch = list(rowSamplePerAttr.keys())[0]
			if (keyInBranch == "0"):
				rowSamplePerAttr["1"] = []
			elif (keyInBranch == "1"):
				rowSamplePerAttr["0"] = []
			
		#Add nodes branches to the parent node
		node = Node(bestattr,decision,rowSamples,values,attrValue)
		for attr in rowSamplePerAttr:
			node.branches.append(recursivelybuildTree(node,newlist,rowSamplePerAttr[attr],data,attr,heuristic))
			
		return node
		
#Build Root depending on the heuristic and call recursive function to build rest of tree
def Heuristic(data,rows,columns,heuristic):
	#Best Attribute Selection
	notSelected = list(range(0,columns))
	rowSamples = list(range(1,rows+1))
	bestgain = 0
	bestattr = ""
	
	bestAttribute={}
	
	#Go through list of Attributes and find each of their gain
	for y in notSelected:
		gain = Gain(data,data[0][y],rowSamples,heuristic)
		bestAttribute[data[0][y]] = gain
		if (gain>bestgain):
			bestgain=gain
			bestattr = data[0][y]
	
	#Get the number of samples belonging to each class ie 0 or 1
	values = findValues(data,rowSamples)
	decision = "0"
	if (values[1]>values[0]):
		decision =  "1"
	
	#Remove Best attribute from list and seperate row samples
	bestattrIndex = data[0].index(bestattr)
	notSelected.remove(bestattrIndex)

	rowSamplePerAttr = {}
	rowindex = 0
	
	for index in rowSamples:
		key = data[index][bestattrIndex]
		if key in rowSamplePerAttr.keys():
			rowSamplePerAttr[key].append(index)
		else:
			rowSamplePerAttr[key] = [index]
	
	#If sample attr has no cases add in that sample attr
	if (len(rowSamplePerAttr) ==1):
		keyInBranch = list(rowSamplePerAttr.keys())[0]
		if (keyInBranch == "0"):
			rowSamplePerAttr["1"] = []
		elif (keyInBranch == "1"):
			rowSamplePerAttr["0"] = []
			
	root = Node(bestattr,decision,rowSamples,values)
	
	for attr in rowSamplePerAttr:
		root.branches.append(recursivelybuildTree(root,notSelected,rowSamplePerAttr[attr],data,attr,heuristic))
	
	return root

#Function to travel through the entire tree for prediction
def TreeTraverse(node,attrnames,example):
	#If traversed through all attributes given return decision at the node
	if (example.count("n/a") == len(example)-1):
		return node.decision
		
	#Travel Through the tree
	else:
		#Get node attribute
		attribute = node.attr
		newExample = example.copy()
		#Find attribute in the attrnames list
		indexA = -1
		decision = ""
		if (attribute != "NONE"):
			indexA = attrnames.index(attribute)
			decision = example[indexA]
			newExample[indexA] = "n/a"
		
		#If node leaf node return
		if (node.isLeafNode()):
			return node.decision
		
		#Else go through rest of nodes
		else:
			#Look through branches to find the next path/node
			for x in node.branches:
				match = x.valueName
				if (match == decision):
					return TreeTraverse(x,attrnames,newExample)


#Function to predict based on root of tree and data given
def predict(root,data):
	rowSamples = list(range(1,len(data)))
	classcol = len(data[0])-1
	numCorrect = 0

	#Get number of correct predictions
	for row in rowSamples:
		answer = data[row][classcol]
		prediction = TreeTraverse(root,data[0],data[row])
		if (answer == prediction):
			numCorrect+=1
			
	#Return accuracy percentage
	accuracy =float(numCorrect)/len(rowSamples)
	return accuracy
		
		
#Function to read in file and return data and tree
def csvreading(filename,heuristic,buildTree="No"):
	#Open file with cvs_reader
	File = open(filename,'r')
	readingdata = csv.reader(File,delimiter=',')
	
	#Variables to count num of rows and columns
	data =[]
	columns =0 #num of attributes
	rows = -1 #num of examples since first row header
	
	#Put in data to 2-D List
	for row in readingdata:
		data.append(row)
		rows+=1
	
	columns =len(data[0])-1

	#Build Tree if training set data used else just return table of data
	if (buildTree == "Yes"):
			return Heuristic(data,rows,columns,heuristic),data
	elif (buildTree == "No"):
		return data
	

def main():
	#READ in from terminal of arguments: trainingdata.csv validation.csv test.csv yes/no H1/H2
#	print("\n\n---------")
	heuristic = sys.argv[5]
	toprint = sys.argv[4]
	
	if(not (toprint == "yes" or toprint == "no")):
		print("Foruth argument needs to be either yes or no")
		print(toprint)
		quit()
	if(not (heuristic == "H1" or heuristic == "H2")):
		print("Fifth argument needs to be either H1 or H2")
		quit()
		
	#Print out Accuracies
	print("DATASET")
	treeRoot,trainingdata = csvreading(sys.argv[1],heuristic,"Yes")
	validationData =csvreading(sys.argv[2],heuristic,"No")
	testData=csvreading(sys.argv[3],heuristic,"No")
	
	#Change beginning of sentence depending on heuristic type
	typeHeuristic = "H1"
	if(heuristic == "H2"):
		typeHeuristic = "H2"
		
	#Print out accuracies of the heuristic
	print(typeHeuristic,"NP train ",predict(treeRoot,trainingdata))
	print(typeHeuristic,"NP valid ",predict(treeRoot,validationData))
	print(typeHeuristic,"NP test  ",predict(treeRoot,testData))
	
	#Print out Tree
	if (toprint =="yes"):
		treeRoot.printTree(0)
		
	print("\n")
	
main()
