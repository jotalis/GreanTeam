from fastapi import FastAPI, WebSocket, Form, HTTPException, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import asyncio, os, json
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
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebSocket Chatbox Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f5f5f5;
        }
        #chatbox {
            width: 350px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            background: white;
            padding: 20px;
            margin-bottom: 20px;
        }
        #responseText {
            height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        #responseImage {
            width: 100%;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        #messageInput {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: calc(100% - 24px);
            margin-bottom: 10px;
        }
        #sendButton {
            padding: 10px 20px;
            background-color: #007bff;
            border: none;
            border-radius: 4px;
            color: white;
            width: 100%;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        #sendButton:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div id="chatbox">
        <div id="responseText">Waiting for data...</div>
        <img id="responseImage" src="" alt="No Image" style="display: none;">
        <input type="text" id="messageInput" placeholder="Type your message here...">
        <button id="sendButton">Send</button>
    </div>

    <script>
        const ws = new WebSocket('ws://localhost:8000/ws');

        ws.onopen = function() {
            console.log('WebSocket connection established');
        };

        ws.onmessage = function(event) {
            console.log('Message received: ', event.data);
            const data = JSON.parse(event.data);
            if (data.text) {
                document.getElementById('responseText').textContent = data.text;
            }
            if (data.image) {
                const imgElement = document.getElementById('responseImage');
                imgElement.src = `data:image/jpeg;base64,${data.image}`;
                imgElement.style.display = 'block';
            }
        };

        ws.onerror = function(error) {
            console.error('WebSocket Error: ', error);
        };

        ws.onclose = function() {
            console.log('WebSocket connection closed');
        };

        document.getElementById('sendButton').addEventListener('click', function() {
            const message = document.getElementById('messageInput').value;
            ws.send(message);
            document.getElementById('messageInput').value = ''; // Clear the input box
        });
    </script>
</body>
</html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Connection accepted")
    try:
        while True:
            # Receive user prompt from the WebSocket
            # json_data = await websocket.receive_text()
            # print(f"Received data: {json_data}") 
            # data = json.loads(json_data)
            
            # user_prompt = data['user_prompt']
            user_prompt = await websocket.receive_text()
            user_prompt = update_user_prompt(user_prompt)
            print(f"Updated prompt: {user_prompt}")
            
            # Process the user prompt using our function (assumed to be defined elsewhere in your module)
            response_text, image_data = process_user_prompt(client, user_prompt)
            print(f"Response: {response_text}, Image Data: {image_data}")  

            # Send back the processed response and image data
            # await websocket.send_text({"text": response_text, "image": image_data})
            await websocket.send_text(json.dumps({"text": response_text, "image": image_data}))
            # await websocket.send_text(image_data)

    except WebSocketDisconnect:
        print("Client disconnected")
