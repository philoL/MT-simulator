
from name_tree import NameTree
from itertools import permutations

class TrafficGenerator():

	def __init__(self, depth = 5, out = 3, file_name = None):
		self._depth = depth
		self._out = out
		self._one_set = []
		self._sets = []
		self._fib = {"/a":"r1"}
		self._file_name = file_name

	def insert_fib(self, prefx, rank):
		self._fib[prefx] = rank

	def generate_one_set(self):
		if self._file_name == None:
			sys.exit("Please configure traffic file name first!")

		lines = open(self._file_name, "r").readlines()

		for line in lines:
			if line[-1] == "\n":
				line = line[:-1]
			self._one_set.append(line)
		print("read from traffic from file: ", self._one_set)

	def permulate(self, l, r):
		if l == r:
			self._sets.append(self._one_set)
		else:
			_set = self._one_set[l]
			for i in range(l, r+1):
				_set[l], _set[i] = _set[i], _set[l]
				self.permulate(l+1, r)
				_set[l], _set[i] = _set[i], _set[l]

	def generate_all_sets(self):
		self.generate_one_set()
		self._sets = list(permutations(self._one_set))
		print("all sets: \n", self._sets)

tg = TrafficGenerator(file_name = "traffic/test_traffic.txt")
tg.generate_all_sets()