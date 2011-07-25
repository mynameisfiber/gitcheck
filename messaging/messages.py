#!/bin/env python

import os
from os import path
import sys

class messages:
  def __init__(self, config):
    self.config       = config
    self.modules_name = []
    self.modules      = []
    self.messengers   = []
    self.load_modules()

  def load_modules(self):
    self.modules = []
    self.find_modules()
    for path in self.config["pluginpath"]:
      sys.path.append(path)
    for m in self.modules_name:
      try:
        tmp = __import__(m)
        self.modules.append(getattr(tmp,tmp.__modulename__)(self.config))
        self.modules[-1].start()
        print "Loaded module %s"%m
      except Exception as e:
        print "Failed to import module %s: %s"%(m,e)
        pass

  def find_modules(self):
    self.modules_name = []
    for pluginfolder in self.config["pluginpath"]:
      pluginfolder = path.expanduser(pluginfolder)
      for m in os.listdir(pluginfolder):
        fullm = path.join(pluginfolder, m)
        if path.isdir(fullm):
          print "Found modules: %s"%fullm
          self.modules_name.append(m)

  def send_message(self, title, message):
    for module in self.modules:
      module.send_message(title, message)

  def fresh_updates_message(self, updates):
    for module in self.modules:
      module.fresh_updates_message(updates)

  def new_updates_message(self, updates):
    for module in self.modules:
      module.new_updates_message(updates)

  def locked_remote_message(self, remotes):
    for module in self.modules:
      module.locked_remote_message(remotes)

  def updates_message(self, updates):
    for module in self.modules:
      module.updates_message(updates)

if __name__ == "__main__":
  config = {"pluginpath" : ["~/projects/gitcheck/messaging/",]}
  a = messages(config)
  print a.modules
