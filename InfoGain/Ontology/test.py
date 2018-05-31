class A:

	def __eq__(self, other):
		return self.name == other.name

	def __nq__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(self.name)

	def __init__(self,name, msg):
		self.name = name
		self.msg = msg

a, b = A("a", "welp"), A("a", "now")

c = set()
c.add(a)

[print(i.msg) for i in c]

c.add(b)

[print(i.msg) for i in c]
