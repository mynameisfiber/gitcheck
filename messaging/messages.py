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
        self.modules.append(m)
        print "Loaded module %s"%m
      except ImportError as e:
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

if __name__ == "__main__":
  config = {"pluginpath" : ["~/projects/gitcheck/messaging/",]}
  a = messages(config)
  print a.modules
