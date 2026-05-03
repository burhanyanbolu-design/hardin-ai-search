"""
Vercel Serverless Function - Proxy to AWS Submission Handler
This forwards HTTPS requests to the HTTP AWS server
"""

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# AWS submission handler endpoint
AWS_ENDPOINT = "http://3.11.229.68:8086/api/submit"

@app.route('/api/submit', methods=['POST'])
def submit_proxy():
    """Proxy submission requests to AWS server"""
    try:
        # Forward the request to AWS
        response = requests.post(
            AWS_ENDPOINT,
            json=request.json,
            timeout=30
        )
        
        # Return the response from AWS
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        return jsonify({
            "error": "Failed to connect to submission handler",
            "details": str(e)
        }), 500
