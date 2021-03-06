import sys, unittest, os
rootdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, rootdir)
from pyppl import doct, proc

class TestDoct (unittest.TestCase):
	
	def testInit(self):
		d = {'a':1, 'b':2}
		dd = doct (d)
		self.assertIsInstance (dd, doct)
		
		ddd = doct (dd)
		self.assertIsInstance (ddd, doct)
		
		d2 = doct (a=1,b=2)
		self.assertEquals (d2, d)
		
	def testGetAttr (self):
		d = {'a':1, 'b':2}
		dd = doct (d)
		self.assertIsInstance (dd, doct)
		
		ddd = doct (dd)
		self.assertIsInstance (ddd, doct)
		
		d2 = doct (a=1,b=2)
		self.assertEquals (d2, d)
		
		self.assertEquals(dd.a, 1)
		self.assertEquals(dd['b'], 2)
		self.assertEquals(ddd['a'], 1)
		self.assertEquals(ddd.b, 2)
		
		d3 = doct ({'a': {'b':1}})
		self.assertEquals (d3.a.b, 1)
	
	def testSetAttr (self):
		d = doct()
		self.assertEquals (d, {})
		d.a = 1
		self.assertEquals (d, {'a':1})
		d.b = {}
		d.b.a = 1
		self.assertEquals (d, {'a': 1, 'b':{'a':1}})
		d.c = "c"
		d.c += '1'
		self.assertEquals (d['c'], 'c1')
		
		d = doct ()
		d.args = doct()
		d.args.samtools = "samtools"
		self.assertEquals (d.args.samtools, "samtools")
		
		p = proc ()
		p.args.samtools = "samtools"
		self.assertEquals (p.args.samtools, "samtools")
		
	def testDel (self):
		d = doct()
		self.assertEquals (d, {})
		d.a = 1
		self.assertEquals (d, {'a':1})
		del d.a
		self.assertEquals (d, {})
		d.a = 2
		self.assertEquals (d, {'a':2})
		d.a = None
		self.assertEquals (d, {'a': None})
		del d['a']
		self.assertEquals (d, {})
		d.a = {}
		d.a.b = 1
		self.assertEquals (d, {'a':{'b':1}})
		del d.a.b
		self.assertEquals (d, {'a':{}})
		
	def testCopy(self):
		a = {'a':1, 'b':2, 'c':3}
		d = doct(a)
		d.c=1
		self.assertEquals (d.c, 1)
		self.assertEquals (a['c'], 3)
		
		d2 = doct (d)
		d2.c = 2
		self.assertEquals (d.c, 1)
		self.assertEquals (d2.c, 2)
		
		d3 = d2
		d3.c = 4
		self.assertEquals (d3.c, 4)
		self.assertEquals (d2.c, 4)
		
		
		
		

if __name__ == '__main__':
	unittest.main()