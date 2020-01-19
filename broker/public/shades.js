let groups = [
    { label: 'All', date: -1 },
    { label: 'None', date: -1 }
];

let shades = [];
let groupDivs = [];
let shadeDivs = [];
let groupElements = [];
let shadeElements = [];
let socket;

// Executed when the DOM is ready
(function() {
    groupDivs = document.getElementById('groups');
    shadeDivs = document.getElementById('shades');

    // Setting up the websocket
    socket = io();

    socket.on('update', payload => {
        shades = payload.shades;
    });

    // Check for devices/groups to add or to remove
    setInterval(() => {
        // Create a copy in case the array gets updated while we work on it
        shadesCopy = [...shades];

        removeShadeElements(shadesCopy);
        addShadeElements(shadesCopy);

        updateGroups();
    }, 1000);
})();

customElements.define(
    'group-button',
    class extends HTMLElement {
        constructor() {
            super();
            const template = document.getElementById('group-button');
            const templateContent = template.content;

            this.addEventListener('click', groupClick);

            const shadowRoot = this.attachShadow({ mode: 'open' }).appendChild(
                templateContent.cloneNode(true)
            );
        }

        set label(value) {
            this._label = value;

            const box = this.shadowRoot.getElementById('box');
            box.textContent = value;
        }

        get label() {
            return this._label;
        }
    }
);

customElements.define(
    'shade-button',
    class extends HTMLElement {
        constructor() {
            super();
            let template = document.getElementById('shade-button');
            let templateContent = template.content;

            this.addEventListener('click', this.clicked);

            const shadowRoot = this.attachShadow({ mode: 'open' }).appendChild(
                templateContent.cloneNode(true)
            );
        }

        set label(value) {
            this._label = value;

            const box = this.shadowRoot.getElementById('box');
            box.textContent = value;
        }

        get label() {
            return this._label;
        }

        get state() {
            return this._state;
        }

        set state(value) {
            this._state = value;
        }

        get group() {
            return this._group;
        }

        set group(value) {
            this._group = value;
        }

        get selected() {
            return this._selected;
        }

        set selected(value) {
            this._selected = value;
            const box = this.shadowRoot.getElementById('box');

            if (value) {
                box.classList.add('selected');
            } else {
                box.classList.remove('selected');
            }
        }

        clicked() {
            const box = this.shadowRoot.getElementById('box');
            box.classList.toggle('selected');
        }

        runningUp() {
            const up = this.shadowRoot.getElementById('up');
            const down = this.shadowRoot.getElementById('down');
            down.classList.remove('highlight');

            clearInterval(this.highlightInterval);

            this.highlightInterval = setInterval(
                _ => up.classList.toggle('highlight'),
                500
            );
        }

        runningDown() {
            const up = this.shadowRoot.getElementById('up');
            const down = this.shadowRoot.getElementById('down');
            up.classList.remove('highlight');

            clearInterval(this.highlightInterval);

            this.highlightInterval = setInterval(
                _ => down.classList.toggle('highlight'),
                500
            );
        }

        onTop() {
            const up = this.shadowRoot.getElementById('up');
            const down = this.shadowRoot.getElementById('down');
            up.classList.add('highlight');
            down.classList.remove('highlight');
            clearInterval(this.highlightInterval);
        }

        onBottom() {
            const up = this.shadowRoot.getElementById('up');
            const down = this.shadowRoot.getElementById('down');
            up.classList.remove('highlight');
            down.classList.add('highlight');
            clearInterval(this.highlightInterval);
        }

        inBetween() {
            const up = this.shadowRoot.getElementById('up');
            const down = this.shadowRoot.getElementById('down');
            up.classList.remove('highlight');
            down.classList.remove('highlight');
            clearInterval(this.highlightInterval);
        }
    }
);

// Select the devices belonging to the group that was just selected
function groupClick(event) {
    const label = event.srcElement.label;

    if (label == 'All') {
        shadeElements.forEach(shadeElement => (shadeElement.selected = true));
    } else if (label == 'None') {
        shadeElements.forEach(shadeElement => (shadeElement.selected = false));
    } else {
        shadeElements.forEach(
            shadeElement =>
                (shadeElement.selected = shadeElement.group == label)
        );
    }
}

// Remove disconnected devices from the DOM
function removeShadeElements(shadesCopy) {
    shadeElements = shadeElements.filter(shadeElement => {
        toKeep =
            shadesCopy.filter(item => item.netId == shadeElement.label).length >
            0;

        if (!toKeep) {
            shadeElement.parentNode.removeChild(shadeElement);
        }

        return toKeep;
    });
}

// Add newly connected devices and update the state of the ones already existing
function addShadeElements(shadesCopy) {
    let index = 0;

    shadesCopy.forEach(item => {
        if (index < shadeElements.length) {
            const shadeElement = shadeElements[index];

            if (shadeElement.label > item.netId) {
                // Add new shade and set state
                const newShadeElement = document.createElement('shade-button');
                newShadeElement.label = item.netId;
                setGroup(newShadeElement, item.group);
                setState(newShadeElement, item.state);

                shadeDivs.insertBefore(newShadeElement, shadeElement);
                shadeElements.splice(index, 0, newShadeElement);
            } else {
                // Element already in the DOM. Only have to set state
                setGroup(shadeElement, item.group);
                setState(shadeElement, item.state);
            }

            index++;
        } else {
            // Add new shade at the end and set state;
            const newShadeElement = document.createElement('shade-button');
            newShadeElement.label = item.netId;
            setGroup(newShadeElement, item.group);
            setState(newShadeElement, item.state);

            shadeDivs.appendChild(newShadeElement);
            shadeElements.push(newShadeElement);
        }
    });
}

function setState(shadeElement, state) {
    if (shadeElement.state != state) {
        switch (state) {
            case 'RUNNING UP':
                shadeElement.runningUp();
                break;
            case 'RUNNING DOWN':
                shadeElement.runningDown();
                break;
            case 'TOP':
                shadeElement.onTop();
                break;
            case 'BOTTOM':
                shadeElement.onBottom();
                break;
            default:
                shadeElement.inBetween();
        }

        shadeElement.state = state;
    }
}

function setGroup(shadeElement, group) {
    shadeElement.group = group;

    filtered = groups.filter(item => item.label == group);

    if (filtered.length == 0) {
        groups.push({ label: group, date: new Date() });
    } else {
        filtered[0].date = new Date();
    }
}

function updateGroups() {
    const now = new Date().getTime();

    // Remove groups that weren't updated since 5 seconds
    groups = groups.filter(
        item => item.date == -1 || now - item.date.getTime() < 5000
    );

    // Clean the groups DIV in the DOM
    while (groupElements.length > 0) {
        groupElement = groupElements.pop();
        groupElement.parentNode.removeChild(groupElement);
    }

    // Recreate groups
    groups.forEach(element => {
        const groupElement = document.createElement('group-button');
        groupElement.label = element.label;

        groupDivs.appendChild(groupElement);
        groupElements.push(groupElement);
    });
}

function emitCommand(command) {
    netIds = shadeElements
        .filter(shadeElement => shadeElement.selected)
        .map(shadeElement => shadeElement.label);

    if (netIds.length > 0) {
        socket.emit(
            'mqtt-command',
            `{"topic": "shades/commands", "netIds": [${netIds}], "message": "${command}"}`
        );
    }
}
