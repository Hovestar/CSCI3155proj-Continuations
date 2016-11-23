#!/usr/bin/python3
from EBNFParser import ParseObjects,EBNFParser
"""
So how should this work?
Well I have the tree of the  grammar so I can generate an object for each rule. 
Then I have a few basic forms
Parse Below (return res) ESymb
concat (check res and get next part ESymbs
or (on failure find next res) ERules
EBNF (needs helper function) EPart
remove stuff (needs to shorten string) ETerm
"""
class ParseObj:
	def __init__(self,name,*args):
		self.name = name
		self.args = args
	def __str__(self):
		return self.name + ("" if len(self.args)==0 else ("("+",".join(map(lambda x: '"'+x+'"' if isinstance(x,str) else str(x),self.args))+")"))


class Parser:
	def __init__(self,grammar):
		"String with grammer is passed in in EBNF form to be read. Makes a parser object that can take arbitrary string and return fail or a parse tree"
		tree = EBNFParser().parse(grammar)
		rules = {}
		while isinstance(tree,ParseObjects.ESeq):
			rules[tree.e2.e1.val1] = tree.e2.e2
			tree = tree.e1
		rules[tree.e1.val1] = tree.e2
		self.rules = rules
	def parse(self,string):
		res = self.parser(string,self.rules["START"])
		if res[1]=="":
			return res[0][0]
		return ParseFail("Full input not consumed")
	def topLevel(self,string,name):
		res = self.parser(string,self.rules[name])
		if isinstance(res,ParseObjects.ParseFail):
			return res
		res,string = res
		if len(res) == 1 and not isinstance(res[0],str):
			return res,string
		return [ParseObj(name,*res)],string
	def parser(self,string,tree):
		if isinstance(tree,ParseObjects.EName):
			res = self.topLevel(string,tree.val1)
			if isinstance(res,ParseObjects.ParseFail):
				return res
			return res[0],res[1]
		if isinstance(tree,ParseObjects.ESymbs):
			res = self.parser(string,tree.e1)
			if isinstance(res,ParseObjects.ParseFail):
				return res
			part1 = res[0]
			string = res[1]
			res = self.parser(string,tree.e2)
			if isinstance(res,ParseObjects.ParseFail):
				return res
			return part1 + res[0],res[1]
		if isinstance(tree,ParseObjects.ERules):
			res = self.parser(string, tree.e1)
			if isinstance(res,ParseObjects.ParseFail):
				return self.parser(string,tree.e2)
			return res
		if isinstance(tree,ParseObjects.EPart):
			res = self.parser(string,tree.e1)
			if isinstance(res,ParseObjects.ParseFail):
				return res
			def helper(exp,string):
				if string == "":
					return exp,string
				res = self.parser(string,tree.e2)
				if isinstance(res,ParseObjects.ParseFail):
					return exp,string
				if res[1]==string:
					return exp,string
				return helper(exp+res[0],res[1])
			return helper(*res)
		if isinstance(tree,ParseObjects.ETerm):
			val = tree.val1
			if string[:len(val)]!=val:
				return ParseObjects.ParseFail("Expected "+val)
			return [val],string[len(val):]


if __name__=="__main__":
	with open("re.gram",'r') as f:
		text = f.read()
	parser = Parser(text)
	tmp = parser.parse("(a.?)*")
	print(tmp)
