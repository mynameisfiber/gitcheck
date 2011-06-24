#!/bin/env python

import pynotify
import os
from Repository import Repository
from time import sleep

_CONFIG = {"MAXDEPTH"        : 20,
           "GIT_PATH"        : "/usr/bin",
           "project_folders" : ['~/projects/',],
           "icon"            : "git.svg",
           "check_freq"      : 300}

def find_repo(folder, maxdepth=-1):
  results = []
  if maxdepth == 0:
    return results
  folder = os.path.expanduser(folder)
  for item in os.listdir(folder):
    full_item = os.path.join(folder, item)
    if os.path.isdir(full_item):
      if item == ".git":
        results.append(folder)
      else:
        results += find_repo(full_item,maxdepth-1)
  return results

def show_message(title, message,icon="git.svg"):
  icon = os.path.join(os.getcwd(),icon)
  msg = pynotify.Notification(title, 
                              message,
                              icon)
  if not msg.show():
    print "Could not display message: (%s) %s"%(title, message)
                        

if __name__ == "__main__":
  if not pynotify.init ("icon-summary-body"):
    print "Could not initialize notification system"
    exit(1)

  repos = []
  for project_folder in _CONFIG["project_folders"]:
    raw_repos = find_repo(project_folder, maxdepth=_CONFIG["MAXDEPTH"])
    for raw_repo in raw_repos:
      repos.append(Repository(raw_repo,GIT_PATH=_CONFIG["GIT_PATH"]))

  while True:
    for repo in repos:
      if repo.check_updates():
        for key, update in repo.get_new_updates():
          print update
          show_message(update["repo"], update["desc"])
    sleep(_CONFIG["check_freq"])
