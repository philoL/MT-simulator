
import collections

PIT_THRESHOLD = 0

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
		self.rank_counters = collections.defaultdict(lambda : [ 0, 0])
		self._rank = None

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
				print(cur)
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
		# current._meas.rank_counters[rank] = [0,0]
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
		"""
			find fib, check if ranks are the same,
			if not add a fib at pit-1 level with the new rank
		"""
		fib_node = self.find_fib(name)
		if fib_node._fib != rank:
			pit_parent_name = "/".join(name.split("/")[:-1])
			next_fib_node = self.insert_path(pit_parent_name)
			next_fib_node._fib = rank

	def mt_update_accurate(self, name, rank):
		"""
			1. lookup FIB to find measurements
			2. increase PIT counter, if it reaches PIT_THRESHOLD follow the following steps
			3. traverse from FIB to name, insert measurements at each name component
			4, update or insert FIB to the first name prefix that has only one ranking
		"""
		fib_node = self.find_fib(name)

		rank_counters = fib_node._meas.rank_counters
		rank_counters[rank][0] += 1 # increment pit counter

		fib_inserted = None
		if rank != fib_node._fib: # insert a fib only when a new ranking is found
			fib_inserted = False
		else:
			fib_inserted = True

		if rank_counters[rank][0] >= PIT_THRESHOLD:
			# check if FIB update is needed at FIB level
			if len(fib_node._meas.rank_counters) == 1 and not fib_inserted: # only one rank, insert fib
				fib_node._fib = rank
				print("Updating FIB rank: ", fib_node)
				fib_inserted = True

			# insert measurements from fib to pit
			rest_componets = name.split('/')[fib_node._level+1:]
			current = fib_node

			for comp in rest_componets:
				child_exists = False
				for child in current._children:
					if child._value == comp: #child exists
						child_exists = True
						child._meas.rank_counters[rank][0] += 1 # update pit counter

						if len(child._meas.rank_counters) == 1 and not fib_inserted: # only one rank, insert fib
							child._fib = rank
							fib_inserted = True
							print("Inserting FIB at node:", child)
							self.mt_collapse_fib(child._parent)

				if not child_exists:
					#add a new node
					child = Node(comp, current._level+1)
					child._parent = current
					child._meas = Measurement()
					current._children.append(child)

					child._meas.rank_counters[rank][0] += 1 # update measurement
					if len(child._meas.rank_counters) == 1 and not fib_inserted: # only one rank, insert fib
						child._fib = rank
						fib_inserted = True
						print("Inserting FIB at node:", child)
						self.mt_collapse_fib(child._parent)

				current = child

	def mt_collapse_fib(self, node):
		"""
			when a new fib is updated or inserted, check if fib collapse is needed
			node is the parent of newly inserted FIB
			assuming two ranks
			this node should contain fib
		"""

		if node == self._root or node == None:
			return

		# check collapse conditions
		child_counter = {"r1":0,"r2":0}
		fib = None

		if node._fib == None:
			# find fib for this node
			current = node._parent
			while current:
				if current._fib != None:
					fib = current._fib
					break

			if not fib:	# at FIB case, no need to collapse upper
				return

		# case with no FIB at this node
		else:
			fib = node._fib

		# count children with different rankings
		for child in node._children:
			if child._fib != None:
				child_counter[child._fib] += 1
			else:
				child_counter[fib] += 1

		# if collapse is needed
		if child_counter['r1'] != child_counter['r2']:
			collapsed_fib = "r1" if child_counter['r1'] > child_counter['r2'] else "r2"

			if fib == collapsed_fib:
				print("--- deleting all child fib, because of", child_counter , " and node fib", fib)
				for child in node._children:
					if child._fib == collapsed_fib:
						child._fib = None
						print("deleting fib to child node", child)
			else:
				print("*** start collapsing, because of", child_counter, " and node fib", fib)
				for child in node._children:
					if child._fib == fib or child._fib == None: # expanding
						child._fib = fib
						print("adding fib to child node", child)
					else: # collapsing
						child._fib = None
						print("deleting fib to child node", child)
				if fib == "r1":
					node._fib = "r2"
				else:
					node._fib = "r1"
				print("adding fib to this node", node)

			# ranking reverting at this point check parents
			self.mt_collapse_fib(node._parent)

if __name__ == "__main__":
	#test basics
	nt = NameTree()
	nt.insert_fib("/a","r1")
	print(nt)
	print("FIB count:", nt.count_fib())
	# print("FIB node:", nt.find_fib("/a/b/c1/1"))

	#test mt_update_fib
	# nt.mt_update_fib("/a/b/c1/d1/1", "r2")
	# print(nt)
	# print("FIB count: ", nt.count_fib())

	# nt.mt_update_fib("/a/b/c1/d2/1", "r2")
	# print(nt)
	# print("FIB count: ", nt.count_fib())

	# nt.mt_update_fib("/a/b/c1/d2/1", "r1")
	# print(nt)
	# print("FIB count: ", nt.count_fib())

	#test mt_update_pit
	# print("\nmt_update_pit testing...")
	# nt.mt_update_pit("/a/b/c1/d1/1", "r1")
	# print(nt)
	# print("FIB count: ", nt.count_fib())

	# nt.mt_update_pit("/a/b/c1/d1/1", "r2")
	# print(nt)
	# print("FIB count: ", nt.count_fib())

	# nt.mt_update_pit("/a/b/c1/d2/1", "r1")
	# print(nt)
	# print("FIB count: ", nt.count_fib())

	# nt.mt_update_pit("/a/b/c1/d2/1", "r2")
	# print(nt)
	# print("FIB count: ", nt.count_fib())

	# mt_update_accurate test case 1
	# nt.mt_update_accurate("/a/b/c1/d1/1", "r2")
	# nt.mt_update_accurate("/a/b/c2/d1/1", "r1")
	# nt.mt_update_accurate("/a/b/c3/d1/1", "r1")
	# print("FIB count: ", nt.count_fib()) # should be 2

	# mt_update_accurate test case 2
	nt.mt_update_accurate("/a/b/c1/d1/1", "r2")
	nt.mt_update_accurate("/a/b2/c1/d1/1", "r1")
	nt.mt_update_accurate("/a/b3/c1/d1/1", "r1")
	nt.mt_update_accurate("/a/b/c2/d1/1", "r1")
	nt.mt_update_accurate("/a/b/c3/d1/1", "r1")
	print("FIB count: ", nt.count_fib()) # should be 2


