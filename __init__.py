"""
@author: shinich39
@title: Load Image 39
@nickname: Load Image 39
@version: 1.0.0
@description: Load png image sequentially with metadata
"""

import numpy as np
import torch
import os
import comfy
import folder_paths as comfy_paths
from PIL import Image, ImageOps
from .libs.parser import parse_png
from .libs.utils import load_image_from_directory

DEBUG = False

class LoadImage():
  def __init__(self):
    self.loaders = {}

  @classmethod
  def INPUT_TYPES(s):
    return {
      "hidden": {
        "unique_id": "UNIQUE_ID",
      },
      "required": {
        "dir_path": ("STRING", {"default": "./ComfyUI/input"}),
        "mode": (["fixed", "increment", "decrement", "reset"],),
        "start_index":  ("INT", {"default": 0, "min": 0, "step": 1}),
      },
      "optional": {
        "default_ckpt_name": (comfy_paths.get_filename_list("checkpoints"), ),
        "default_positive": ("STRING", {"default": "", "multiline": True}),
        "default_negative": ("STRING", {"default": "", "multiline": True}),
        "default_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
        "default_steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
        "default_cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
        "default_sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
        "default_scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
        "default_denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
      },
    }
  
  @classmethod
  def IS_CHANGED(cls, **kwargs):
    return float("NaN")

  CATEGORY = "image"
  RETURN_TYPES = ("IMAGE", "MASK", "STRING", "INT", "STRING", "STRING", "STRING", "SEED", "INT", "FLOAT", "STRING", "STRING", "FLOAT")
  RETURN_NAMES = ("image", "mask", "filename", "index", "ckpt_name", "positive", "negative", "seed", "steps", "cfg", "sampler_name", "scheduler", "denoise")

  FUNCTION = "exec"

  def exec(self, unique_id, dir_path, mode, start_index, default_ckpt_name, default_positive, default_negative, default_seed, default_steps, default_cfg, default_sampler_name, default_scheduler, default_denoise):
    if DEBUG:
      print(f"dir_path: {dir_path}")

    if not os.path.isdir(dir_path):
      raise FileNotFoundError(f"{dir_path} not found.")
    
    current_index = start_index
    if self.loaders.__contains__(unique_id):
      current_index = self.loaders[unique_id]

    # reset
    if mode == "reset":
      current_index = start_index
      self.loaders[unique_id] = start_index
  
    # load
    image, file_path, file_name, file_index = load_image_from_directory(dir_path, current_index)

    if DEBUG:
      print(f"file_index: {file_index}")

    if image is None:
      raise FileNotFoundError(f"Image not found.")
    
    # set index
    if mode == "increment":
      self.loaders[unique_id] = file_index + 1
    elif mode == "decrement":
      self.loaders[unique_id] = file_index - 1
    elif mode == "reset":
      self.loaders[unique_id] = file_index

    # parse
    p_prompt, n_prompt, setting, parameter = parse_png(file_path)

    if DEBUG:
      print(f"positive: {p_prompt}")
      print(f"negative: {n_prompt}")
      print(f"setting: {setting}")
      print(f"parameter: {parameter}")

    model = default_ckpt_name if "model" not in parameter else parameter["model"]
    positive = default_positive if p_prompt is None else p_prompt
    negative = default_negative if n_prompt is None else n_prompt
    seed = default_seed if "seed" not in parameter else parameter["seed"]
    steps = default_steps if "steps" not in parameter else parameter["steps"]
    cfg = default_cfg if "cfg" not in parameter else parameter["cfg"]
    sampler_name = default_sampler_name if "sampler" not in parameter else parameter["sampler"]
    scheduler = default_scheduler if "scheduler" not in parameter else parameter["scheduler"]
    denoise = default_denoise if "denoise" not in parameter else parameter["denoise"]

    # image
    img = ImageOps.exif_transpose(image)
    image = img.convert("RGB")
    image = np.array(image).astype(np.float32) / 255.0
    image = torch.from_numpy(image)[None,]
    if 'A' in img.getbands():
      mask = np.array(img.getchannel('A')).astype(np.float32) / 255.0
      mask = 1. - torch.from_numpy(mask)
    else:
      mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")

    return (image, mask.unsqueeze(0), file_name, file_index, model, positive, negative, seed, steps, cfg, sampler_name, scheduler, denoise)
  
WEB_DIRECTORY = "./web"

NODE_CLASS_MAPPINGS = {
  "Load Image #39": LoadImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
  "Load Image #39": "Load Image #39",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]