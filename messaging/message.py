#!/bin/env python

import threading

class message(threading.Thread):
  def __init__(self, config=None):
    threading.Thread.__init__(self)
    self.running = False
    self.config = config

  def send_message(self, title, message):
    pass

  def fresh_updates_message(self, updates):
    pass

  def new_updates_message(self, updates):
    pass

  def locked_remote_message(self, remotes):
    """remotes = (repo_raw, remote)"""
    pass

  def updates_message(self, updates):
    pass

	def start(self):
	  return False

	def exit(self):
	  self.running = False
