// // Pinulator Scanner

// // PinEntry: {
// //   name: string,
// //   namespace: string,
// //   value: Any,
// //   type: string
// //   html_template: {"topic": string, "value": string},
// //   value_history: List[(Any, datetime)]
// // }

document.addEventListener("DOMContentLoaded", () => {
  const refreshButton = document.getElementById("refreshButton");
  const refreshRateSelect = document.getElementById("refreshRate");
  const variablesTableBody = document.getElementById("variablesTable").querySelector("tbody");
  const addCanvasButton = document.getElementById("addCanvas");
  const canvasContainer = document.getElementById("canvasContainer");
  const variableRows = new Map();

  let refreshInterval;
  let currentRate = parseInt(refreshRateSelect.value);

  // ############################################################
  // ############################################################
  // ############################################################

  // Refresh button handler
  refreshButton.addEventListener("click", fetchAllPins);

  // Refresh rate change handler
  refreshRateSelect.addEventListener("change", () => {
    currentRate = parseInt(refreshRateSelect.value);
    clearInterval(refreshInterval);
    if (currentRate > 0) refreshInterval = setInterval(fetchAllPins, currentRate);
  });

  // Add canvas button handler
  addCanvasButton.addEventListener("click", () => {
    const canvasWrapper = document.createElement("div");
    canvasWrapper.classList.add("canvas-wrapper");
    canvasWrapper.innerHTML = `
            <button class="removeCanvas">Remove Canvas</button>
            <button class="addVariable">Add Variable</button>
            <canvas></canvas>
        `;
    canvasContainer.appendChild(canvasWrapper);

    const removeCanvasButton = canvasWrapper.querySelector(".removeCanvas");
    removeCanvasButton.addEventListener("click", () => {
      canvasContainer.removeChild(canvasWrapper);
    });

    // Add functionality to handle adding variables and drawing on the canvas
  });

  // ############################################################
  // ############################################################
  // ############################################################

  // Fetch all pins periodically
  const fetchAllPins = async () => {
    try {
      const response = await fetch("/all_pins");
      const pins = await response.json();
      console.log("Fetched pins:", pins);
      updateVariablesTable(pins);
    } catch (error) {
      console.error("Error fetching pins:", error);
    }
  };

  // Update the variables table
  const updateVariablesTable = (pins) => {
    // TODO: group-by namespace. Currently the challenge with this is the sorting of the rows
    const newPins = new Set(pins.map((pin) => pin.name));
    // Update existing rows and add new ones
    pins.forEach((pin) => {
      if (variableRows.has(pin.name)) {
        console.log("Updating existing row -> ", pin.name);
        updateExistingPin(pin);
      } else {
        console.log("Adding new row -> ", pin.name);
        addNewPin(pin);
      }
    });

    // Turn font-color to gray for removed variables
    variableRows.forEach((row, name) => {
      if (!newPins.has(name)) {
        row.querySelector(".topic").style.color = "gray";
      }
    });
  };

  const updateExistingPin = (pin) => {
    const row = variableRows.get(pin.name);
    const valueElement = row.querySelector(".value");
    fetch(`/pins/${pin.name}/read`)
      .then((response) => response.json())
      .then((data) => {
        console.log(`Updating of ${pin.name} -> ${data.value}`);
        valueElement.textContent = data.value;
        row.querySelector(".topic").style.color = "black";
      })
      .catch((error) => {
        console.error(`Error fetching ${pin.name}:`, error);
        row.querySelector(".topic").style.color = "red";
      });
  };

  const addNewPin = (pin) => {
    const row = document.createElement("tr");
    const topic = document.createElement("td");
    const value = document.createElement("td");
    topic.classList.add("topic");
    value.classList.add("value");
    topic.innerHTML = pin.html_template.topic;
    value.innerHTML = pin.html_template.value;
    row.appendChild(topic);
    row.appendChild(value);
    variablesTableBody.appendChild(row);
    variableRows.set(pin.name, row);
  };

  // ############################################################
  // ############################################################
  // ############################################################
  // Initial fetch and set interval
  fetchAllPins();
  refreshInterval = setInterval(fetchAllPins, currentRate);
});
