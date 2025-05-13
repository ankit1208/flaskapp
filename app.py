from flask import Flask, render_template, request
import requests
import json
import os

app = Flask(__name__)

# Schema for context
SCHEMA = """
Table: digx_ap_trans
Columns:
- TXN_ID
- PARTY_ID
- ACCOUNT_ID
- ACCOUNT_TYPE
- CURRENCY
- AMOUNT
- CREATED_BY (Name of person who initiated the transaction)
- NAME (Transaction name)
- CREATION_DATE
"""

def load_examples_from_json(filepath="examples.json"):
    if not os.path.exists(filepath):
        return ""
    
    with open(filepath, "r") as f:
        data = json.load(f)

    examples = data.get("examples", [])
    formatted = "\n".join([
        f"Example {i+1}:\nPrompt: {ex['prompt']}\nOutput: {ex['output']};"
        for i, ex in enumerate(examples)
    ])
    return formatted

def generate_sql_ollama(user_prompt):
    examples = load_examples_from_json()
    full_prompt = f"""{SCHEMA}
{examples}

Now, based on the above examples:
Prompt: {user_prompt}
Output:"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "codellama:7b-instruct",
            "prompt": full_prompt,
            "stream": False
        }
    )

    return response.json().get("response", "No response").strip()

@app.route("/", methods=["GET", "POST"])
def index():
    sql_output = None
    if request.method == "POST":
        prompt = request.form["prompt"]
        sql_output = generate_sql_ollama(prompt)
    return render_template("index.html", sql_output=sql_output)

if __name__ == "__main__":
    app.run(debug=True)
