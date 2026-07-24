const background = document.getElementById("background");
const reward = document.getElementById("rewardImage");
const historyContainer = document.getElementById("rewardHistoryBody");
const userName = document.getElementById("userName");
const queue = [];
let busy = false;
const sounds = {};

async function getSoundFiles() {
  const response = await fetch("./soundsDir.json");
  const soundsDict = await response.json();
  Object.keys(soundsDict).forEach((key) => {
    sounds[key] = new Audio("./sounds/" + soundsDict[key]);
  });
}

async function loadJSON() {
  const response = await fetch("./displayconfig.json");
  const configData = await response.json();
  return configData;
}

function makeVisible() {
  sounds.coin.play();
  background.className = "visible";
  setTimeout(() => {
    sounds.crank.play();
    setTimeout(() => {
      sounds.rumble.play();
      setTimeout(() => {
        sounds.open.play();
        historyContainer.innerHTML = "";
        userName.textContent =
          queue[0].chatter + " has redeemed " + queue[0].name;
        reward.src = queue[0].path;
        for (let x = 0; x < queue[0].previous_rewards.length; x++) {
          const wrapper = document.createElement('div')
          wrapper.className = "historyTileWrapper"
          const tile = document.createElement("img");
          tile.src = queue[0].previous_rewards[x].RewardPath;
          tile.className = "historyTile";
          wrapper.appendChild(tile);
          const counter = document.createElement("span")
          counter.className = "counter"
          counter.textContent = queue[0].previous_rewards[x].CountOfRedeems
          wrapper.appendChild(counter)
          historyContainer.appendChild(wrapper)
        }
        setTimeout(() => {
          reward.className = "visible";
          userName.className = "visible";
          historyContainer.className = "visible";
          sounds.celebrate.play()
          setTimeout(() => {
            queueManager();
            
          }, displayDuration * 1000)
          
          
        }, fadeInDelay * 1000);
      }, sounds.rumble.duration * 1000);
    }, sounds.crank.duration * 1000);
  }, sounds.coin.duration * 1000);
}

function changeReward() {
  reward.className = "hidden";
  userName.className = "hidden";
  historyContainer.className = "hidden";
  setTimeout(() => {
    makeVisible();
  }, 3300);
}

function makeHidden() {
  setTimeout(() => {
    reward.className = "hidden";
    background.className = "hidden";
    userName.className = "hidden";
    historyContainer.className = "hidden";
    busy = false;
  }, displayDuration * 1000);
}

function queueManager() {
  queue.shift();
  if (queue.length > 0) {
    setTimeout(() => {
      changeReward();
    }, displayDuration * 1000);
  } else {
    makeHidden();
  }
}

function connect() {
  const socket = new WebSocket("ws://localhost:" + config.websocket_port);
  socket.onmessage = function (event) {
    queue.push(JSON.parse(event.data));
    console.log("Data recieved from websocket: " + event.data);
    if (!busy) {
      makeVisible();
      busy = true;
    }
  };
  socket.onclose = function () {
    setTimeout(() => {
      connect();
    }, 2500);
  };
}

const config = await loadJSON();
await getSoundFiles();
const fadeInDelay = config.overlay_duration_fade_in_gap;
const displayDuration = config.overlay_duration_hold;
connect();
