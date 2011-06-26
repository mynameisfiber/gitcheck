#!/bin/env python
import os
from hashlib import md5
from time import time
import subprocess

class Repository:
  def __init__(self, location, config=None):
    self.config   = config
    self.location = os.path.expanduser(location)
    self.name     = os.path.basename(self.location)

    self.lockedremote = []
    self.refresh_repo()   
    self.remotes      = self.find_remotes()
    self.local_heads  = self.find_local_heads()

    self.updates = {}
    self.fresh_updates = []
    self.new_updates = []

  def get_updates(self):
    for key, update in self.updates.iteritems():
      yield (key, update)

  def get_new_updates(self):
    for key in self.new_updates:
      yield (key, self.updates[key])
      self.updates[key] = False

  def get_fresh_updates(self):
    for key in self.fresh_updates:
      yield (key, self.updates[key])

  def check_updates(self):
    prev_updates_keys = self.updates.keys()
    self.fresh_updates = []
    self.new_updates = []
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
              key = md5(update["repo"]+update["ref"]+update["desc"]).hexdigest()

              update["fresh"] = True
              self.fresh_updates.append(key)
              if key not in prev_updates_keys:
                update["new"] = True
                self.new_updates.append(key)
              else:
                update["new"] = False

              self.updates.update( {key : update} )
            except:
              pass
        except KeyError:
          pass

  def _run_git_cmd(self, cmd):
    try:
      env = {"GIT_SSH":os.path.join(os.getcwd(),"ssh_wrapper")}
      if self.config is not None and "GIT_PATH" in self.config and self.config["GIT_PATH"] is not None:
        git = os.path.join(self.config["GIT_PATH"],'git')
      else:
        git = 'git'
      pd = subprocess.Popen(("%s %s"%(git,cmd)).split(), 
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

  def refresh_repo(self):
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

  def __getitem__(self, item):
    return self.updates[item]
