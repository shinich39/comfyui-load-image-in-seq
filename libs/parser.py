from PIL import Image
from PIL.PngImagePlugin import PngInfo, PngImageFile
from PIL.JpegImagePlugin import JpegImageFile

from .comfyui import ComfyUI

def parse_png(file_path):
  with open(file_path, "rb") as file, Image.open(file) as image:
    width = image.width
    height = image.height
    info = image.info
    format = image.format

    if not isinstance(image, PngImageFile):
      raise Exception("Only supported for PNG format")
    
    parser = ComfyUI(info=info, width=width, height=height)
    positive = parser.positive
    negative = parser.negative
    setting = parser.setting
    parameter = parser.parameter

    return positive, negative, setting, parameter