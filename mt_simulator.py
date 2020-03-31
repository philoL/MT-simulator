
from name_tree import NameTree

TOP_DOWN = "top_down"
BOTTOM_UP = "bottom_up"
LPSR = "lpsr"

class MTSimulator():
	def __init__(self):
		self._name_tree = NameTree()
		self._ideal_ranks = {"r1": "/a"}
		self._update_scheme = None

	def __str__(self):
		return self._name_tree.__str__()

	def update_or_insert_rank(self, rank, name):
		self._ideal_ranks[rank] = name

	def insert_fib(self, name, rank):
		self._name_tree.insert_fib(name, rank)

	def count_fib(self):
		return self._name_tree.count_fib()

	def read_traffic_from_file(self, file_name):
		lines = open(file_name, "r").readlines()

		for line in lines:
			if line[-1] == "\n":
				line = line[:-1]
				rank = None
				if len(self._ideal_ranks) == 1 :
					rank = "r1"
				elif line.startswith(self._ideal_ranks["r2"]):
					rank = "r2"
				else:
					rank = "r1"

				# print(line, rank)
				# self._name_tree.mt_update_fib(line, rank)
				# self._name_tree.mt_update_pit(line, rank)
				self._name_tree.mt_update_accurate(line, rank)

