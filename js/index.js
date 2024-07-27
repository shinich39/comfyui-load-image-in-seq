import { app, ComfyApp } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { ComfyUI, $el } from "../../scripts/ui.js";

const CLASS_NAME = "Load Image In Seq";
const MASK_COLOR = {
  r: 0,
  g: 0,
  b: 0,
  rgb: "rgb(0,0,0)",
}

$el("style", {
	textContent: `
	.load-image-in-seq-mask-editor-container {
    position: relative;
    display: flex; 
    justify-content: center; 
    align-items: center; 
    color: var(--descrip-text); 
    font-family: Verdana, Arial, Helvetica, sans-serif; 
    font-size: 0.8rem;
    letter-spacing: 0;
  }
	.load-image-in-seq-mask-editor-canvas {
    position: absolute;
    max-width: 100%;
    max-height: 100%;
  }
  `,
	parent: document.body,
});

async function getDir(node) {
  if (!node.widgets) {
    throw new Error("Widgets not found.");
  }
  const pathWidget = node.widgets.find(function(item) {
    return item.name === "dir_path";
  });
  if (!pathWidget) {
    throw new Error("Path widget not found.");
  }

  const dirPath = pathWidget.value;
  const response = await api.fetchApi("/shinich39/liis/get_images", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ dirPath }),
  });

  if (response.status !== 200) {
    throw new Error("Error occurred.");
  }

  node.images = await response.json();

  await render(node);
}

async function render(node) {
  const indexWidget = node.widgets.find(function(item) {
    return item.name === "index";
  });

  if (!indexWidget) {
    console.error(new Error("Index widget not found."));
    return;
  }
  
  const images = node.images;
  const index = (images.length + indexWidget.value) % images.length;
  const image = images[index];

  if (!image) {
    console.error(new Error("Image not found."));
    return;
  }

  const filenameWidget = node.widgets.find(function(item) { return item.name === "filename"; });
  const ckptWidget = node.widgets.find(function(item) { return item.name === "ckpt_name"; });
  const positiveWidget = node.widgets.find(function(item) { return item.name === "positive"; });
  const negativeWidget = node.widgets.find(function(item) { return item.name === "negative"; });
  const seedWidget = node.widgets.find(function(item) { return item.name === "seed"; });
  const stepsWidget = node.widgets.find(function(item) { return item.name === "steps"; });
  const cfgWidget = node.widgets.find(function(item) { return item.name === "cfg"; });
  const samplerWidget = node.widgets.find(function(item) { return item.name === "sampler_name"; });
  const schedulerWidget = node.widgets.find(function(item) { return item.name === "scheduler"; });
  const denoiseWidget = node.widgets.find(function(item) { return item.name === "denoise"; });
  const maskWidget = node.widgets.find(function(item) { return item.name === "maskeditor"; });


  if (filenameWidget) {
    filenameWidget.value = image.original_name || "";
  }
  if (indexWidget) {
    indexWidget.value = index;
  }
  if (ckptWidget) {
    ckptWidget.value = image.model || "";
  }
  if (positiveWidget) {
    positiveWidget.value = image.positive || "";
  }
  if (negativeWidget) {
    negativeWidget.value = image.negative || "";
  }
  if (seedWidget) {
    seedWidget.value = image.seed || 0;
  }
  if (stepsWidget) {
    stepsWidget.value = image.steps || 20;
  }
  if (cfgWidget) {
    cfgWidget.value = image.cfg || 8.0;
  }
  if (samplerWidget) {
    samplerWidget.value = image.sampler_name || "euler";
  }
  if (schedulerWidget) {
    schedulerWidget.value = image.scheduler || "normal";
  }
  if (denoiseWidget) {
    denoiseWidget.value = image.denoise || 1.00;
  }
  if (maskWidget) {
    try {
      maskWidget.element.style.width = node.size[0] - 32;
      maskWidget.element.style.height = node.size[0] - 32;
      maskWidget.originalImgLoaded = false;
      maskWidget.maskImgLoaded = false;
      maskWidget.originalPath = image.original_path;
      maskWidget.maskPath = image.mask_path;
      maskWidget.originalCtx.clearRect(0,0,maskWidget.originalCanvas.width,maskWidget.originalCanvas.height);
      maskWidget.maskCtx.clearRect(0,0,maskWidget.maskCanvas.width,maskWidget.maskCanvas.height);
      maskWidget.originalImg.src = pathToSrc(image.original_path);
      maskWidget.maskImg.src = pathToSrc(image.mask_path);
    } catch(err) {
      console.error(err);
    }
  }
  app.graph.setDirtyCanvas(true);
}

