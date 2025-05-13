from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Schema + Examples for better responses
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

EXAMPLES = """
Example 1:
Prompt: List all transactions made in GBP currency.
Output: SELECT * FROM digx_ap_trans WHERE CURRENCY = 'GBP';

Example 2:
Prompt: Show all transaction IDs created by John Doe.
Output: SELECT TXN_ID FROM digx_ap_trans WHERE CREATED_BY = 'John Doe';

Example 3:
Prompt: What is the name of the transaction with ID E8IXC8UKIPLU?
Output: SELECT NAME FROM digx_ap_trans WHERE TXN_ID = 'E8IXC8UKIPLU';
"""

def generate_sql_ollama(user_prompt):
    full_prompt = f"""{SCHEMA}
{EXAMPLES}

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
    return response.json()["response"].strip()

@app.route("/", methods=["GET", "POST"])
def index():
    sql_output = None
    if request.method == "POST":
        prompt = request.form["prompt"]
        sql_output = generate_sql_ollama(prompt)
    return render_template("index.html", sql_output=sql_output)

if __name__ == "__main__":
    app.run(debug=True)
