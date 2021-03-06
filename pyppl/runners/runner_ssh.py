import os
from getpass import getuser
from subprocess import check_output, list2cmdline

from .runner import runner
from ..helpers import utils


class runner_ssh (runner):
	"""
	The ssh runner

	@static variables:
		`serverid`: The incremental number used to calculate which server should be used.
		- Don't touch unless you know what's going on!

	"""
	serverid = 0

	def __init__ (self, job):
		"""
		Constructor
		@params:
			`job`:    The job object
			`config`: The properties of the process
		"""
		
		super(runner_ssh, self).__init__(job)
		# construct an ssh cmd
		sshfile      = self.job.script + '.ssh'

		conf         = {}
		if hasattr (self.job.proc, 'sshRunner'):
			conf     = self.job.proc.sshRunner
			
		if 'checkRunning' in conf:
			self.checkRunning = bool (conf['checkRunning'])
			
		if not 'servers' in conf:
			raise Exception ("%s: No servers found." % self.job.proc._name())
		
		servers      = conf['servers']

		serverid     = runner_ssh.serverid % len (servers)
		self.server  = servers[serverid]
		# TODO: check the server is alive?

		self.cmd2run = "cd %s; %s" % (os.getcwd(), self.cmd2run)
		sshsrc       = [
			'#!/usr/bin/env bash',
			''
			'trap "status=\\$?; echo \\$status > %s; exit \\$status" 1 2 3 6 7 8 9 10 11 12 15 16 17 EXIT' % self.job.rcfile
		]
		
		if 'preScript' in conf:
			sshsrc.append (conf['preScript'])
		
		keyfile = ''
		if 'keys' in conf:
			if not isinstance (conf['keys'], list) or len (conf['keys']) != len (servers):
				raise Exception ("%s: Key files for ssh runners must be a list corresponding to the servers." % self.job.proc._name())
			keyfile = '-i "%s"' % conf['keys'][serverid]
		sshsrc.append ('ssh %s %s "%s"' % (keyfile, self.server, self.cmd2run))
		
		if 'postScript' in conf:
			sshsrc.append (conf['postScript'])

		runner_ssh.serverid += 1
		
		with open (sshfile, 'w') as f:
			f.write ('\n'.join(sshsrc) + '\n')
		
		self.script = utils.chmodX(sshfile)