async function increaseIndex(node) {
  const modeWidget = node.widgets.find(function(item) {
    return item.name === "mode";
  });
  if (!modeWidget || modeWidget.value === "fixed") {
    return;
  }
  const indexWidget = node.widgets.find(function(item) {
    return item.name === "index";
  });
  if (!indexWidget) {
    return;
  }

  // increment
  indexWidget.value = indexWidget.value + 1;

  await render(node);
}

function pathToSrc(filePath) {
  return `/shinich39/liis/get_image?path=${filePath}&d=${Date.now()}`;
  // return `${location.host}/shinich39/liis/get_image?path=${filePath}`;
}

document.addEventListener('pointerup', (event) => pointerUpEvent(event));

app.registerExtension({
	name: "shinich39.LoadImageInSeq",
  setup() {
    // for (const node of app.graph._nodes) {
    //   if (node.comfyClass === CLASS_NAME) {
    //     // initialize after open comfyui
    //     getDir(node);
    //   }
    // }
  },
	nodeCreated(node, app) {
    if (node.comfyClass !== CLASS_NAME) {
      return;
    }

    const pathWidget = node.widgets.find(function(item) {
      return item.name === "dir_path";
    });
    pathWidget.callback = function(value) {
      getDir(node);
    }

    const indexWidget = node.widgets.find(function(item) {
      return item.name === "index";
    });
    indexWidget.callback = function(value) {
      render(node);
    }

    // set "control_after_generate" to fixed
    const seedWidget = node.widgets.find(function(item) {
      return item.name === "seed";
    });
    if (seedWidget && seedWidget.linkedWidgets && seedWidget.linkedWidgets[0]) {
      seedWidget.linkedWidgets[0].value = "fixed";
    }

    const posWidget = node.widgets.find(function(item) {
      return item.name === "positive";
    });
    const negWidget = node.widgets.find(function(item) {
      return item.name === "negative";
    });

    posWidget.options.getMinHeight = function(e) {
      return 128;
    }
    posWidget.options.getMaxHeight = function(e) {
      return 256;
    }
    negWidget.options.getMinHeight = function(e) {
      return 128;
    }
    negWidget.options.getMaxHeight = function(e) {
      return 256;
    }

    // set mask editor widget
    let maskWidget;
    ;(function() {
      const container = document.createElement("div");
      container.className = "load-image-in-seq-mask-editor-container";
      const originalCanvas = document.createElement("canvas");
      const originalCtx = originalCanvas.getContext("2d", {willReadFrequently: true});
      originalCanvas.className = "load-image-in-seq-mask-editor-canvas";
      const maskCanvas = document.createElement("canvas");
      const maskCtx = maskCanvas.getContext("2d", {willReadFrequently: true});
      maskCanvas.className = "load-image-in-seq-mask-editor-canvas";
      maskCanvas.style.mixBlendMode = "initial";
      maskCanvas.style.opacity = 0.7;

      container.appendChild(originalCanvas);
      container.appendChild(maskCanvas);
      
      maskWidget = node.addDOMWidget("maskeditor", "", container, {
        serialize: false,
        getMinHeight: function() {
          return node.size[0];
        },
      });

      maskWidget.serializeValue = () => undefined;

      maskWidget.originalCanvas = originalCanvas;
      maskWidget.originalCtx = originalCtx;
      maskWidget.maskCanvas = maskCanvas;
      maskWidget.maskCtx = maskCtx;
      
      maskWidget.zoomRatio = 1.0;
      maskWidget.panX = 0;
      maskWidget.panY = 0;
      maskWidget.brushSize = 10;
      maskWidget.drawingMode = false;
      maskWidget.lastx = -1;
      maskWidget.lasty = -1;
      maskWidget.lasttime = 0;
      maskWidget.initializeCanvasPanZoom = initializeCanvasPanZoom;
      maskWidget.invalidatePanZoom = invalidatePanZoom;
      maskWidget.showBrush = showBrush;
      maskWidget.hideBrush = hideBrush;
      maskWidget.handleWheelEvent = handleWheelEvent;
      maskWidget.pointerMoveEvent = pointerMoveEvent;
      maskWidget.pointerDownEvent = pointerDownEvent;
      maskWidget.drawMoveEvent = drawMoveEvent;
      maskWidget.pointerUpEvent = pointerUpEvent;
      maskWidget.saveEvent = saveEvent;
      maskWidget.clearEvent = clearEvent;
      
			maskCanvas.addEventListener('wheel', (event) => maskWidget.handleWheelEvent(maskWidget, event));
			maskCanvas.addEventListener('pointerleave', (event) => maskWidget.hideBrush(maskWidget, event));
			maskCanvas.addEventListener('pointerdown', (event) => maskWidget.pointerDownEvent(maskWidget, event));
			maskCanvas.addEventListener('pointermove', (event) => maskWidget.drawMoveEvent(maskWidget, event));
      
      const originalImg = new Image();
      maskWidget.originalImg = originalImg;
      maskWidget.originalImgLoaded = false;
      
      const maskImg = new Image();
      maskWidget.maskImg = maskImg;
      maskWidget.maskImgLoaded = false;

      originalImg.onload = function() {
        maskWidget.originalImgLoaded = true;
        maskWidget.originalCanvas.width = originalImg.width;
        maskWidget.originalCanvas.height = originalImg.height;
        maskWidget.originalCtx.drawImage(originalImg, 0, 0, originalImg.width, originalImg.height);
        imagesLoaded();
      }

      maskImg.onload = function() {
        maskWidget.maskImgLoaded = true;
        maskWidget.maskCanvas.width = maskImg.width;
        maskWidget.maskCanvas.height = maskImg.height;
        maskWidget.maskCtx.drawImage(maskImg, 0, 0, maskImg.width, maskImg.height);
        imagesLoaded();
      }

      function imagesLoaded() {
        if (maskWidget.originalImgLoaded && maskWidget.maskImgLoaded) {
          // paste mask data into alpha channel
          const maskData = maskCtx.getImageData(0, 0, maskCanvas.width, maskCanvas.height);
  
          // invert mask
          for (let i = 0; i < maskData.data.length; i += 4) {
            if(maskData.data[i+3] == 255) {
              maskData.data[i+3] = 0;
            } else {
              maskData.data[i+3] = 255;
            }
  
            maskData.data[i] = MASK_COLOR.r;
            maskData.data[i+1] = MASK_COLOR.g;
            maskData.data[i+2] = MASK_COLOR.b;
          }
  
          maskCtx.globalCompositeOperation = 'source-over';
          maskCtx.putImageData(maskData, 0, 0);
          maskWidget.initializeCanvasPanZoom();
        }
      }

      // focus to node
      container.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        document.getElementById("graph-canvas").focus();
      });

      // focus to node
      originalCanvas.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        container.click();
      });

      // focus to node
      maskCanvas.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        container.click();
      });

      // add mask control widget
      const clearWidget = node.addWidget("button", "Clear", () => {}, {
        serialize: false,
      });

      clearWidget.serializeValue = () => undefined;
      clearWidget.callback = function() {
        maskWidget.clearEvent(maskWidget);
      }
    })();

    // next, prev event
    node.onKeyDown = keyDownEvent;

    // resize event
    const onResize = node.onResize;
		node.onResize = function (size) {
      maskWidget.initializeCanvasPanZoom();
      onResize?.apply(this, arguments);
		};

    // initialize after create a new node
    // initialize after launched comfyui
    setTimeout(function() {
      getDir(node);
    }, 128);

    async function keyDownEvent(e) {
      const { key } = e;

      if (key === "ArrowLeft" || key === "ArrowUp") {
        e.preventDefault();
        e.stopPropagation();
        indexWidget.value = indexWidget.value - 1;
        await render(node);
      } else if (key === "ArrowRight" || key === "ArrowDown") {
        e.preventDefault();
        e.stopPropagation();
        indexWidget.value = indexWidget.value + 1;
        await render(node);
      }
    }
  }
});

