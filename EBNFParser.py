#!/usr/bin/python3
class ParseObjects:
	class ParseFail:
		def __init__(self,reason="No Error Message"):
			self.reason = reason
		def __str__(self):
			return "The parse failed because: "+self.reason
	class ESeq:
		def __init__(self,e1,e2):
			self.e1 = e1
			self.e2 = e2
		def __str__(self):
			return "ESeq("+str(self.e1)+","+str(self.e2)+")"
	class EName:
		def __init__(self,val1):
			self.val1 = val1
		def __str__(self):
			return "EName(\""+str(self.val1)+"\")"
	class ERules:
		def __init__(self,e1,e2):
			self.e1 = e1
			self.e2 = e2
		def __str__(self):
			return "ERules("+str(self.e1)+","+str(self.e2)+")"
	class EPart:
		def __init__(self,e1,e2):
			self.e1 = e1
			self.e2 = e2
		def __str__(self):
			return "EPart("+str(self.e1)+","+str(self.e2)+")"
	class ESymbs:
		def __init__(self,e1,e2):
			self.e1 = e1
			self.e2 = e2
		def __str__(self):
			return "ESymbs("+str(self.e1)+","+str(self.e2)+")"
	class EBnf:
		def __init__(self,e1,e2):
			self.e1 = e1
			self.e2 = e2
		def __str__(self):
			return "EBnf("+str(self.e1)+","+str(self.e2)+")"
	class ETerm:
		def __init__(self,value):
			self.val1 = value
		def __str__(self):
			return "ETerm(\""+self.val1+"\")"

class EBNFParser:
	def __init__(self):
		pass
	def parse(self,string):
		string=string.strip(" ").strip("\t")
		res = self.ESeq(string)
		if(res[1].strip()==""):
			return res[0]
		return ParseObjects.ParseFail("Didn't consume full input")
	def ESeq(self,string):
		string=string.strip(" ").strip("\t")
		res = self.EBnf(string)
		if isinstance(res,ParseObjects.ParseFail):
			return res
		def helper(exp,string):
			if(string == ""):
				return (exp,string)
			if(string[0]!="\n"):
				return exp,string
			res = self.EBnf(string[1:])
			if isinstance(res,ParseObjects.ParseFail):
				return (exp,string)
			return helper(ParseObjects.ESeq(exp,res[0]),res[1])
		return helper(*res)
	def EBnf(self,string):
		string=string.strip(" ").strip("\t")
		res = self.EName(string)
		if( isinstance(res,ParseObjects.ParseFail)):
			return res
		if(not res[1][:len("::=")] == "::="):
			return ParseFail("Expected a ::=")
		string = res[1][len("::="):]
		name = res[0]
		res = self.ERules(string)
		if isinstance(res,ParseObjects.ParseFail):
			return res
		return (ParseObjects.EBnf(name,res[0]),res[1])
	def EName(self,string):
		string=string.strip(" ").strip("\t")
		delim = ['"',':','=','|',"\\","}","{","\n"]
		i = 0
		for c in string:
			if c in delim:
				break
			i+=1
		if(i==0):
			return ParseObjects.ParseFail("Expected a name")
		return ParseObjects.EName(string[:i].strip()),string[i:]
	def ERules(self,string):
		string=string.strip(" ").strip("\t")
		res = self.EPart(string)
		if isinstance(res,ParseObjects.ParseFail):
			return res
		def helper(exp,string):
			if string=="":
				return (exp,string)
			if(string[0] != "|"):
				return (exp,string)
			res = self.EPart(string[1:])
			if isinstance(res,ParseObjects.ParseFail):
				return exp,string
			return helper(ParseObjects.ERules(exp,res[0]),res[1])
		return helper(*res)
	def EPart(self,string):
		string=string.strip(" ").strip("\t")
		res = self.ESymbs(string)
		if isinstance(res,ParseObjects.ParseFail):
			return res
		string = res[1]
		if string[0]!='{':
			return res
		start = res[0]
		res = self.ERules(string[1:])
		if isinstance(res,ParseObjects.ParseFail):
			return res
		if res[1][0] != '}':
			return ParseObjects.ParseFail("Expected }")
		return ParseObjects.EPart(start,res[0]),res[1][1:]
	def ESymbs(self,string):
		string=string.strip(" ").strip("\t")
		res = self.ESymb(string)
		if isinstance(res,ParseObjects.ParseFail):
			return res
		def helper(exp,string):
			if string == "":
				return exp,string
			res = self.ESymb(string)
			if isinstance(res,ParseObjects.ParseFail):
				return (exp,string)
			if res[1]==string:
				return exp,string
			return helper(ParseObjects.ESymbs(exp,res[0]),res[1])
		return helper(*res)
	def ESymb(self,string):
		string=string.strip(" ").strip("\t")
		res = self.ETerm(string)
		if isinstance(res,ParseObjects.ParseFail):
			return self.EName(string)
		return res
	def ETerm(self,string):
		string=string.strip(" ").strip("\t")
		if string[0]!='"':
			return ParseObjects.ParseFail('Expected "')
		ind = string[1:].index('"')+1
		while(string[ind-1]=='\\'):
			ind += string[ind+1:].index('"')+1
		return ParseObjects.ETerm(string[1:ind]),string[ind+1:]

if __name__=="__main__":
	with open("re.gram",'r') as f:
		grammar = f.read()
	parser = EBNFParser()
	print(parser.parse(grammar))
