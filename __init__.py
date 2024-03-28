"""
@author: shinich39
@title: Load Image #39
@nickname: Load Image #39
@version: 1.0.0
@description: Load png image sequentially with metadata
"""

import server
import numpy as np
import torch
import os
import comfy
import folder_paths as comfy_paths
from PIL import Image, ImageOps
from .libs.parser import parse_png
from .libs.utils import load_image_from_directory

DEBUG = False
VERSION = "1.0.0"
WEB_DIRECTORY = "./js"
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# main
class LoadImage():
  def __init__(self):
    pass

  @classmethod
  def INPUT_TYPES(cls):
    return {
      "hidden": {
        "unique_id": "UNIQUE_ID",
      },
      "required": {
        "dir_path": ("STRING", {"default": "./ComfyUI/input"}),
        "mode": (["fixed", "increment"],),
        "index":  ("INT", {"default": 0, "min": 0, "step": 1}),
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
  RETURN_TYPES = ("IMAGE",  "MASK", "STRING",  "INT",    "STRING",     "STRING",   "STRING",   "INT", "INT",    "FLOAT",  "STRING",       "STRING",     "FLOAT")
  RETURN_NAMES = ("image",  "mask", "filename","index",  "ckpt_name",  "positive", "negative", "seed", "steps",  "cfg",    "sampler_name", "scheduler",  "denoise")

  FUNCTION = "exec"

  def exec(self, unique_id, dir_path, mode, index, default_ckpt_name, default_positive, default_negative, default_seed, default_steps, default_cfg, default_sampler_name, default_scheduler, default_denoise):
    if DEBUG:
      print(f"#39 unique_id: {unique_id}")
      print(f"#39 dir_path: {dir_path}")
      print(f"#39 mode: {mode}")
      print(f"#39 index: {index}")

    if not os.path.isdir(dir_path):
      raise FileNotFoundError(f"#39 {dir_path} not found.")
  
    # load
    image, file_path, file_name, file_index = load_image_from_directory(dir_path, index)

    if image is None:
      raise FileNotFoundError(f"#39 Image not found.")
    
    if DEBUG:
      print(f"#39 file_path: {file_path}")
      print(f"#39 file_name: {file_name}")
      print(f"#39 file_index: {file_index}")
      
    # parse
    p_prompt, n_prompt, setting, parameter = parse_png(file_path)

    if DEBUG:
      print(f"#39 positive: {p_prompt}")
      print(f"#39 negative: {n_prompt}")
      print(f"#39 setting: {setting}")
      print(f"#39 parameter: {parameter}")

    model = default_ckpt_name if parameter["model"] == "None" else parameter["model"]
    positive = default_positive if not p_prompt else p_prompt
    negative = default_negative if not n_prompt else n_prompt
    seed = default_seed if parameter["seed"] == "None" else parameter["seed"]
    steps = default_steps if parameter["steps"] == "None" else parameter["steps"]
    cfg = default_cfg if parameter["cfg"] == "None" else parameter["cfg"]
    sampler_name = default_sampler_name if parameter["sampler"] == "None" else parameter["sampler"]
    scheduler = default_scheduler if parameter["scheduler"] == "None" else parameter["scheduler"]
    denoise = default_denoise if parameter["denoise"] == "None" else parameter["denoise"]

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

# to js
def update_workflow_index(json_data):
  nodes = json_data['extra_data']['extra_pnginfo']['workflow']['nodes']
  widget_idx_map = json_data['extra_data']['extra_pnginfo']['workflow']['widget_idx_map']
  prompt = json_data['prompt']

  updates = {}
  for node in nodes:
    node_id = str(node['id']) # unique_id
    node_type = str(node['type']) # node name
    if DEBUG:
      print(f"#39 node_id {node_id}")
      print(f"#39 node_type {node_type}")
       
    if node_type == "Load Image #39" and node_id in prompt:
      node_inputs = prompt[node_id]['inputs']
      
      mode = node_inputs["mode"]
      index = node_inputs["index"]

      if mode == "increment":
        index += 1

      updates[node_id] = index

  if DEBUG:
    print(f"#39 updates {updates}")

  server.PromptServer.instance.send_sync("load-image-39-update-index", updates)

def onprompt(json_data):
  print(f"#39 onprompt: {json_data}")

  update_workflow_index(json_data)

  # for k, v in json_data['prompt'].items():
  #   if v['class_type'] == "Load Image #39":

  #   for k2, v2 in v['inputs'].items():
  #     if isinstance(v2, str) and '$GlobalSeed.value$' in v2:
  #       v['inputs'][k2] = v2.replace('$GlobalSeed.value$', str(value))

  return json_data

server.PromptServer.instance.add_on_prompt_handler(onprompt)

NODE_CLASS_MAPPINGS["Load Image #39"] = LoadImage
NODE_DISPLAY_NAME_MAPPINGS["Load Image #39"] = "Load Image #39"