// Helper function to convert a data URL to a Blob object
function dataURLToBlob(dataURL) {
	const parts = dataURL.split(';base64,');
	const contentType = parts[0].split(':')[1];
	const byteString = atob(parts[1]);
	const arrayBuffer = new ArrayBuffer(byteString.length);
	const uint8Array = new Uint8Array(arrayBuffer);
	for (let i = 0; i < byteString.length; i++) {
		uint8Array[i] = byteString.charCodeAt(i);
	}
	return new Blob([arrayBuffer], { type: contentType });
}

function initializeCanvasPanZoom() {
  // set initialize
  let drawWidth = this.originalImg.width;
  let drawHeight = this.originalImg.height;

  let width = this.element.clientWidth;
  let height = this.element.clientHeight;

  if (this.originalImg.width > width) {
    drawWidth = width;
    drawHeight = (drawWidth / this.originalImg.width) * this.originalImg.height;
  }

  if (drawHeight > height) {
    drawHeight = height;
    drawWidth = (drawHeight / this.originalImg.height) * this.originalImg.width;
  }

  this.zoomRatio = drawWidth / this.originalImg.width;

  const canvasX = (width - drawWidth) / 2;
  const canvasY = (height - drawHeight) / 2;
  this.panX = canvasX;
  this.panY = canvasY;

  this.invalidatePanZoom();
}

