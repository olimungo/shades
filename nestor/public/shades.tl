<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">

    <title>nestor</title>

    <link rel="stylesheet" type="text/css" href="shades.css">
    <link href="https://fonts.googleapis.com/css?family=Roboto:300,700&display=swap" rel="stylesheet">
</head>

<body>

    <div id="main">
        <div class="title align-horizontal">
            <div>nestor<span class="category">| shades</span></div>
        </div>

        <div><span class="ip">${d.ip}</span></div>

        <div class="vertical-spacer-big"></div>

        <div class="align-vertical">
            <button onclick="emitCommand('up')">
                <svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 -1 32 32" xml:space="preserve"
                    class="svg">
                    <path d="M18.221,7.206l9.585,9.585c0.879,0.879,0.879,2.317,0,3.195l-0.8,0.801c-0.877,0.878-2.316,0.878-3.194,0 
                        l-7.315-7.315l-7.315,7.315c-0.878,0.878-2.317,0.878-3.194,0l-0.8-0.801c-0.879-0.878-0.879-2.316,0-3.195l9.587-9.585 
                        c0.471-0.472,1.103-0.682,1.723-0.647C17.115,6.524,17.748,6.734,18.221,7.206z" fill="#ffa500" />
                </svg>
            </button>

            <div class="vertical-spacer"></div>

            <button onclick="emitCommand('stop')">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -150 1792 2042" class="svg">
                    <path d="M1216 1184v-576q0-14-9-23t-23-9h-576q-14 0-23 9t-9 23v576q0 14 9 23t23 9h576q14 0 23-9t9-23zm448-288q0 
                        209-103 385.5t-279.5 279.5-385.5 103-385.5-103-279.5-279.5-103-385.5 
                        103-385.5 279.5-279.5 385.5-103 385.5 103 279.5 279.5 103 385.5z" fill="#ffa500" />
                </svg>
            </button>

            <div class="vertical-spacer"></div>

            <button onclick="emitCommand('down')">
                <svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 -1 32 32" xml:space="preserve"
                    class="svg">
                    <path d="M14.77,23.795L5.185,14.21c-0.879-0.879-0.879-2.317,0-3.195l0.8-0.801c0.877-0.878,2.316-0.878,3.194,0 
                        l7.315,7.315l7.316-7.315c0.878-0.878,2.317-0.878,3.194,0l0.8,0.801c0.879,0.878,0.879,2.316,0,3.195l-9.587,9.585 
                        c-0.471,0.472-1.104,0.682-1.723,0.647C15.875,24.477,15.243,24.267,14.77,23.795z"
                        fill="#ffa500" />
                </svg>
            </button>

            <div class="vertical-spacer-big"></div>
        </div>
    </div>

    <div id="groups" class="groups"></div>

    <div class="vertical-spacer-small"></div>

    <div id="shades" class="shades"></div>

    <template id="group-button">
        <style>
            .box {
                color: orange;
                border: solid 1px orange;
                padding: .5rem;
                border-radius: .5rem;
                margin: .5rem;
                padding: 1.5rem 2rem;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                font-weight: 600;
                font-size: 2.5rem;
            }
        </style>

        <div id="box" class="box">default</div>
    </template>

    <template id="shade-button">
        <style>
            .component {
                font-size: 1.5rem;
                display: flex;
                flex-direction: column;
                align-items: center;
                cursor: pointer;
            }

            .box {
                color: orange;
                border: solid 1px orange;
                padding: 1rem;
                border-radius: .5rem;
                margin: .5rem;
                width: 3.5rem;
                height: 3.5rem;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 2.5rem;
            }

            .border {
                width: 4rem;
                border-top: solid .25rem transparent;
            }

            .highlight {
                border-color: orange;
            }

            .selected {
                background: orange;
                color: #222;
            }
        </style>

        <div class="component">
            <div id="up" class="border up"></div>
            <div id="box" class="box">default</div>
            <div id="down" class="border down"></div>
        </div>
    </template>

    <script src="/socket.io/socket.io.js"></script>
    <script src="shades.js"></script>
</body>

</html>