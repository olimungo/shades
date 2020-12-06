window.addEventListener('DOMContentLoaded', (event) => {
    fetch('/settings/values')
        .then(response => response.json())
        .then(response => {
            setTagValue('ip', response.ip);
            setTagValue('net-id', response.netId);
            setTagValue('tag-net-id', response.netId);
            setTagValue('group', response.group);
            setTagValue('motor-reversed', response.motorReversed);
            setTagValue('essid', response.essid);

            document.title = `Shade ${response.netId}`; 
        });
});

function setTagValue(tagId, value) {
    const tag = document.getElementById(tagId);
    tag.tagName == 'INPUT' ? tag.type == 'checkbox' ? (tag.checked = parseInt(value)) : (tag.value = value) : (tag.textContent = value);
}

function debounce(fn, wait = 100) {
    let timeout;

    return function (...args) {
        clearTimeout(timeout);

        timeout = setTimeout(() => {
            fn.apply(this, args);
        }, wait);
    };
}

function setNetId(value) {
    fetch(`/settings/net?id=${value}`).then();
    const tag = document.getElementById('tag-net-id');
    tag.textContent = value;
    document.title = `Shade ${value}`;
}

const debouncedSetNetId = debounce(setNetId, 500);

function setGroup(value) {
    fetch(`/settings/group?name=${value}`).then();
}

const debouncedSetGroup = debounce(setGroup, 500);

function displayMain() {
    const main = document.getElementById('main'),
        settings = document.getElementById('settings');

    main.classList.remove('hidden');
    settings.classList.add('hidden');
}

function displaySettings() {
    const main = document.getElementById('main'),
        settings = document.getElementById('settings');

    main.classList.add('hidden');
    settings.classList.remove('hidden');
}

async function fetchWithTimeout(resource, options) {
    const { timeout = 8000 } = options;
    
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
  
    const response = await fetch(resource, {
      ...options,
      signal: controller.signal  
    });
    clearTimeout(id);
  
    return response;
}

function displayConnectionInProgress() {
    const settings = document.getElementById('settings'),
        connection = document.getElementById('connection');

    settings.classList.add('hidden');
    connection.classList.remove('hidden');

    setTimeout(checkConnection, 3000);
}

function checkConnection() {
    try {
        return fetchWithTimeout('/settings/values', {
          timeout: 3000
        })
        .then(response => response.json())
        .then(response => {
            if (response.ip != "192.168.4.1") {
                setTagValue('new-ip', response.ip);

                const spinner = document.getElementById('spinner'),
                    newIp = document.getElementById('new-ip');

                spinner.classList.add('hidden');
                newIp.classList.remove('hidden');
            }
            else {
                setTimeout(checkConnection, 3000);
            }
        });
      } catch (error) {
        console.log(error.name === 'AbortError');
        setTimeout(checkConnection, 3000);
      }
}

function connect() {
    const essid = document.getElementById('essid');
    const pwd = document.getElementById('pwd');

    fetch(`/connect?essid=${essid.value}&password=${pwd.value}`).then();

    displayConnectionInProgress();
}