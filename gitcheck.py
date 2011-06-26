#!/bin/env python

_CONFIG = {"GIT_PATH"        : None,  #None = use system $PATH
           "project_folders" : [('~/projects/',       1),
                                ('~/Documents/code/', 5)],
           "icon"            : "git.svg",
           "check_freq"      : 5}

import signal
import os
from Repositories import Repositories
from time import sleep
import threading

try:
  import pynotify
  if not pynotify.init("icon-summary-body"):
    print "Could not initialize notification system"
    pynotify = None
except ImportError:
  pynotify = None
try:
  import growl
  growlNotifier = growl.GrowlNotifier("gitcheck",['Repo modified'])
  growlNotifier.register()
except:
  growl = None
  growlNotifier = None

try:
  from gui import gtktoolbar
  gtkinstance = gtktoolbar.Indicator(_CONFIG["icon"])
  gtkinstance.start()
  signal.signal(signal.SIGTERM, gtkinstance.exit)
  signal.signal(signal.SIGINT, gtkinstance.exit)
except ImportError:
  gtkinstance = None

class gitcheck(threading.Thread):
  def __init__(self, config):
    threading.Thread.__init__(self)
    self.config = config
    self.running = False

    self.repositories = None
    self.setup_repos()

  def setup_repos(self):
    self.repositories = Repositories(config=self.config)
    for project_folder, MAXDEPTH in self.config["project_folders"]:
      project_folder = os.path.expanduser(project_folder)
      if os.path.exists(project_folder):
        raw_repos = self.find_repo(project_folder, maxdepth=MAXDEPTH)
        for raw_repo in raw_repos:
          self.repositories.add_repository(raw_repo)

  def warn_locked(self):
    for repo, remote in self.repositories.get_locked_remotes():
      print "Warning", "%s: remote '%s' is not updatable.  Check that a passwordless SSH key exists for this remote"%(name, remote)

  def run(self):
    self.running = True
    while self.running:
      print "Checking for updates"
      self.repositories.update_repositories()
      #self.show_gui_updates(self.repositories.get_fresh_updates())
      print "Going through new updates"
      for key, update in self.repositories.get_new_updates():
        print "Is this actually new? ", update["new"]
        self.show_message("Update to %s"%update["repo"], "[%s]\n%s"%(update["ref"],update["desc"]),{key:update})
      sleep(_CONFIG["check_freq"])
      self.repositories.refresh_repositories()

  def find_repo(self, folder, maxdepth=-1):
    results = []
    if maxdepth == 0:
      return results
    folder = os.path.expanduser(folder)
    for item in os.listdir(folder):
      full_item = os.path.join(folder, item)
      if os.path.isdir(full_item):
        gitlocation = os.path.join(full_item, ".git")
        if os.path.isdir(gitlocation):
          results.append(full_item)
        else:
          results += self.find_repo(full_item,maxdepth-1)
    return results
  
  def show_message(self, title, message, update=None, icon="git.svg"):
    icon = os.path.join(os.getcwd(),icon)
    message = message.replace('&', '&amp;')
    message = message.replace('<', '&lt;')
    message = message.replace('>', '&gt;')
  
    print "%s: %s"%(title, message)
    if pynotify is not None:
      msg = pynotify.Notification(title, 
                                  message,
                                  icon)
      try:
        if not msg.show():
          print "Could not display message: (%s) %s"%(title, message)
      except:
        print "Error communicating with notification daemon"
  
    if growlNotifier is not None:
      growlNotifier.notify('Repo modified',title,message)
                        

if __name__ == "__main__":
  checker = gitcheck(_CONFIG)
  checker.start()
  
