#!/usr/bin/python
import appindicator
import gtk
import threading
import signal
import os
gtk.threads_init()
from messaging.message import message

class Indicator(message):
  def __init__(self, config):
		message.__init__(config)
    self.icon = message.config["icon"]
    signal.signal(signal.SIGTERM, self.exit)
    self.updates = {}
    self.icon = icon
    self.setup_indicator()

  def setup_indicator(self):
    self.indicator = appindicator.Indicator("checkgitgui", "checkgitgui", appindicator.CATEGORY_APPLICATION_STATUS)
    self.indicator.set_status(appindicator.STATUS_ACTIVE)

    self.indicator.set_icon(self.icon)
    self.indicator.set_menu(self.setup_menu())

  def fresh_updates_message(self, updates):
    self.updates.update(updates)
    self.indicator.set_menu(self.setup_menu())

  def foo(self, item):
    print "Foo has been called"
    print dir(item)

  def exit(self, *args, **kwargs):
    exit(1)

  def setup_menu(self):
    menu = gtk.Menu()

    for key, update in self.updates.iteritems():
      updateitem = gtk.MenuItem("%s: [%s]"%(update["repo"], update["ref"]))
      updateitem.update_key = key
      updateitem.show()
      menu.append(updateitem)

    item = gtk.SeparatorMenuItem()
    item.show()
    menu.append(item)

    item = gtk.MenuItem("_Preferences")
    item.connect("activate", self.foo)
    item.show()
    menu.append(item)

    item = gtk.MenuItem("Quit")
    item.connect("activate", self.exit)
    item.show()
    menu.append(item)

    return menu

  def run(self):
    gtk.main()


if __name__ == "__main__":
  a = Indicator()
  a.start()
