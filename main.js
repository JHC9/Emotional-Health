function handleStartStopClick() {
    var xhr = new XMLHttpRequest();
    var button = document.getElementById("start-stop-button");

    if (button.innerHTML === "Start") {
        xhr.open("GET", "/start_signal", true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                button.innerHTML = "Stop";
            }
        };
        xhr.send();
    } else if (button.innerHTML === "Stop") {
        xhr.open("GET", "/stop_signal", true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                button.innerHTML = "Start";
            }
        };
        xhr.send();
    }
}