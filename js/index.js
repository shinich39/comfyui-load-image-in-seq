import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { $el } from "../../scripts/ui.js";

const DEBUG = false;
const CLASS_NAME = "Load Image In Seq";

$el("style", {
	textContent: `
	.shinich39-load-image-in-seq-text { background-color: #222; padding: 2px; color: #ddd; }
  `,
	parent: document.body,
});

function updateIndexHandler(event) {
	const nodes = app.graph._nodes_by_id;
  const updates = event.detail;

  if (DEBUG) {
    console.log(CLASS_NAME + ".nodes:", nodes);
    console.log(CLASS_NAME + ".updates:", updates);
  }

	for (let i in nodes) {
		const node = nodes[i];

    if (node.type !== CLASS_NAME) {
      continue;
    }
    if (!node.widgets) {
      continue;
    }

    if (DEBUG) {
      console.log(CLASS_NAME + ".node.id:", node.id);
      console.log(CLASS_NAME + ".node.type:", node.type);
      console.log(CLASS_NAME + ".node.widgets:", node.widgets);
    }

    const indexWidget = node.widgets.find(function(item) {
      return item.name == "index";
    });
    if (!indexWidget) {
      continue;
    }

    if (DEBUG) {
      console.log(CLASS_NAME + ".indexWidget:", indexWidget);
    }

    if (updates[node.id] !== undefined) {
      indexWidget.value = updates[node.id];
    }
	}
}

api.addEventListener("load-image-in-seq", updateIndexHandler);

app.registerExtension({
	name: "shinich39.LoadImageInSeq",
	nodeCreated(node, app) {
    if (node.comfyClass !== CLASS_NAME) {
      return;
    }
  
    if (DEBUG) {
      console.log("LoadImageInSeq.node", node);
    }
  }
});