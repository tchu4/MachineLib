HW1

Declaration:
I have done this assignment completely on my own. I have not copied it, nor have I given my solution to anyone else. I understand that if I am involved in plagiarism or cheating I will have to sign an official form that I have cheated and that this form will be stored in my official university record. I also understand that I will receive a grade of 0 for the involved assignment for my first offense and that I will receive a grade of “F” for the course for any additional offense.

Teresa Chu

Language Used: Python

Instructions on Compiling
	Arguments needed:
		1)CSV file containing training data
		2)CSV file containing validation data
		3)CSV file containing test data
		4)Yes or no where 
			yes means the tree will be printed 
			no means the tree will not be printed
			*Please note that yes and no must be lowercase*
		5)H1 or H2 where 
			H1 = Information Gain Heuristic
			H2 = Variance Impurity Heuristic
	Compiling
		Needs to be run with python3
		There are issues with printing when run just with python
		
	Example of running code: 
		python3 program.py training_set.csv validation_set.csv test_set.csv yes H2
		python3 program.py training_set.csv validation_set.csv test_set.csv no H1

Notes
	In training set 2, where there were some noise in the data, I have it set that if the probability between the two classes is equal, then the decision is set to be class 1. This also includes instances where there were no samples of the other choice. For example, if for the last attribute chosen is XA and all samples left in there have attribute 0 so there are no samples with the opposing attribute 1, then we add in a node for that attribute and set the decision of that attribute to be 1. In this case, we treat the noise  as another value.
		 

