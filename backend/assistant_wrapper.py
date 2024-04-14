from event_handler import EventHandler
from openai import OpenAI
from dotenv import load_dotenv
import base64
load_dotenv()


def update_user_prompt(prompt):
    
    prompt += """
    Generate code to perform the calculations to answer. Then, create a visualization using seaborn. 
    'file-elY239Qugdm6pfRvaGXymIzL' is a '.txt' containing data information about what each column represents in the csv data files above. Use the information in the text file to know which columns to extract from each csv.
    'file-TzOVAHko5TwyrRsaPySmIR0Z' is called "searches.csv" and 'file-4FKpqlvJOZqxNUfIJHAHRGJY' is called "contacts.csv". They are both datasets that contain data
    """
    return prompt

def process_user_prompt(client, user_prompt):

    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_prompt
    )
    
    event_handler = EventHandler()

    # Start streaming the responses
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id="asst_1AVGmHhCpOt0L1GL7ykWNlYi", 
        instructions="Answer with minimal text and output image data",
        event_handler=event_handler,
    ) as stream:
        stream.until_done()

    # Extract the answer and image data using the event handler
    text_response = event_handler.text_delta_values
    image_data = event_handler.image_data

    # Format the prompt for the chat completion
    prompt = f"""
    Extract the answer to the user's prompt from the text. 

    User prompt: '{user_prompt}'
    Text: '{text_response}'
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract the text content and image data
    extracted_text = response.choices[0].message.content.strip()

    # Return or print the results
    print(extracted_text)
    print(event_handler.image_id)
    
    image_data = client.files.content(event_handler.image_id)
    image_data_bytes = image_data.read()
    image_data = base64.b64encode(image_data_bytes).decode('utf-8')
    with open(f"./image-{event_handler.image_id}.png", "wb") as file:
        file.write(image_data_bytes)
        
    # print(extracted_text, image_data)
    return extracted_text, image_data


if __name__ == "__main__":
    # Example usage:
    client = OpenAI()
    process_user_prompt(client, update_user_prompt("""What day of the week were the most bookings made?"""))
