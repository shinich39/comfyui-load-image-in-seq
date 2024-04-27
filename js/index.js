import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { $el } from "../../scripts/ui.js";

const DEBUG = false;
const CLASS_NAME = "Load Image In Seq";

// $el("style", {
// 	textContent: `
// 	.shinich39-load-image-in-seq-text { background-color: #222; padding: 2px; color: #ddd; }
//   `,
// 	parent: document.body,
// });

async function getMetadata(node) {
  if (!node.widgets) {
    throw new Error("Widgets not found.");
  }
  const pathWidget = node.widgets.find(function(item) {
    return item.name === "dir_path";
  });
  const indexWidget = node.widgets.find(function(item) {
    return item.name === "index";
  });
  if (!pathWidget || !indexWidget) {
    throw new Error("Widget not found.");
  }

  const dirPath = pathWidget.value;
  const index = indexWidget.value;
  const response = await api.fetchApi("/shinich39/get_metadata", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({dirPath, index}),
  });

  if (DEBUG) {
    console.log("POST /shinich39/get_metadata", response);
  }

  return response.status === 200 ? response.json() : {};
}

function setMetadata(node, data) {
  if (!node.widgets) {
    throw new Error("Widgets not found.");
  }
  
  const filenameWidget = node.widgets.find(function(item) { return item.name === "filename"; });
  const indexWidget = node.widgets.find(function(item) { return item.name === "index"; });
  const ckptWidget = node.widgets.find(function(item) { return item.name === "ckpt_name"; });
  const positiveWidget = node.widgets.find(function(item) { return item.name === "positive"; });
  const negativeWidget = node.widgets.find(function(item) { return item.name === "negative"; });
  const seedWidget = node.widgets.find(function(item) { return item.name === "seed"; });
  const stepsWidget = node.widgets.find(function(item) { return item.name === "steps"; });
  const cfgWidget = node.widgets.find(function(item) { return item.name === "cfg"; });
  const samplerWidget = node.widgets.find(function(item) { return item.name === "sampler_name"; });
  const schedulerWidget = node.widgets.find(function(item) { return item.name === "scheduler"; });
  const denoiseWidget = node.widgets.find(function(item) { return item.name === "denoise"; });
  if (filenameWidget) {
    filenameWidget.value = data.filename || "";
  }
  if (indexWidget) {
    indexWidget.value = data.file_index > -1 ? data.file_index : 0;
  }
  if (ckptWidget) {
    ckptWidget.value = data.model || "";
  }
  if (positiveWidget) {
    positiveWidget.value = data.positive || "";
  }
  if (negativeWidget) {
    negativeWidget.value = data.negative || "";
  }
  if (seedWidget) {
    seedWidget.value = data.seed || 0;
  }
  if (stepsWidget) {
    stepsWidget.value = data.steps || 20;
  }
  if (cfgWidget) {
    cfgWidget.value = data.cfg || 8.0;
  }
  if (samplerWidget) {
    samplerWidget.value = data.sampler_name || "euler";
  }
  if (schedulerWidget) {
    schedulerWidget.value = data.scheduler || "normal";
  }
  if (denoiseWidget) {
    denoiseWidget.value = data.denoise || 1.00;
  }
}

async function render(node) {
  const data = await getMetadata(node)

  if (DEBUG) {
    console.log(CLASS_NAME+" render", data);
  }

  setMetadata(node, data);
}

async function increaseIndex(node) {
  const modeWidget = node.widgets.find(function(item) {
    return item.name == "mode";
  });
  if (!modeWidget || modeWidget.value === "fixed") {
    return;
  }
  const indexWidget = node.widgets.find(function(item) {
    return item.name == "index";
  });
  if (!indexWidget) {
    return;
  }

  // mode: increment
  indexWidget.value = indexWidget.value + 1;

  await render(node);
}

app.registerExtension({
	name: "shinich39.LoadImageInSeq",
	nodeCreated(node, app) {
    if (node.comfyClass !== CLASS_NAME) {
      return;
    }
    if (DEBUG) {
      console.log(CLASS_NAME+" node", node);
    }

    const pathWidget = node.widgets.find(function(item) {
      return item.name === "dir_path";
    });

    pathWidget.callback = function(value) {
      render(node);
    }

    const indexWidget = node.widgets.find(function(item) {
      return item.name === "index";
    });

    indexWidget.callback = function(value) {
      render(node);
    }

    const seedWidget = node.widgets.find(function(item) {
      return item.name === "seed";
    });

    // set "control_after_generate" fixed
    if (seedWidget && seedWidget.linkedWidgets && seedWidget.linkedWidgets[0]) {
      const widget = seedWidget.linkedWidgets[0];
      widget.value = "fixed";
    }

    // after node update
    setTimeout(function() {
      render(node);
    }, 128);
  }
});

api.addEventListener("promptQueued", async function() {
  for (const node of app.graph._nodes) {
    if (node.comfyClass === CLASS_NAME) {
      if (DEBUG) {
        console.log(CLASS_NAME+" promptQueued", node);
      }

      await increaseIndex(node);
    }
  }
});
