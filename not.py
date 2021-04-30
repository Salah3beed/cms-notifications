#!/usr/bin/env python
from __future__ import print_function
import sys
from gi.repository import Notify
from argparse import ArgumentParser
import time
def _main():
	parser = ArgumentParser()
	parser.add_argument(
		'-n','--name', help='name', default="GUC-Notifications")
	parser.add_argument(
		'-i','--icon', help='icon ', default="")
	args = parser.parse_args()

	Notify.init("GUC-Notification")

	name = args.name

	notification = Notify.Notification.new (name)
	notification.show()

	lines_iterator = iter(sys.stdin.readline, b"")

	try:
		for line in lines_iterator:
			if line:
				print(line,end="")
				sys.stdout.flush()
				notification.update(name, line, args.icon)
				notification.show()
			else:
				break
			time.sleep(5)
	except KeyboardInterrupt:
		sys.exit(0)

if __name__ == '__main__':
	try:
		_main()
	except KeyboardInterrupt:
		sys.exit(0)
