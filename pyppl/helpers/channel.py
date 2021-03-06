"""
Channel for pyppl
"""
from copy import copy as pycopy
from . import utils

class channel (list):
	"""
	The channen class, extended from `list`
	"""
	
	@staticmethod
	def create (l = None):
		"""
		Create a channel from a list
		@params:
			`l`: The list, default: []
		@returns:
			The channel created from the list
		"""
		if l is None: 
			l = []
		ret = channel()
		for e in l:
			ret.append (channel._tuplize(e))
		return ret

	@staticmethod
	def fromChannels (*args):
		"""
		Create a channel from channels
		@params:
			`args`: The channels
		@returns:
			The channel merged from other channels
		"""
		ret = channel.create()
		ret.merge (*args)
		return ret
	
	@staticmethod
	# t = 'dir', 'file', 'link' or 'any'
	def fromPath (pattern, t = 'any'):
		"""
		Create a channel from a path pattern
		@params:
			`pattern`: the pattern with wild cards
			`t`:       the type of the files/dirs to include
		@returns:
			The channel created from the path
		"""
		from glob import glob
		ret = channel.create(sorted(glob(pattern)))
		if t != 'any':
			from os import path
		if t == 'link':
			return ret.filter (path.islink)
		elif t == 'dir':
			return ret.filter (path.isdir)
		elif t == 'file':
			return ret.filter (path.isfile)
		return ret

	@staticmethod
	def fromPairs (pattern):
		"""
		Create a width = 2 channel from a pattern
		@params:
			`pattern`: the pattern
		@returns:
			The channel create from every 2 files match the pattern
		"""
		from glob import glob
		ret = sorted(glob(pattern))
		c = channel.create()
		for i in range(0, len(ret), 2):
			c.append ((ret[i], ret[i+1]))
		return c
	
	@staticmethod
	def fromFile (fn, delimit = "\t"):
		"""
		Create channel from the file content
		It's like a matrix file, each row is a row for a channel.
		And each column is a column for a channel.
		@params:
			`fn`:      the file
			`delimit`: the delimit for columns
		@returns:
			A channel created from the file
		"""
		ret = channel.create()
		with open (fn) as f:
			for line in f:
				line = line.strip()
				if not line: 
					continue
				row = line.split(delimit)
				ret.rbind (row)
		return ret

	@staticmethod
	def fromArgv ():
		"""
		Create a channel from `sys.argv[1:]`
		"python test.py a b c" creates a width=1 channel
		"python test.py a,1 b,2 c,3" creates a width=2 channel
		@returns:
			The channel created from the command line arguments
		"""
		from sys import argv
		ret  = channel.create()
		args = argv[1:]
		alen = len (args)
		if alen == 0: 
			return ret
		
		width = None
		for arg in args:
			items = tuple(utils.split(arg, ','))
			if width is not None and width != len(items):
				raise ValueError('Width %s (%s) is not consistent with previous %s' % (len(items), arg, width))
			width = len(items)
			ret.append (items)
		return ret
	
	@staticmethod
	def _tuplize (tu):
		"""
		A private method, try to convert an element to tuple
		If it's a string, convert it to `(tu, )`
		Else if it is iterable, convert it to `tuple(tu)`
		Otherwise, convert it to `(tu, )`
		Notice that string is also iterable.
		@params:
			`tu`: the element to be converted
		@returns:
			The converted element
		"""
		if isinstance(tu, utils.basestring):
			tu = (tu, )
		else:
			try: 
				iter(tu)
			except Exception:	
				tu = (tu, )
		#return tuple(tu)
		return (tu, ) if isinstance(tu, list) else tuple (tu) 

	
	def expand (self, col = 0, pattern = "*"):
		"""
		expand the channel according to the files in <col>, other cols will keep the same
		`[(dir1/dir2, 1)].expand (0, "*")` will expand to
		`[(dir1/dir2/file1, 1), (dir1/dir2/file2, 1), ...]`
		length: 1 -> N
		width:  M -> M
		@params:
			`col`:     the index of the column used to expand
			`pattern`: use a pattern to filter the files/dirs, default: `*`
		@returns:
			The expanded channel
			Note, self is also changed
		"""
		from glob import glob
		import os
		folder = self[0][col]
		files  = glob (os.path.join(folder, pattern))
		
		tmp = list (self[0])
		for i, f in enumerate(files):
			n = pycopy(tmp)
			n [col] = f
			if i == 0:
				self[i] = tuple(n)
			else:
				self.append (tuple(n))
		return self
		
	def collapse (self, col = 0):
		"""
		Do the reverse of expand
		length: N -> 1
		width:  M -> M
		@params:
			`col`:     the index of the column used to collapse
		@returns:
			The collapsed channel
			Note, self is also changed
		"""
		if self.length() == 0:
			raise ValueError('Cannot collapse an empty channel.')
		
		from os.path import dirname, sep, commonprefix
		compx = sep
		row = list(self[0])
		if self.length() == 1:
			path  = row[col]
			compx = dirname (path)
		else:
			paths = self.colAt(col).toList()
			compx = dirname(commonprefix(paths))
		row[col] = compx
		self = channel.create([tuple(row)])
		return self
	
	def copy (self):
		"""
		Copy a channel using `copy.copy`
		@returns:
			The copied channel
		"""
		return pycopy(self)

	def width (self):
		"""
		Get the width of a channel
		@returns:
			The width of the channel
		"""
		if not self: 
			return 0
		ele = self[0]
		if not isinstance(ele, tuple): 
			return 1
		return len(ele)
	
	def length (self):
		"""
		Get the length of a channel
		It's just an alias of `len(chan)`
		@returns:
			The length of the channel
		"""
		return len (self)

	def map (self, func):
		"""
		Alias of python builtin `map`
		@params:
			`func`: the function
		@returns:
			The transformed channel
		"""
		return channel.create(map(func, self))

	def filter (self, func):
		"""
		Alias of python builtin `filter`
		@params:
			`func`: the function
		@returns:
			The transformed channel
		"""
		return channel.create(filter(func, self))

	def reduce (self, func):
		"""
		Alias of python builtin `reduce`
		@params:
			`func`: the function
		@returns:
			The transformed channel
		"""
		return channel.create(utils.reduce(func, self))
	
	def _rbindOne(self, row):
		"""
		Like R's rbind, do a row bind to a channel
		@params:
			`row`: the row to be bound to channel
		@returns:
			The combined channel
			Note, self is also changed
		"""
		row = utils.range2list (row)
		if not isinstance (row, list) and not isinstance(row, tuple):
			row = [row]
		if len(row) == 1:
			row = row * max(1, self.width())
		if self.width() == 0 or self.width() == len (row):
			self.append (tuple(row))
		else:
			raise ValueError ('Cannot bind row (len: %s) to channel (width: %s): width is different.' % (len(row), self.width()))
		return self
	
	def rbind (self, *rows):
		"""
		The multiple-argument versoin of `rbind`
		@params:
			`rows`: the rows to be bound to channel
		@returns:
			The combined channel
			Note, self is also changed
		"""
		for row in rows: 
			if isinstance(row, channel):
				for r in row:
					self._rbindOne(r)
			else:
				self._rbindOne(row)
		return self
	
	def _cbindOne (self, col):
		"""
		Like R's cbind, do a column bind to a channel
		@params:
			`col`: the column to be bound to channel
		@returns:
			The combined channel
			Note, self is also changed
		"""
		col = utils.range2list(col)
		if not isinstance(col, list): 
			col = [col]
		if len (col) == 1: 
			col = col * max(1, self.length())
		if self.length() == 0 :
			for ele in col: 
				self.append (channel._tuplize(ele))
		elif self.length() == len (col):
			for i in range (self.length()):
				self[i] += channel._tuplize(col[i])
		else:
			raise ValueError ('Cannot bind column (len: %s) to channel (length: %s): length is different.' % (len(col), self.length()))
		return self
	
	def cbind (self, *cols):
		"""
		The multiple-argument versoin of `cbind`
		@params:
			`cols`: the columns to be bound to channel
		@returns:
			The combined channel
			Note, self is also changed
		"""
		for col in cols:
			self._cbindOne(col)
		return self
		
	def merge (self, *chans):
		"""
		Also do column bind, but with channels, and also you can have multiple with channels as arguments
		@params:
			`chans`: the channels to be bound to channel
		@returns:
			The combined channel
			Note, self is also changed
		"""
		for chan in chans:
			if not isinstance(chan, channel): 
				chan = channel.create(chan)
			cols = [x.toList() for x in chan.split()]
			self.cbind (*cols)
		return self
	
	def colAt (self, index):
		"""
		Fetch one column of a channel
		@params:
			`index`: which column to fetch
		@returns:
			The channel with that column
		"""
		return self.slice (index, 1)
	
	def slice (self, start, length = None):
		"""
		Fetch some columns of a channel
		@params:
			`start`:  from column to start
			`length`: how many columns to fetch, default: None (from start to the end)
		@returns:
			The channel with fetched columns
		"""
		if start is None: 
			start = self.width()
		if length is None: 
			length = self.width()
		if start < 0: 
			start = start + self.width()
		if start >= self.width(): 
			return channel.create()
		ret = channel.create()
		if length == 0: 
			return ret
		for ele in self:
			row = ele[start:start+length]
			ret.rbind (row)
		return ret
	
	def insert (self, index, col):
		"""
		Insert a column to a channel
		@params:
			`index`:  at which position to insert
			`col`:    The column to be inserted
		@returns:
			The channel with the column inserted
			Note, self is also changed
		"""
		col = utils.range2list(col)
		if not isinstance(col, list): 
			col = [col]
		if len (col) == 1: 
			col = col * max(1, self.length())
		part1 = self.slice (0, index)
		part2 = self.slice (index)
		del self[:]
		self.merge (part1)
		self.cbind (col)
		self.merge (part2)
		return self
	
	def fold (self, n = 1):
		"""
		Fold a channel. Make a row to n-length chunk rows
		```
		a1	a2	a3	a4
		b1	b2	b3	b4
		if n==2, fold(2) will change it to:
		a1	a2
		a3	a4
		b1	b2
		b3	b4		
		```
		@params:
			`n`: the size of the chunk
		@returns
			The new channel
		"""
		if self.width()%n != 0:
			raise ValueError ('Failed to fold, the width %s cannot be divided by %s' % (self.width(), n))
		ret = channel.create()
		for row in self:
			for i in [x*n for x in range(int(self.width()/n))]:
				ret.rbind (row[i:i+n])
		return ret
	
	def unfold (self, n = 2):
		"""
		Do the reverse thing as self.fold does
		@params:
			`n`: How many rows to combind each time. default: 2
		@returns:
			The unfolded channel
		"""
		if self.length()%n != 0:
			raise ValueError ('Failed to unfold, the length %s cannot be divided by %s' % (self.width(), n))
		ret = channel.create()
		for i in [x*n for x in range(int(self.length()/n))]:
			ret.rbind (utils.reduce (lambda x, y: x+y, self[i:i+n]))
		return ret
	
	def split (self):
		"""
		Split a channel to single-column channels
		@returns:
			The list of single-column channels
		"""
		return [ self.colAt(i) for i in range(self.width()) ]
	
	def toList (self): # [(a,), (b,)] to [a, b], only applicable when width =1
		"""
		Convert a single-column channel to a list (remove the tuple signs)
		`[(a,), (b,)]` to `[a, b]`, only applicable when width=1
		@returns:
			The list converted from the channel.
		"""
		if self.width() != 1:
			raise ValueError ('Width = %s, but expect width = 1.' % self.width())
		
		return [ e[0] if isinstance(e, tuple) else e for e in self ]

