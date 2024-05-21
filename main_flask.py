import openai
import time
from openai import OpenAI
import pandas as pd
import json
import csv
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

# Functions
def delete_file(client, file_id):
    client.files.delete(
        file_id=file_id,
    )

def delete_all_files(client):
    # Delete all existing files
    file_list = client.files.list()
    # Extracting existing files ids into an array
    docs_ids_list = [item.id for item in file_list.data]
    # Delete all existing files
    for id in docs_ids_list:
        delete_file(client, id)

def convert_string_to_csv(data_str, csv_filename='output.csv'):
    # Extract data between curly braces
    pattern = re.compile(r'\{([^}]+)\}')
    matches = pattern.findall(data_str)

    # Split each match by comma and then by colon to get key-value pairs
    data_list = []
    for match in matches:
        data_dict = {}
        items = match.split(',')
        for item in items:
            key, value = item.split(':', 1)
            data_dict[key.strip()] = value.strip()
        data_list.append(data_dict)

    # Define the CSV file header based on keys from one of the dictionaries
    header = list(data_list[0].keys())

    # Write data to CSV
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(data_list)

    # print(f'Data successfully written to {csv_filename}')

# Get list of available assistants ids
def get_assistants_ids_list(client):
    my_assistants = client.beta.assistants.list(
        order="desc",
        limit="20",
    )
    assistants = my_assistants.data
    assistants_dict = {"Create Assistant": "create-assistant"}
    for assistant in assistants:
        assistants_dict[assistant.name] = assistant.id

    assistants_list1 = list(assistants_dict.keys())
    assistants_list2 = list(assistants_dict.values())

    return assistants_list2

def chat_display(client, thread):
    final_message = ''
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    ).data

    for message in reversed(messages):
        if message.role in ["user", "assistant"]:
            for content in message.content:
                if content.type == "text":
                    ans = content.text.value
                    final_message += ans

    return final_message

# Main executable function
def main(selected_assistant_id, prompt, data_str):
    OAIK1 = "sk-proj-3JRgQ"
    OAIK2 = "BuQOQbRNaGMR"
    OAIK3 = "Q7UT3BlbkFJVhs"
    OAIK4 = "0Ks8aKl3Q2SAT6BKm"
    OAIK = OAIK1 + OAIK2 + OAIK3 + OAIK4
    openai_key = OAIK
    api_k = openai_key
    client = OpenAI(api_key=openai_key)

    if api_k:
        client = OpenAI(api_key=api_k)
        assistant_id_option = get_assistants_ids_list(client)

        if selected_assistant_id in assistant_id_option:
            delete_all_files(client)

            # Convert the string to CSV
            convert_string_to_csv(data_str, 'prompt_data.csv')

            # Step 1: Upload a file with an "assistants" purpose
            file = client.files.create(
                file=open("prompt_data.csv", "rb"),
                purpose='assistants'
            )

            # Step 2: Create a Thread
            thread = client.beta.threads.create()

            # Step 3: Add a Message to a Thread
            message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )

            # Step 3.1: Update assistant with the csv file
            assistant = client.beta.assistants.update(
                assistant_id=selected_assistant_id,
                tool_resources={
                    "code_interpreter": {
                        "file_ids": [file.id]
                    }
                }
            )

            # Step 4: Run the Assistant
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=selected_assistant_id,
                # instructions="Please address the user as Luis Bernal. The user has a premium account."
            )

            # Step 5: Get messages
            while True:
                # Wait for 5 seconds
                time.sleep(5)

                # Retrieve the run status
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )

                # If run is completed, get messages
                if run_status.status == 'completed':
                    final_message = chat_display(client, thread)
                    break

        else:
            final_message = 'The assistant DOES NOT exist!!'

        print(final_message)

    return final_message

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    selected_assistant_id = data.get('selected_assistant_id')
    prompt = data.get('prompt')
    data_str = data.get('data_str')

    answer = main(selected_assistant_id, prompt, data_str)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)
