# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
#  
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
#  
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@

import string
import stack.commands
from stack.exception import *

class command(stack.commands.HostArgumentProcessor,
	stack.commands.add.command):
        
	def serviceCheck(self, service):
		#
		# a service can look like:
		#
		#	reserved words: all
		#       named service: ssh
		#       specific port: 8069
		#       port range: 0:1024
		#
		if service == 'all':
			#
			# valid
			#
			return

		if service[0] in string.digits:
			#
			# if the first character is a number, then assume
			# this is a port or port range:
			#
			ports = service.split(':')
			if len(ports) > 2:
				msg = 'port range "%s" is invalid. ' % service
				msg += 'it must be "integer:integer"'
				raise CommandError(self, msg)

			for a in ports:
				try:
					i = int(a)
				except:
					msg = 'port specification "%s" ' % \
						service
					msg += 'is invalid. '
					msg += 'it must be "integer" or '
					msg += '"integer:integer"'
                                        raise CommandError(self, msg)
				
		#
		# if we made it here, then the service definition looks good
		#
		return


	def doParams(self):

		(service, network, outnetwork, chain, action, protocol, flags,
			comment, table, rulename) = self.fillParams([
				('service',		None,	True),
				('network',		None),
				('output-network',	None),
				('chain',		None,	True),
				('action',		None,	True),
				('protocol',		None,	True),
				('flags',		None),
				('comment',		None),
				('table',		'filter'),
				('rulename',		None),
			])
		
		if not network and not outnetwork:
                        raise ParamRequired(self, ('network', 'output-network'))

		if table not in [ 'filter', 'raw', 'mangle','nat']:
                        raise ParamError(self, 'table', 'is not valid')

		#
		# check if the network exists
		#
		if network == 'all':
			network = 0
		elif network:
			rows = self.db.execute("""select id from subnets where
				name = '%s'""" % (network))

			if rows == 0:
                                raise CommandError(self, 'network "%s" not in the database. Run "stack list network" to get a list of valid networks.' % network)

			network, = self.db.fetchone()
		else:
			network = 'NULL'

		if outnetwork == 'all':
			outnetwork = 0
		elif outnetwork:
			rows = self.db.execute("""select id from subnets where
				name = '%s'""" % (outnetwork))

			if rows == 0:
				raise CommandError(self, 'output-network "%s" not in the database. Run "stack list network" to get a list of valid networks.')

			outnetwork, = self.db.fetchone()
		else:
			outnetwork = 'NULL'

		self.serviceCheck(service)

		action = action.upper()
		chain = chain.upper()

		if protocol:
			protocol = '"%s"' % protocol
		else:
			protocol = 'NULL'

		if flags:
			flags = '"%s"' % flags
		else:
			flags = 'NULL'

		if comment:
			comment = '"%s"' % comment
		else:
			comment = 'NULL'

		if not rulename:
			import uuid
			rulename = "%s" % uuid.uuid1()

		return (service, network, outnetwork, chain, action,
			protocol, flags, comment, table, rulename)


	def checkRule(self, hierarchy, extrawhere, service, network, outnetwork,
		chain, action, protocol, flags, comment, table, rulename):

		query = 'select * from %s where name="%s"' % (hierarchy, rulename)
		rows  = self.db.execute(query)
		if rows:
			raise CommandError(self, 'Rule with rulename %s already exists' %
                                                   rulename)

		query = """select * from %s where %s
			service = '%s' and action = '%s' and chain = '%s' and
			if ('%s' = 'NULL', insubnet is NULL,
				insubnet = %s) and
			if ('%s' = 'NULL', outsubnet is NULL,
				outsubnet = %s) and
			if ('%s' = 'NULL', protocol is NULL,
				protocol = %s) and
			if ('%s' = 'NULL', flags is NULL,
				flags = %s) """ % (hierarchy, extrawhere, service,
			action, chain, network, network, outnetwork,
			outnetwork, protocol, protocol, flags, flags)
		rows  = self.db.execute(query)
		if rows:
			raise CommandError(self, 'firewall rule already exists')


	def insertRule(self, hierarchy, extracol, extraval, service, network,
		outnetwork, chain, action, protocol, flags, comment, table, rulename):

		#
		# all input has been verified. add the row
		#
		self.db.execute("""insert into %s
			(%s insubnet, outsubnet, service, protocol,
			action, chain, flags, comment, tabletype, name)
			values (%s %s, %s,'%s', %s, '%s', '%s', %s, %s,'%s','%s')""" %
			(hierarchy, extracol, extraval, network, outnetwork,
			service, protocol, action, chain, flags, comment, table, rulename))


class Command(command):
	"""
	Add a global firewall rule for the all hosts in the cluster.

	<param type='string' name='service' require='1'>
	The service identifier, port number or port range. For example
	"www", 8080 or 0:1024.
	To have this firewall rule apply to all services, specify the
	keyword 'all'.
	</param>

	<param type='string' name='protocol' require='1'>
	The protocol associated with the rule. For example, "tcp" or "udp".
	To have this firewall rule apply to all protocols, specify the
	keyword 'all'.
	</param>
	
        <param type='string' name='network'>
        The network this rule should be applied to. This is a named network
        (e.g., 'private') and must be one listed by the command
        'stack list network'.
	To have this firewall rule apply to all networks, specify the
	keyword 'all'.
	</param>

        <param type='string' name='output-network' optional='1'>
        The output network this rule should be applied to. This is a named
	network (e.g., 'private') and must be one listed by the command
        'stack list network'.
	</param>

        <param type='string' name='chain' require='1'>
	The iptables 'chain' this rule should be applied to (e.g.,
	INPUT, OUTPUT, FORWARD).
	</param>

        <param type='string' name='action' require='1'>
	The iptables 'action' this rule should be applied to (e.g.,
	ACCEPT, REJECT, DROP).
	</param>

	<param type='string' name='table'>
	The table to add the rule to. Valid values are 'filter',
	'nat', 'mangle', and 'raw'. If this parameter is not
	specified, it defaults to 'filter'
	</param>

	<param type='string' name='rulename'>
	The rule name for the rule to add. This is the handle by
	which the admin can remove or override the rule.
	</param>

	<example cmd='add firewall network=public service="ssh"
protocol="tcp" action="ACCEPT" chain="INPUT" flags="-m state --state NEW"
table="filter" rulename="accept_public_ssh"'>
	Accept TCP packets for the ssh service on the public network on
	the INPUT chain in the "filter" table and apply the "-m state --state NEW"
	flags to the rule.
	If 'eth1' is associated with the public network, this will be
	translated as the following iptables rule:
	"-A INPUT -i eth1 -p tcp --dport ssh -m state --state NEW -j ACCEPT"
	</example>

	<example cmd='add firewall network=private service="all" protocol="all" action="ACCEPT" chain="INPUT"'>
	Accept all protocols and all services on the private network on the
	INPUT chain.
	If 'eth0' is the private network, then this will be translated as
	the following iptables rule:
	"-A INPUT -i eth0 -j ACCEPT"
	</example>
	"""
	def run(self, params, args):
                
		(service, network, outnetwork, chain, action, protocol, flags,
                         comment, table, rulename) = self.doParams()

		self.checkRule('global_firewall', '', service, network,
			outnetwork, chain, action, protocol, flags, comment, table, rulename)

		self.insertRule('global_firewall', '', '', service, network,
			outnetwork, chain, action, protocol, flags, comment, table, rulename)
