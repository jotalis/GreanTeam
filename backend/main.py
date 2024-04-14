from fastapi import FastAPI, WebSocket, Form, HTTPException, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
import asyncio, os
import pandas as pd
from assistant_wrapper import update_user_prompt, process_user_prompt
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# client = AsyncOpenAI(
#     api_key=os.environ.get("OPENAI_API_KEY")
# )
client = OpenAI()

@app.get("/", response_class=HTMLResponse)
async def get_form():
    return """
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OpenAI GPT-4 Stream</title>
    </head>
    <body>
        <h1>Enter Prompt for OpenAI GPT-4</h1>
        <form action="#" onsubmit="connectWebSocket(); return false;">
            <input type="text" id="promptInput" placeholder="Enter your prompt here" />
            <button type="submit">Send Prompt</button>
        </form>
        <div id="responseContainer" style="white-space: pre-wrap;"></div> <!-- Added for displaying responses -->
        <script>
            function connectWebSocket() {
                // Clear previous responses
                document.getElementById('responseContainer').innerHTML = '';

                var ws = new WebSocket("ws://localhost:8000/ws");
                ws.onopen = function(event) {
                    var prompt = document.getElementById('promptInput').value;
                    ws.send(prompt);
                };
                ws.onmessage = function(event) {
                    console.log("Message from server ", event.data);
                    var container = document.getElementById('responseContainer');
                    container.textContent += event.data + '\'; // Update to append text
                };
                ws.onerror = function(event) {
                    console.error("WebSocket error observed:", event);
                };
                ws.onclose = function(event) {
                    console.log("WebSocket connection closed: ", event);
                };
            }
        </script>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive user prompt from the WebSocket
            user_prompt = await websocket.receive_text()
            user_prompt = update_user_prompt(user_prompt)
            # Process the user prompt using our function (assumed to be defined elsewhere in your module)
            response_text, image_data = process_user_prompt(client, user_prompt)

            # Send back the processed response and image data
            await websocket.send_text(response_text)
            await websocket.send_text(image_data)

    except WebSocketDisconnect:
        print("Client disconnected")