function invalidatePanZoom() {
  let rawWidth = this.originalImg.width * this.zoomRatio;
  let rawHeight = this.originalImg.height * this.zoomRatio;

  if(this.panX + rawWidth < 10) {
    this.panX = 10 - rawWidth;
  }

  if(this.panY + rawHeight < 10) {
    this.panY = 10 - rawHeight;
  }

  let width = `${rawWidth}px`;
  let height = `${rawHeight}px`;

  let left = `${this.panX}px`;
  let top = `${this.panY}px`;

  this.maskCanvas.style.width = width;
  this.maskCanvas.style.height = height;
  this.maskCanvas.style.left = left;
  this.maskCanvas.style.top = top;

  this.originalCanvas.style.width = width;
  this.originalCanvas.style.height = height;
  this.originalCanvas.style.left = left;
  this.originalCanvas.style.top = top;
}

function showBrush() {
  if (!this.brush) {
    this.brush = document.createElement("div");
    // this.brush.className = "load-image-in-seq-mask-editor-brush";
    document.body.appendChild(this.brush);
  }
  // canvas scale
  const scale = app.canvas.ds.scale;

  this.brush.style.backgroundColor = "rgba(0,0,0,0.2)";
  this.brush.style.boxShadow = "0 0 0 1px white";
  this.brush.style.borderRadius = "50%";
  this.brush.style.MozBorderRadius = "50%";
  this.brush.style.WebkitBorderRadius = "50%";
  this.brush.style.position = "absolute";
  this.brush.style.zIndex = 8889;
  this.brush.style.pointerEvents = "none";
  this.brush.style.width = this.brushSize * 2 * this.zoomRatio * scale + "px";
  this.brush.style.height = this.brushSize * 2 * this.zoomRatio * scale + "px";
  this.brush.style.left = (this.cursorX - this.brushSize * this.zoomRatio * scale) + "px";
  this.brush.style.top = (this.cursorY - this.brushSize * this.zoomRatio * scale) + "px";
}

function hideBrush() {
  if (this.brush) {
    this.brush.parentNode.removeChild(this.brush);
    this.brush = null;
  }
}

function handleWheelEvent(self, event) {
  event.preventDefault();

  // canvas scale
  const scale = app.canvas.ds.scale;

  // adjust brush size
  if(event.deltaY < 0)
    self.brushSize = Math.min(self.brushSize+(10 / scale), 100 / scale);
  else
    self.brushSize = Math.max(self.brushSize-(10 / scale), 1);

  self.showBrush();
}

function pointerMoveEvent(self, event) {
  self.cursorX = event.pageX;
  self.cursorY = event.pageY;
  self.showBrush();
}

