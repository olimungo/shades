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

    socket.emit('get-states');

    socket.on('update', payload => {
        shades = payload.shades;

        removeShadeElements();
        addShadeElements();
        updateGroups();
    });
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
            const template = document.getElementById('shade-button');
            const templateContent = template.content;

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
            this._selected = !this._selected;
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
function removeShadeElements() {
    shadeElements = shadeElements.filter(shadeElement => {
        if (!shades.some(item => item.netId == shadeElement.label)) {
            shadeElement.parentNode.removeChild(shadeElement);
            return false;
        }

        return true;
    });
}

// Add newly connected devices and update the state of the ones already existing
function addShadeElements() {
    let index = 0;

    shades.forEach(item => {
        if (index < shadeElements.length) {
            if (item.netId < shadeElements[index].label) {
                // Add new shade and set state
                const shadeElement = document.createElement('shade-button');
                shadeElement.label = item.netId;
                setGroup(shadeElement, item.group);
                setState(shadeElement, item.state);

                shadeDivs.insertBefore(shadeElement, shadeElements[index]);
                shadeElements.splice(index, 0, shadeElement);
            } else {
                // Element already in the DOM. Only have to set state
                setGroup(shadeElements[index], item.group);
                setState(shadeElements[index], item.state);
            }
        } else {
            // Add new shade at the end and set state;
            const newShadeElement = document.createElement('shade-button');
            newShadeElement.label = item.netId;
            setGroup(newShadeElement, item.group);
            setState(newShadeElement, item.state);

            shadeDivs.appendChild(newShadeElement);
            shadeElements.push(newShadeElement);
        }

        index++;
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

    if (group != '') {
        filtered = groups.filter(item => item.label == group);

        if (filtered.length == 0) {
            groups.push({ label: group, date: new Date() });
        } else {
            filtered[0].date = new Date();
        }
    }
}

function updateGroups() {
    const now = new Date().getTime();

    // Remove groups that weren't updated since 35 seconds
    groups = groups.filter(
        item => item.date == -1 || now - item.date.getTime() < 35000
    );

    // Remove the groups in the DOM
    groupElements = groupElements.filter(groupElement => {
        if (!groups.some(item => item.label == groupElement.label)) {
            groupElement.parentNode.removeChild(groupElement);
            return false;
        }

        return true;
    });

    // Remove All and None
    let [all, none, ...newGroups] = [...groups];

    // Keep only new groups and sort
    newGroups = newGroups
        .filter(item => !groupElements.some(elem => elem.label == item.label))
        .sort((a, b) => (a.label < b.label ? -1 : 1));

    // Add back All and None if not yet created
    if (groupElements.length == 0) {
        newGroups = [all, none, ...newGroups];
    }

    // Insert new groups into the DOM
    let index = 2;

    newGroups.forEach(element => {
        let inserted = false;

        while (index < groupElements.length) {
            //console.log(element);
            //console.log(groupElements[index]);
            if (element.label < groupElements[index].label) {
                const groupElement = document.createElement('group-button');
                groupElement.label = element.label;

                groupDivs.insertBefore(groupElement, groupElements[index]);
                groupElements.splice(index, 0, groupElement);

                inserted = true;

                break;
            }

            index++;
        }

        if (!inserted) {
            // Add at the end
            const groupElement = document.createElement('group-button');
            groupElement.label = element.label;

            groupDivs.appendChild(groupElement);
            groupElements.push(groupElement);
        }
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
