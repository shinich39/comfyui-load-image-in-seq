import { api } from "../../scripts/api.js";

const DEBUG = false;
const NODE_TYPE = "Load Image #39";

function updateIndexHandler(event) {
	const nodes = app.graph._nodes_by_id;
  const updates = event.detail;

  if (DEBUG) {
    console.log("#39 nodes:", nodes);
    console.log("#39 updates:", updates);
  }

	for (let i in nodes) {
		const node = nodes[i];

    if (node.type !== NODE_TYPE) {
      continue;
    }
    if (!node.widgets) {
      continue;
    }

    if (DEBUG) {
      console.log("#39 node id:", node.id);
      console.log("#39 node type:", node.type);
      console.log("#39 node widgets:", node.widgets);
    }

    const indexWidget = node.widgets.find(function(item) {
      return item.name == "index";
    });
    if (!indexWidget) {
      continue;
    }

    if (DEBUG) {
      console.log("#39 index widget:", indexWidget);
    }

    if (updates[node.id] !== undefined) {
      indexWidget.value = updates[node.id];
    }
	}
}

api.addEventListener("load-image-39", updateIndexHandler);