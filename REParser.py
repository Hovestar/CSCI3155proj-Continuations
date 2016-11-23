#!/usr/bin/python3
class ParseFail:
	pass

class RNoString:
	def __str__(self):
		return "RNoString"
class REmptyString:
	def __str__(self):
		return "REmptyString"
class RAnyChar:
	def __str__(self):
		return "RAnyChar"
class RSingle:
	def __init__(self,c):
		self.c = c
	def __str__(self):
		return "RSingle(\""+self.c+"\")"
class RConcat:
	def __init__(self,re1, re2):
		self.re1 = re1
		self.re2 = re2
	def __str__(self):
		return "RConcat("+str(self.re1)+", "+str(self.re2)+")"
class RUnion:
	def __init__(self,re1, re2):
		self.re1 = re1
		self.re2 = re2
	def __str__(self):
		return "RUnion("+str(self.re1)+", "+str(self.re2)+")"
class RStar:
	def __init__(self,re1):
		self.re1 = re1
	def __str__(self):
		return "RStar("+str(self.re1)+")"
class RPlus:
	def __init__(self,re1):
		self.re1 = re1
	def __str__(self):
		return "RPlus("+str(self.re1)+")"
class ROption:
	def __init__(self,re1):
		self.re1 = re1
	def __str__(self):
		return "ROption("+str(self.re1)+")"
class RIntersect:
	def __init__(self,re1, re2):
		self.re1 = re1
		self.re2 = re2
	def __str__(self):
		return "RIntersect("+str(self.re1)+", "+str(self.re2)+")"
class RNeg:
	def __init__(self,re1):
		self.re1 = re1
	def __str__(self):
		return "RNeg("+str(self.re1)+")"

class REParser():
	def __init__(self,):
		pass
	def re(self,string):
		return self.union(string)
	
	def union(self,string):
		res = self.intersect(string)
		if(isinstance(res,ParseFail)):
			return res
		def unions(re,string):
			if(string == ""):
				return (re,string)
			if(string[0]!="|"):
				return (re,string)
			res = self.intersect(string[1:])
			if(isinstance(res,ParseFail)):
				return res
			return unions(RUnion(re,res[0]),res[1])
		return unions(*res)
	
	def intersect(self,string):
		res = self.concat(string)
		if(isinstance(res,ParseFail)):
			return res
		def intersects(acc,string):
			if(string == ""):
				return (acc,string)
			if(string[0] != "&"):
				return (acc,string)
			res = self.concat(string[1:])
			if(isinstance(res,ParseFail)):
				return res
			return intersects(RIntersect(re,res[0]),res[1])
		return intersects(*res)
	
	def concat(self,string):
		res = self.Not(string)
		if isinstance(res,ParseFail):
			return res
		def concats(acc,string):
			if(string == ""):
				return (acc,string)
			res = self.Not(string)
			if isinstance(res,ParseFail):
				return (acc,string)
			return concats(RConcat(acc,res[0]),res[1])
		return concats(*res)
	
	def Not(self,string):
		res = self.star(string)
		if not isinstance(res,ParseFail):
			return res
		if(string[0] != "~"):
			return res
		res = self.Not(string[1:])
		if isinstance(res,ParseFail):
			return res
		return (RNeg(res[0]),res[1])
	
	def star(self,string):
		res = self.atom(string)
		if isinstance(res,ParseFail):
			return res
		def stars(acc,string):
			if(string == ""):
				return (acc,string)
			first = string[0]
			rest = string[1:]
			if(first=="*"):
				return stars(RStar(acc),rest)
			elif(first=="?"):
				return stars(ROption(acc),rest)
			elif(first=="+"):
				return stars(RPlus(acc),rest)
			else:
				return (acc,string)
		return stars(*res)
	
	def atom(self,string):
		delimiters = set(['|', '&', '~', '*', '+', '?', '!', '#', '.', '(', ')'])
		if string[0] == "#":
			return (REmptyString(),string[1:])
		if string[0] == "!":
			return (RNoString(),string[1:])
		if string[0] == ".":
			return (RAnyChar(), string[1:])
		if string[0] == "(":
			res = self.union(string[1:])
			if isinstance(res,ParseFail):
				return res
			string = res[1]
			re = res[0]
			if(string[0]==")"):
				return (re,string[1:])
			return ParseFail()
		if string[0] not in delimiters:
			return (RSingle(string[0]),string[1:])
		else:
			return ParseFail()

if __name__=="__main__":
	parser = REParser()
	res = parser.re("(a.?)*")
	print(res[0])
