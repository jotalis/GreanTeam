from fastapi import FastAPI, WebSocket, Form, HTTPException, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
import asyncio, os, json
import pandas as pd
from assistant_wrapper import update_user_prompt, process_user_prompt
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            background-image : url('static/dublindive_bg2.png');
            background-color: #f5f5f5;
        }
        #chatbox {
            width: 500px;
            height: 600px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            background: white;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        #messages {
            height: 450px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 4px;
            background: #efefef;
        }
        .message {
            padding: 8px;
            margin: 4px 0;
            border-radius: 4px;
            max-width: 65%;
            align-self: flex-end;
        }
        .sent-message {
            background-color: #007bff;
            color: white;
            margin-left: auto;
            margin-right: 10px; 
            align-self: flex-end; 

        }
        .received-message {
            background-color: #e0e0e0;
            color: black;
            margin-left: 10px; 
            margin-right: auto;
            align-self: flex-start;
        }
        .typing-indicator {
            padding: 8px;
            margin: 4px 10px auto 4px;
            border-radius: 4px;
            background-color: #e0e0e0;
            color: black;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            max-width: 65%;
            align-self: flex-start; 
        }
        .typing-indicator span {
            height: 8px;
            width: 8px;
            background-color: #9E9E9E;
            border-radius: 50%;
            display: inline-block;
            margin: 0 5px;
            animation: typing 1s infinite;
        }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        .message-image {
            max-width: 65%;
            border-radius: 4px;
            margin-top: 10px;
            align-self: flex-end; 
            margin-left: 10px;
            margin-right: auto;
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
        #header-text {
            position: absolute;
            top: 30px;
            left: 30px;
            font-size: 48px;
            font-weight: bold;
            text-transform: uppercase;
            color: #333;
        }
    </style>
</head>
<body>
<div id="header-text">BOBBY</div>
    <div id="chatbox">
        <div id="messages"></div>
        <input type="text" id="messageInput" placeholder="Type your message here...">
        <button id="sendButton">Send</button>
    </div>

    <script>
        const ws = new WebSocket('ws://localhost:8000/ws');
        const messagesElement = document.getElementById('messages');

        ws.onopen = function() {
            console.log('WebSocket connection established');
            
        };

        ws.onmessage = function(event) {
            console.log('Message received: ', event.data);
            removeTypingIndicator();
            const data = JSON.parse(event.data);
            if (data.text) {
                addMessage(data.text, 'received-message');
            }
            if (data.image) {
                addImage(data.image);
            }
            messagesElement.scrollTop = messagesElement.scrollHeight; // Scroll to the bottom
        };

        ws.onerror = function(error) {
            console.error('WebSocket Error: ', error);
            removeTypingIndicator();
        };

        ws.onclose = function() {
            console.log('WebSocket connection closed');
            removeTypingIndicator();
        };

        document.getElementById('sendButton').addEventListener('click', function() {
            const inputElement = document.getElementById('messageInput');
            const message = inputElement.value;
            if (message.trim() !== '') {
                ws.send(message);
                addMessage(message, 'sent-message');
                showTypingIndicator();
                inputElement.value = ''; // Clear the input box
            }
        });

        function showTypingIndicator() {
            const typingIndicator = document.createElement('div');
            typingIndicator.classList.add('message', 'typing-indicator');
            typingIndicator.innerHTML = '<span></span><span></span><span></span> Bobby is typing...';
            messagesElement.appendChild(typingIndicator);
        }

        function removeTypingIndicator() {
            const typingIndicator = document.querySelector('.typing-indicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }

        function addMessage(text, className) {
            const newMessage = document.createElement('div');
            newMessage.textContent = text;
            newMessage.classList.add('message', className);
            messagesElement.appendChild(newMessage);
        }

        function addImage(base64Image) {
            const imgElement = document.createElement('img');
            imgElement.src = `data:image/jpeg;base64,${base64Image}`;
            imgElement.classList.add('message-image');
            messagesElement.appendChild(imgElement);
        }

        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                document.getElementById('sendButton').click();
            }
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
