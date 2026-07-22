const background = document.getElementById("background");
const reward = document.getElementById("rewardImage");
const historyContainer = document.getElementById("rewardHistoryBody");
const userName = document.getElementById("userName");
const queue = [];
let busy = false;
let config

async function loadJSON() {
    const response = await fetch("../config.json")
    config = await response.json()
    
}

function makeVisible() {
    historyContainer.innerHTML = "";
    background.className = "visible";
    userName.textContent = queue[0].chatter + " has redeemed " + queue[0].name;
    reward.src = queue[0].path;
    for (let x = 0; x < queue[0].previous_rewards.length; x++) {
            const tile = document.createElement("img");
            tile.src = queue[0].previous_rewards[x].RewardPath;
            tile.className = "historyTile";
            historyContainer.appendChild(tile);
        }
    setTimeout(() => {
        reward.className = "visible";
        userName.className = "visible";
        historyContainer.className = "visible";
        queueManager()
    }, fadeInDelay * 1000);
}

function changeReward() { 
    reward.className = "hidden";
    userName.className = "hidden";
    historyContainer.className = "hidden";
    setTimeout(() => {
        makeVisible()
    }, 3300)
}

function makeHidden() {

        reward.className = "hidden";
        background.className = "hidden";
        userName.className = "hidden";
        historyContainer.className = "hidden";
        busy = false

}


function queueManager() {
    queue.shift()
    setTimeout(() => {
        if (queue.length > 0) {
        
            changeReward()
        }
    else {
        makeHidden()
    }
    }, displayDuration * 1000)
    
}

function connect() {
    const socket = new WebSocket("ws://localhost:" + config.websocket_port);
    socket.onmessage = function (event) {
        queue.push(JSON.parse(event.data));
        console.log("Data recieved from websocket: " + event.data);
        if (!busy) {
            makeVisible()
            busy = true
        }
        
    };
    socket.onclose = function () {
        setTimeout(() => {
            connect();
        }, 2500);
    };
}

await loadJSON()
const fadeInDelay = config.overlay_duration_fade_in_gap;
const displayDuration = config.overlay_duration_hold;
connect();