function drawMoveEvent(self, event) {
  if(event.ctrlKey || event.shiftKey) {
    return;
  }

  event.preventDefault();

  this.cursorX = event.pageX;
  this.cursorY = event.pageY;

  self.showBrush();

  let left_button_down = window.TouchEvent && event instanceof TouchEvent || event.buttons == 1;
  let right_button_down = [2, 5, 32].includes(event.buttons);

  if (!event.altKey && left_button_down) {
    var diff = performance.now() - self.lasttime;

    const maskRect = self.maskCanvas.getBoundingClientRect();

    var x = event.offsetX;
    var y = event.offsetY

    if(event.offsetX == null) {
      x = event.targetTouches[0].clientX - maskRect.left;
    }

    if(event.offsetY == null) {
      y = event.targetTouches[0].clientY - maskRect.top;
    }

    x /= self.zoomRatio;
    y /= self.zoomRatio;

    var brushSize = this.brushSize;
    if(event instanceof PointerEvent && event.pointerType == 'pen') {
      brushSize *= event.pressure;
      this.last_pressure = event.pressure;
    }
    else if(window.TouchEvent && event instanceof TouchEvent && diff < 20){
      // The firing interval of PointerEvents in Pen is unreliable, so it is supplemented by TouchEvents.
      brushSize *= this.last_pressure;
    }
    else {
      brushSize = this.brushSize;
    }

    if(diff > 20 && !this.drawingMode)
      requestAnimationFrame(() => {
        self.maskCtx.beginPath();
        self.maskCtx.fillStyle = MASK_COLOR.rgb;
        self.maskCtx.globalCompositeOperation = "source-over";
        self.maskCtx.arc(x, y, brushSize, 0, Math.PI * 2, false);
        self.maskCtx.fill();
        self.lastx = x;
        self.lasty = y;
      });
    else
      requestAnimationFrame(() => {
        self.maskCtx.beginPath();
        self.maskCtx.fillStyle = MASK_COLOR.rgb;
        self.maskCtx.globalCompositeOperation = "source-over";

        var dx = x - self.lastx;
        var dy = y - self.lasty;

        var distance = Math.sqrt(dx * dx + dy * dy);
        var directionX = dx / distance;
        var directionY = dy / distance;

        for (var i = 0; i < distance; i+=5) {
          var px = self.lastx + (directionX * i);
          var py = self.lasty + (directionY * i);
          self.maskCtx.arc(px, py, brushSize, 0, Math.PI * 2, false);
          self.maskCtx.fill();
        }
        self.lastx = x;
        self.lasty = y;
      });

    self.lasttime = performance.now();
  }
  else if((event.altKey && left_button_down) || right_button_down) {
    const maskRect = self.maskCanvas.getBoundingClientRect();
    const x = (event.offsetX || event.targetTouches[0].clientX - maskRect.left) / self.zoomRatio;
    const y = (event.offsetY || event.targetTouches[0].clientY - maskRect.top) / self.zoomRatio;

    var brushSize = this.brushSize;
    if(event instanceof PointerEvent && event.pointerType == 'pen') {
      brushSize *= event.pressure;
      this.last_pressure = event.pressure;
    }
    else if(window.TouchEvent && event instanceof TouchEvent && diff < 20){
      brushSize *= this.last_pressure;
    }
    else {
      brushSize = this.brushSize;
    }

    if(diff > 20 && !drawingMode) // cannot tracking drawingMode for touch event
      requestAnimationFrame(() => {
        self.maskCtx.beginPath();
        self.maskCtx.globalCompositeOperation = "destination-out";
        self.maskCtx.arc(x, y, brushSize, 0, Math.PI * 2, false);
        self.maskCtx.fill();
        self.lastx = x;
        self.lasty = y;
      });
    else
      requestAnimationFrame(() => {
        self.maskCtx.beginPath();
        self.maskCtx.globalCompositeOperation = "destination-out";
        
        var dx = x - self.lastx;
        var dy = y - self.lasty;

        var distance = Math.sqrt(dx * dx + dy * dy);
        var directionX = dx / distance;
        var directionY = dy / distance;

        for (var i = 0; i < distance; i+=5) {
          var px = self.lastx + (directionX * i);
          var py = self.lasty + (directionY * i);
          self.maskCtx.arc(px, py, brushSize, 0, Math.PI * 2, false);
          self.maskCtx.fill();
        }
        self.lastx = x;
        self.lasty = y;
      });

      self.lasttime = performance.now();
  }
}

