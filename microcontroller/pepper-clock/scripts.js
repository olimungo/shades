window.addEventListener('DOMContentLoaded', (event) => {
    fetch('/settings/values')
        .then(response => response.json())
        .then(response => {
            setTagValue('eco-mode', response.ecoMode);
            setTagValue('essid', response.essid);
            setModeCheckbox();
        });
});

function setMode() {
    const tag = document.getElementById('eco-mode');
    value = tag.checked ? 1 : 0;

    setModeCheckbox()
    fetch(`/settings/set-eco-mode?val=${value}`).then();
}

function setModeCheckbox() {
    const tagLabel = document.getElementById('mode-label');
    const tag = document.getElementById('eco-mode');

    if (tag.checked) {
        tagLabel.textContent = "Eco mode";
    } else {
        tagLabel.textContent = "Animated mode";
    }
}

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

function checkConnection() {
    try {
        return fetchWithTimeout('/settings/connected', {
            timeout: 3000
        })
            .then(response => response.json())
            .then(response => {
                if (response.connected == '1') {
                    const connection = document.getElementById('connection'),
                        connectionSuccess = document.getElementById('connection-success');

                    connection.classList.add('hidden');
                    connectionSuccess.classList.remove('hidden');
                }
                else {
                    setTimeout(checkConnection, 3000);
                }
            });
    } catch (error) {
        setTimeout(checkConnection, 3000);
    }
}

function connect() {
    const essid = document.getElementById('essid'),
        pwd = document.getElementById('pwd'),
        main = document.getElementById('main'),
        connection = document.getElementById('connection');

    main.classList.add('hidden');
    connection.classList.remove('hidden');

    fetch(`/connect?essid=${essid.value}&password=${pwd.value}`).then();

    setTimeout(checkConnection, 3000);
}

function showMain() {
    const main = document.getElementById('main'),
        connectionSuccess = document.getElementById('connection-success');

    connectionSuccess.classList.add('hidden');
    main.classList.remove('hidden');
}

function shutdownAp() {
    fetch(`/settings/shutdown-ap`).then();

    const main = document.getElementById('main'),
        apShutdown = document.getElementById('ap-shutdown');

    main.classList.add('hidden');
    apShutdown.classList.remove('hidden');
}