import os
from django.core.files.storage import FileSystemStorage


### This is useed to overwrite the existing file when uploading ###
class OverrideExisting(FileSystemStorage):
  OS_OPEN_FLAGS = os.O_WRONLY | os.O_TRUNC | os.O_CREAT | getattr(os, 'O_BINARY', 0)

  def get_available_name(self, name, max_length = None):
    return name