from fastapi import FastAPI, WebSocket, Form, HTTPException, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
import asyncio, os
import pandas as pd
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

client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

df = pd.read_csv("./final_preprocessed.csv")
#retrieve only the ts_booking_at column

column_descriptions = """
searches.tsv : Contains a row for each set of searches that a user does for Dublin.
ds : Date of the search
id_user : Alphanumeric user_id
ds_checkin : Date stamp of the check-in date of the search
ds_checkout : Date stamp of the check-out date of the search
n_searches : Number of searches in the search set
n_nights : The number of nights the search was for
n_guests_min : The minimum number of guests selected in a search set
n_guests_max : The maximum number of guests selected in a search set
origin_country : The country the search was from
filter_price_min : The value of the lower bound of the price filter, if the user used it
filter_price_max : The value of the upper bound of the price filter, if the user used it
filter_room_types : The room types that the user filtered by, if the user used the room_types filter
filter_neighborhoods : The neighborhoods types that the user filtered by, if the user used the neighborhoods filter

contacts.tsv : Contains a row for every time that an assigned visitor makes an inquiry for a stay in a listing in Dublin.
id_guest : Alphanumeric user_id of the guest making the inquiry
id_host : Alphanumeric user_id of the host of the listing to which the inquiry is made
id_listing : Alphanumeric identifier for the listing to which the inquiry is made
ts_contact_at : UTC timestamp of the moment the inquiry is made.
ts_reply_at : UTC timestamp of the moment the host replies to the inquiry, if so
ts_accepted_at : UTC timestamp of the moment the host accepts the inquiry, if so
ts_booking_at : UTC timestamp of the moment the booking is made, if so
ds_checkin : Date stamp of the check-in date of the inquiry
ds_checkout : Date stamp of the check-out date of the inquiry
n_guests : The number of guests the inquiry is for
n_messages : The total number of messages that were sent around this inquiry
"""


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
            user_prompt = await websocket.receive_text()

            # Step 1: Identify relevant data
            columns = df.columns.to_list()
            print(columns)
            # init_prompt = f"Given the question: '{user_prompt}' and the dataset columns: '{columns}', what data columns are necessary to answer it? Return only the column names separated by commas \n\nColumn Information: '{column_descriptions}'\nSelect only the necessary columns"
            # init_response = await client.chat.completions.create(
            #     model="gpt-3.5-turbo-0125",
            #     messages=[{"role": "user", "content": init_prompt}],
            # )
            # necessary_columns = ['user_id']
            necessary_columns = []
            # print(init_response.choices[0].message.content.strip())
            # necessary_columns += init_response.choices[0].message.content.strip().replace("'", "").split(',')
            # print(necessary_columns)
            # filtered_df = df[necessary_columns]
            # print("filtered")
            # Initialize or reset necessary_columns if not yet defined or to clear old data
            necessary_columns = []

            # Extract the string from the response and prepare by removing single quotes
            # columns_string = init_response.choices[0].message.content.strip().replace("'", "")
    
            # Split the string into a list, strip each element of leading/trailing spaces, and append to necessary_columns
            # necessary_columns.extend([column.strip() for column in columns_string.split(',')])

            # Print the cleaned column names
            print(df.columns)
            necessary_columns = ['ds_checkin', 'ds_checkout']
            filtered_df = df[necessary_columns]
            print(necessary_columns)
            
            csv_context = filtered_df.to_string(index=False)
            print("converting to string")
            
            # # Step 2: Filter the DataFrame
            # if all(column in df.columns for column in necessary_columns):
            #     filtered_df = df[necessary_columns]
            #     data_context = filtered_df.to_string(index=False)
            # else:
            #     await websocket.send_text("Some of the specified columns do not exist in the data.")
            #     continue

            # #print the dimension of the dataframe
            # print(filtered_df.shape)

            # Step 3: Detailed query with filtered data
            detailed_prompt = fr"{user_prompt}\n\nData: {csv_context}\nUse only columns that exist in both the data and column descriptions: {column_descriptions}"
            print("sending prompt")
            stream = await client.chat.completions.create(
                model="gpt-4-turbo-2024-04-09",
                messages=[
                    # {"role": "system", "content": "You are a chatbot that responds with as minimal of an answer as possible . Do not write any sentences to explain. Just write the answer to the user's question. Respond with a single word or a short phrase."},
                    {"role": "user", "content": detailed_prompt}
                ],
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    await websocket.send_text(chunk.choices[0].delta.content)
            print("done")
    #     while True:
    #         user_prompt = await websocket.receive_text()
    #         full_prompt = f"{csv_context}\n\nPrompt: {user_prompt}"
    #         stream = await client.chat.completions.create(
    #             model="gpt-4",
    #             messages=[{"role": "user", "content": full_prompt}],
    #             stream=True,
    #         )
    #         async for chunk in stream:
    #             if chunk.choices[0].delta.content:
    #                 await websocket.send_text(chunk.choices[0].delta.content)
    except WebSocketDisconnect:
        print("Client disconnected")
