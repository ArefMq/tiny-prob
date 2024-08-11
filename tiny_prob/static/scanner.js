// Pinulator Scanner

// PinEntry: {
//   name: string,
//   namespace: string,
//   value: Any,
//   type: string
//   html_template: {"topic": string, "value": string, "editable_field": string},
//   readable: bool,
//   writable: bool,
//   value_history: List[(Any, datetime)]
// }

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

  // Fetch all pins periodically
  const fetchAllPins = async () => {
    try {
      const response = await fetch("/all_pins");
      const pins = await response.json();
      // console.log("Fetched pins:", pins);
      updateVariablesTable(pins);
    } catch (error) {
      console.error("Error fetching pins:", error);
    }
  };

  // Update the variables table
  // This will update existing rows, add new rows and turn font-color to gray for removed variables.
  const updateVariablesTable = (pins) => {
    const newPins = new Set(pins.map((pin) => pin.name));
    var toUpdate = [];

    pins.forEach((pin) => {
      if (variableRows.has(pin.name)) {
        // console.log("Updating existing row -> ", pin.name);
        toUpdate.push(pin);
      } else {
        // console.log("Adding new row -> ", pin.name);
        addNewPin(pin);
      }
    });

    // Update existing pins
    updateExistingPin(toUpdate);

    // Turn font-color to gray for removed variables
    variableRows.forEach((row, name) => {
      if (!newPins.has(name)) {
        disablePin(row);
      }
    });
  };

  // Disable a pin
  const disablePin = (row) => {
    row.querySelector(".topic").style.color = "gray";
    // TODO: make read-only
  };

  const addNewPin = (pin) => {
    const addEditableField = (data_field) => {
      const editButton = document.createElement("button");
      editButton.classList.add("edit-button");
      editButton.textContent = "Edit";
      editButton.addEventListener("click", handleEditButtonClick);
      data_field.appendChild(editButton);

      const editControls = document.createElement("div");
      editControls.classList.add("edit-controls");
      editControls.style.display = "none";
      data_field.appendChild(editControls);

      editControls.innerHTML = pin.html_template.editable_html;
      const hiddenField = document.createElement("input");
      hiddenField.type = "hidden";
      hiddenField.name = "pin_name";
      hiddenField.value = pin.name;
      editControls.appendChild(hiddenField);

      const okButton = document.createElement("button");
      okButton.classList.add("ok-btn");
      okButton.textContent = "OK";
      okButton.addEventListener("click", handleOkButtonClick);
      editControls.appendChild(okButton);

      const cancelButton = document.createElement("button");
      cancelButton.classList.add("cancel-btn");
      cancelButton.textContent = "Cancel";
      cancelButton.addEventListener("click", handleCancelButtonClick);
      editControls.appendChild(cancelButton);
    };

    const row = document.createElement("tr");
    const topic = document.createElement("td");
    const data = document.createElement("td");
    topic.classList.add("topic");
    data.classList.add("data");
    topic.innerHTML = pin.html_template.topic;
    data.innerHTML = pin.html_template.value;

    if (pin.writable) {
      addEditableField(data);
    }

    row.appendChild(topic);
    row.appendChild(data);
    variablesTableBody.appendChild(row);
    variableRows.set(pin.name, row);
  };

  const updateExistingPin = (toUpdatePins) => {
    var payload = {
      read_pins: toUpdatePins.map((pin) => pin.name),
      write_pins: {}, // TODO: Implement write functionality
    };

    fetch("/pin_value", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((data) => {
        Object.entries(data.read_pins).forEach(([pin_name, pin_value]) => {
          const row = variableRows.get(pin_name);
          const dataElement = row.querySelector(".data");
          const valueElement = dataElement.querySelector(".value");
          // console.log(`Updating ${pin_name} -> ${pin_value}`);
          valueElement.textContent = pin_value;
        });
      })
      .catch((error) => {
        console.error("Error fetching pin value:", error);
      });
  };

  // ############################################################
  // #################### Edit ##################################
  // ############################################################

  // Function to handle the "Edit" button click
  const handleEditButtonClick = (event) => {
    const dataCell = event.target.closest(".data");
    const valueSpan = dataCell.querySelector(".value");
    const editControls = dataCell.querySelector(".edit-controls");
    const editInput = dataCell.querySelector(".edit-input");

    // Show the edit controls and hide the edit button
    valueSpan.style.display = "none";
    event.target.style.display = "none";
    editControls.style.display = "inline";
    editInput.value = valueSpan.textContent;
  };

  // Function to handle the "Cancel" button click
  const handleCancelButtonClick = (event) => {
    const dataCell = event.target.closest(".data");
    const valueSpan = dataCell.querySelector(".value");
    const editControls = dataCell.querySelector(".edit-controls");
    const editBtn = dataCell.querySelector(".edit-button");

    // Hide the edit controls and show the edit button
    valueSpan.style.display = "inline";
    editBtn.style.display = "inline";
    editControls.style.display = "none";
  };

  // Function to handle the "OK" button click
  const handleOkButtonClick = (event) => {
    const dataCell = event.target.closest(".data");
    const valueSpan = dataCell.querySelector(".value");
    const editControls = dataCell.querySelector(".edit-controls");
    const editInput = dataCell.querySelector(".edit-input");
    const editBtn = dataCell.querySelector(".edit-button");
    const pin_name = editControls.querySelector('input[name="pin_name"]').value;

    // Call the editVariable function with the new value
    editVariable(pin_name, editInput.value);

    // Update the value span with the new value
    valueSpan.textContent = editInput.value;

    // Hide the edit controls and show the edit button
    valueSpan.style.display = "inline";
    editBtn.style.display = "inline";
    editControls.style.display = "none";
  };

  // Function to handle the "Add Variable" button click
  const editVariable = (name, value) => {
    // console.log(`Editing ${name} -> ${value}`);
    const payload = {
      write_pins: {
        [name]: value
      }
    };

    fetch("/pin_value", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((data) => {
        // Handle the response data if needed
        console.log("Edit response:", data);
      })
      .catch((error) => {
        console.error("Error editing variable:", error);
      });
  };

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
  // Initial fetch and set interval
  fetchAllPins();
  refreshInterval = setInterval(fetchAllPins, currentRate);
});
