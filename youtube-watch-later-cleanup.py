from uiautomator import device as d
from signal import signal, SIGINT
from sys import exit, stdout
from collections import defaultdict
import json
import traceback
from datetime import datetime

debug = False

def debug(data):
    if (debug):
        print(data)

def load_data():
    with open("data.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

debug("Loading data")
data = load_data()
debug("Loaded data")

def stop_handle(signal_received, frame):
    debug("stop_handle: saving data")
    data['saved_videos'].sort()
    save_data(data)
    debug("stop_handle: saved data")

    if (signal_received == SIGINT):
        exit(0)

signal(SIGINT, stop_handle)

def swipe(v):
    bounds = v.bounds
    top = bounds['top']
    left = bounds['left']
    right = bounds['right']
    bottom = bounds['bottom']

    midVertical = ((bottom - top) / 2) + bottom

    debug("swipe: dragging: %f %f%f %f" % (left, midVertical, 0, midVertical))
    d.drag(left, midVertical, 0, midVertical, steps=10)

def delete_view(view):
  debug("delete_view: %s" % view.text)
  swipe(view)

  debug("delete_view: Removing %s" % view.text)
  try:
    d(text="REMOVE").click()
  except:
    d(text="Remove").click()

  debug("delete_view: Waiting for remove from watch later")
  d(text="Removed From Watch Later").wait.exists(timeout=5000)
  debug("delete_view: Waiting for remove from watch later to be gone")
  d(text="Removed From Watch Later").wait.gone(timeout=5000)

def deletePrivateVideos():
  privateVideos = d(text="[Private video]")
  for privateVideo in privateVideos:
    debug("Private video")
    delete_view(privateVideo)

def removeVideosByCertainAuthors():
  authors = d(resourceId="com.google.android.youtube:id/author")
  for authorView in authors:
    author = authorView.text
    if author in data['remove_videos_by_authors']:
      debug("AuthorView")
      stdout.write('D')

      delete_view(authorView)

      if author not in data['deleted_authors']:
        data['deleted_authors'][author] = 0

      data['deleted_authors'][author] += 1

def recordVideosListed():
  authors = d(resourceId="com.google.android.youtube:id/author")
  for authorView in authors:
    titleView = authorView.sibling(resourceId="com.google.android.youtube:id/title")

    author = authorView.text
    title = titleView.text
    videoName = author + ": " + title

    if videoName not in data['saved_videos']:
        data['saved_videos'].append(videoName)

def main():
  while True:
    deletePrivateVideos()
    removeVideosByCertainAuthors()
    recordVideosListed()
    stdout.flush()
    debug("Scrolling")
    d().scroll()

while True:
  try:
    debug("Dragging in loop")
    d.drag(550, 750, 550, 550, steps=10)
    main()
  except Exception as e:
    traceback.print_exc()
  finally:
    stop_handle("", "")