function pointerDownEvent(self, event) {
  if (!self.originalImgLoaded || !self.maskImgLoaded) {
    return;
  }

  if(event.ctrlKey) {
    if (event.buttons == 1) {
      self.mousedown_x = event.clientX;
      self.mousedown_y = event.clientY;

      self.mousedown_panX = self.panX;
      self.mousedown_panY = self.panY;
    }
    return;
  }

  var brushSize = self.brushSize;
  if(event instanceof PointerEvent && event.pointerType == 'pen') {
    brushSize *= event.pressure;
    self.last_pressure = event.pressure;
  }

  if ([0, 2, 5].includes(event.button)) {
    self.drawingMode = true;

    event.preventDefault();

    if(event.shiftKey) {
      self.zoom_lasty = event.clientY;
      self.last_zoomRatio = self.zoomRatio;
      return;
    }

    const maskRect = self.maskCanvas.getBoundingClientRect();
    const x = (event.offsetX || event.targetTouches[0].clientX - maskRect.left) / self.zoomRatio;
    const y = (event.offsetY || event.targetTouches[0].clientY - maskRect.top) / self.zoomRatio;

    self.maskCtx.beginPath();
    if (!event.altKey && event.button == 0) {
      self.maskCtx.fillStyle = MASK_COLOR.rgb;
      self.maskCtx.globalCompositeOperation = "source-over";
    } else {
      self.maskCtx.globalCompositeOperation = "destination-out";
    }
    self.maskCtx.arc(x, y, brushSize, 0, Math.PI * 2, false);
    self.maskCtx.fill();
    self.lastx = x;
    self.lasty = y;
    self.lasttime = performance.now();
  }
}

function pointerUpEvent(event) {
  event.preventDefault();

  // reset all canvas
  for (const node of app.graph._nodes) {
    if (node.comfyClass === CLASS_NAME) {
      const w = node.widgets?.find(function(item) { return item.name === "maskeditor"; });
      if (w) {

        // call save event
        if (w.drawingMode) {
          w.saveEvent(w);
        }

        w.mousedown_x = null;
        w.mousedown_y = null;
        w.drawingMode = false;
      }
    }
  }
}

async function saveEvent(self) {
  const backupCanvas = document.createElement('canvas');
  const backupCtx = backupCanvas.getContext('2d', {willReadFrequently:true});
  backupCanvas.width = self.originalImg.width;
  backupCanvas.height = self.originalImg.height;

  backupCtx.clearRect(0,0, backupCanvas.width, backupCanvas.height);
  backupCtx.drawImage(self.maskCanvas,
    0, 0, self.maskCanvas.width, self.maskCanvas.height,
    0, 0, backupCanvas.width, backupCanvas.height);

  // paste mask data into alpha channel
  const backupData = backupCtx.getImageData(0, 0, backupCanvas.width, backupCanvas.height);

  // refine mask image
  for (let i = 0; i < backupData.data.length; i += 4) {
    if(backupData.data[i+3] == 255)
      backupData.data[i+3] = 0;
    else
      backupData.data[i+3] = 255;

    backupData.data[i] = 0;
    backupData.data[i+1] = 0;
    backupData.data[i+2] = 0;
  }

  backupCtx.globalCompositeOperation = 'source-over';
  backupCtx.putImageData(backupData, 0, 0);

  const formData = new FormData();
  const dataURL = backupCanvas.toDataURL();
  const blob = dataURLToBlob(dataURL);
  formData.append('image', blob);
  formData.append('original_path', self.originalPath);
  formData.append('mask_path', self.maskPath);

	await api.fetchApi('/shinich39/liis/save_mask', {
		method: 'POST',
		body: formData
	});

  // console.log("Mask saved.");
}

async function clearEvent(self) {
  await api.fetchApi('/shinich39/liis/remove_mask', {
		method: 'POST',
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      original_path: self.originalPath,
      mask_path: self.maskPath,
    }),
	});

  // reload mask
  self.maskImgLoaded = false;
  self.maskCtx.clearRect(0,0,self.maskCanvas.width,self.maskCanvas.height);
  self.maskImg.src = pathToSrc(self.maskPath);

  // console.log("Mask removed.");
}

api.addEventListener("promptQueued", async function() {
  for (const node of app.graph._nodes) {
    if (node.comfyClass === CLASS_NAME) {
      await increaseIndex(node);
    }
  }
});
