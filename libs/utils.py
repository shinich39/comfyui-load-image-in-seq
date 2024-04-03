import os
from pathlib import Path
from PIL import Image, ImageOps

VALID_EXTENSIONS = [".png"]

def get_all_image_files(dir_path):
  image_list = []
  for file in os.listdir(dir_path):
    ext = os.path.splitext(file)[1]
    if ext.lower() not in VALID_EXTENSIONS:
      continue
    image_list.append(
      Path(os.path.join(dir_path, file)).as_posix()
    )
  return image_list

def load_image_from_directory(dir_path, image_index):
  file_list = get_all_image_files(dir_path)
  file_length = len(file_list)

  if file_length == 0:
    return None, None, None, 0, -1
  
  file_index = (file_length + image_index) % file_length
  file_path = file_list[file_index]
  file_name = Path(file_path).resolve().stem

  image = Image.open(file_path)

  return image, file_path, file_name, file_length, file_index
