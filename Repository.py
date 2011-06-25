#!/bin/env python
import os
from hashlib import md5
from time import time
import subprocess

class Repository:
  def __init__(self, location, GIT_PATH="/usr/bin"):
    self.GIT_PATH = GIT_PATH
    self.location = location
    self.name     = os.path.basename(self.location)

    self.lockedremote = []
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
    hasupdate = self.has_updates()
    for remote,refs in self.remotes.iteritems():
      for head, checksum in refs.iteritems():
        try:
          if self.local_heads[head] != checksum:
            try:
              update = {}
              update["repo"] = self.name
              update["ref"] = "%s/%s"%(remote,head)
              update["desc-full"]  = self.get_commit_desc(remote, head)
              update["desc"] = update["desc-full"][len(update["ref"])+3:].strip() #cleanup
              update["timestamp"] = time()
              update["new"] = True
              key = md5(update["desc"]).hexdigest()

              if key not in self.updates_keys:
                self.updates_keys.append(key)
                self.updates.update( {md5(update["desc"]).hexdigest() : update} )
                hasupdate |= True
            except:
              pass
        except KeyError:
          pass
    return hasupdate

  def _run_git_cmd(self, cmd):
    try:
      env = {"GIT_SSH":os.path.join(os.getcwd(),"ssh_wrapper")}
      pd = subprocess.Popen(("%s/git %s"%(self.GIT_PATH,cmd)).split(), 
                            stdin=subprocess.PIPE, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            cwd=self.location, 
                            env=env)
      mesg = pd.stdout.readlines()
      pd.wait()
      retval = pd.returncode
    except subprocess.CalledProcessError, e:
      mesg = e.output
      retval = e.returncode
    return {"retval" : retval, "mesg" : mesg}

  def get_commit_desc(self, remote, head):
    output = self._run_git_cmd("show-branch %s/%s"%(remote, head))
    if output["retval"] == 0:
      return output["mesg"][0].strip()
    else:
      raise Exception(("Error: retval = %d"%output[retval])+output["mesg"])

  def update_repo(self):
    remote_path = os.path.join(self.location, ".git", "refs", "remotes")
    remotes = {}
    try:
      for remote in os.listdir(remote_path):
        output = self._run_git_cmd("remote update %s"%remote)
        if output["retval"] != 0:
          self.lockedremote.append(remote)
    except OSError:
      pass

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
