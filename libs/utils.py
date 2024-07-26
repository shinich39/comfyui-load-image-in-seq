import os
from pathlib import Path

VALID_EXTENSIONS = [".png"]

def get_all_image_files(dir_path):
  image_list = []
  for file in os.listdir(dir_path):
    ext = os.path.splitext(file)[1]
    if ext.lower() not in VALID_EXTENSIONS:
      continue
    # mask
    if file.startswith("."):
      continue
    image_list.append(
      Path(os.path.join(dir_path, file)).as_posix()
    )
  return image_list