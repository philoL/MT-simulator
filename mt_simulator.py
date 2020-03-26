
import collections

class Node():
	def __init__(self, value=None, level=0):
		self._value = value
		self._parent = None
		self._children = []
		self._fib = None
		self._meas = None
		self._level = level

	def __str__(self):
		return "name: %s, level: %d, fib: %s, meas: %s" % (self._value, self._level, self._fib, self._meas)

class Measurement():
	"""ranking: pit_counter, child_counter"""

	def __init__(self):
		self.rank_counters = dict()

	def __str__(self):
		return self.rank_counters.__str__()

class NameTree():

	def __init__(self):
		self._root = Node("/")

	def __str__(self):
		queue = [self._root]
		res = "---------- NameTree ---------\n"
		while queue:
			cur = queue.pop(0)
			res += cur._value + " : "
			for child in cur._children:
				res += child._value +","
				queue.append(child)
			res += "\n"
		res+= "------------------------------"
		return res

	def count_fib(self):
		count = 0
		queue = [self._root]

		while queue:
			cur = queue.pop(0)
			# print(cur)
			if cur._fib != None:
				count += 1
			for child in cur._children:
				queue.append(child)

		return count

	def find_fib(self, name):
		""" LPM is performed, return node that contains fib"""
		current = self._root
		fib_node = None
		components = name.split('/')

		for comp in components[1:]:
			if current._fib != None:
				fib_node = current

			comp_exists = False
			for child in current._children:
				if child._value == comp:
					current = child
					comp_exists = True
					break
			if not comp_exists:
				break

		return fib_node

	def insert_path(self, name):
		"""	give a name, insert a path into nt, each node is one component, return the inserted node"""
		components = name.split('/')
		current = self._root

		for comp in components[1:]:
			child_exists = False
			for child in current._children:
				if child._value == comp:
					current = child
					child_exists = True
					break

			if not child_exists:
				child = Node(comp, current._level+1)
				child._parent = current
				current._children.append(child)
				current = child

		return current


	def insert_fib(self, name, rank):
		""" name is composed with "/" to seperate components, e.g., /a/b/c """
		current = self.insert_path(name)
		current._fib = rank
		current._meas = Measurement()
		current._meas.rank_counters = (0,0)
		# print(current)

	def mt_update_fib(self, name, rank):
		"""
			find fib, check if fib_rank is the same as rank,
			if not, add a fib at fib+1 level with the new rank
		"""
		fib_node = self.find_fib(name)
		if fib_node._fib != rank:
			next_fib_node_name = "/".join(name.split("/")[:fib_node._level+2])
			# print("$$$", next_fib_node_name)
			next_fib_node = self.insert_path(next_fib_node_name)
			next_fib_node._fib = rank

	def mt_update_pit(self, name, rank):
		pass

	def mt_update_accurate(self, name, rank):
		pass


if __name__ == "__main__":
	#test basics
	nt = NameTree()
	nt.insert_fib("/a/b","r1")
	print(nt)
	print("FIB count: ", nt.count_fib())
	print(nt.find_fib("/a/b/c1/1"))

	#test mt_update_fib
	nt.mt_update_fib("/a/b/c1/d1/1", "r2")
	print(nt)
	print("FIB count: ", nt.count_fib())

	nt.mt_update_fib("/a/b/c1/d2/1", "r2")
	print(nt)
	print("FIB count: ", nt.count_fib())

	nt.mt_update_fib("/a/b/c1/d2/1", "r1")
	print(nt)
	print("FIB count: ", nt.count_fib())