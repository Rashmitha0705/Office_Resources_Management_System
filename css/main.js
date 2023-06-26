// static/main.js

function populateRooms() {
    var floorSelect = document.getElementById("floor");
    var roomSelect = document.getElementById("room");
  
    roomSelect.innerHTML = "";
  
    if (floorSelect.value === "GF") {
      for (var i = 1; i <= 5; i++) {
        var option = document.createElement("option");
        option.text = "GF" + i;
        option.value = "GF" + i;
        roomSelect.add(option);
      }
    } else {
      for (var i = 1; i <= 5; i++) {
        var option = document.createElement("option");
        option.text = floorSelect.value + i;
        option.value = floorSelect.value + i;
        roomSelect.add(option);
      }
    }
  }
  
  function addResource() {
    var resourceType = document.getElementById("resource_type").value;
    var floor = document.getElementById("floor").value;
    var room = document.getElementById("room").value;
    var quantity = document.getElementById("quantity").value;
  
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        document.getElementById("resource_form").reset();
        document.getElementById("success_message").style.display = "block";
      }
    };
    xhttp.open("POST", "/add_resource", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("resource_type=" + resourceType + "&floor=" + floor + "&room=" + room + "&quantity=" + quantity);
  }
  
  document.getElementById("floor").addEventListener("change", populateRooms);
  document.getElementById("resource_form").addEventListener("submit", function(event) {
    event.preventDefault();
    addResource();
  });
  