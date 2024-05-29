import pandas as pd
from flask import Flask, request, jsonify

# Specify the path to your Excel file
file_path = 'Sample Questions Demo.xlsx'

# Read the Excel file
df = pd.read_excel(file_path)

# Define the find_answer function
def find_answer(question, df):
    # Normalize the question for case-insensitive comparison
    normalized_question = question.lower().strip()

    # Iterate through the DataFrame to find the matching question
    for idx, row in df.iterrows():
        if row['Question'].lower().strip() == normalized_question:
            return row['Answer']

    # If no match is found, return a default message
    return "Please ask again."

# Initialize the Flask application
app = Flask(__name__)

# Define a route to handle the POST request
@app.route('/get_answer', methods=['POST'])
def get_answer():
    # Parse the request to get the question
    data = request.get_json()
    question = data.get('question', '')

    # Use the find_answer function to find the answer
    answer = find_answer(question, df)

    # Return the answer as a JSON response
    return jsonify({'answer': answer})

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
