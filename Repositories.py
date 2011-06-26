#!/bin/env python

from Repository import Repository

class Repositories:
  def __init__(self, repositories_raw=list(), config=None):
    self.config = config

    self.updates = {}
    self.repositories_raw = []
    self.repositories = {}
    for repo_raw in repositories_raw:
      self.add_repository(repo_raw)

  def add_repository(self, repo):
    self.repositories_raw.append(repo)
    self.repositories.update(self.init_repo(repo))

  def init_repo(self, repo_raw):
    return { repo_raw : Repository(repo_raw, config=self.config) }

  def refresh_repositories(self):
    self.updates = {}
    for repo in self.repositories.itervalues():
      repo.refresh_repo()
      self.updates.update(repo.updates)

  def update_repositories(self):
    self.updates = {}
    for repo in self.repositories.itervalues():
      repo.check_updates()
      self.updates.update(repo.updates)

  def get_locked_remotes(self):
    for name, repo in self.repositories.iteritems():
      for remote in repo.lockedremote:
        yield (name, remote)

  def get_new_updates(self):
    for repo in self.repositories.itervalues():
      for update in repo.get_new_updates():
        yield update

  def get_fresh_updates(self):
    for repo in self.repositories.itervalues():
      for update in repo.get_fresh_updates():
        yield update

  def get_updates(self):
    for repo in self.repositories.itervalues():
      for update in repo.get_updates():
        yield update

  def __getitem__(self, item):
    return self.repositories[item]

  def get_update(self, key):
    return (self.repositories[self.updates[key]])[key]

if __name__ == "__main__":
  repos = Repositories()
  repos.add_repository("~/projects/zzp2")

  print repos

  print "Fresh Updates:"
  print list(repos.get_fresh_updates())

  print "New Updates:"
  print list(repos.get_new_updates())
    
