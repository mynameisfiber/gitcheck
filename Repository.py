#!/bin/env python
import os
from hashlib import md5

class Repository:
  def __init__(self, location, GIT_PATH="/usr/bin"):
    self.GIT_PATH = GIT_PATH
    self.location = location
    self.name     = os.path.basename(self.location)

    self.update_repo()   
    self.remotes      = self.find_remotes()
    self.local_heads  = self.find_local_heads()

    self.updates = {}
    self.updates_keys = []
    self.check_updates()

  def has_updates(self):
    for key, data in self.updates.iteritems():
      if data["new"]:
        return True
    return False

  def get_new_updates(self):
    for key, data in self.updates.iteritems():
      if data["new"]:
        yield (key, data)
        data["new"] = False

  def check_updates(self):
    updates = {}
    hasupdate = self.get_new_updates()
    for remote,refs in self.remotes.iteritems():
      for head, checksum in refs.iteritems():
        try:
          if self.local_heads[head] != checksum:
            update = {}
            update["repo"] = self.name
            update["ref"] = "%s/%s"%(remote,head)
            update["desc"]  = self.get_commit_desc(remote, head)[0]
            update["desc"] = update["desc"][len(update["ref"])+3:].strip() #cleanup
            update["new"] = True
            key = md5(update["desc"]).hexdigest()

            if key not in self.updates_keys:
              self.updates_keys.append(key)
              self.updates.update( {md5(update["desc"]).hexdigest() : update} )
              hasupdate |= True
        except KeyError:
          pass
    return hasupdate

  def _run_git_cmd(self, cmd):
    pwd = os.getcwd()
    os.chdir(self.location)
    pd = os.popen("%s/git %s"%(self.GIT_PATH,cmd))
    mesg = pd.readlines()
    retval = pd.close()
    os.chdir(pwd)
    return {"retval" : retval, "mesg" : mesg}

  def get_commit_desc(self, remote, head):
    output = self._run_git_cmd("show-branch %s/%s"%(remote, head))
    if output["retval"] is None:
      return output["mesg"]
    else:
      return "Error: %s"%output["mesg"]

  def update_repo(self):
    output = self._run_git_cmd("remote update")
    if output["retval"] is not None:
      raise Exception("%s: Problem updating remote"%self.name)

  def find_local_heads(self):
    heads = {}
    path = os.path.join(self.location, ".git", "refs", "heads")
    for head in os.listdir(path):
      heads.update( {head : file(os.path.join(path,head)).readline().strip()} )
    return heads

  def find_remotes(self):
    remote_path = os.path.join(self.location, ".git", "refs", "remotes")
    remotes = {}
    try:
      for remote in os.listdir(remote_path):
        refs = {}
        refs_path = os.path.join(remote_path, remote)
        for ref in os.listdir(refs_path):
          refs.update( {ref : file(os.path.join(refs_path, ref)).readline().strip()} )
        remotes.update( {remote : refs} )
      return remotes
    except OSError:
      return {}
