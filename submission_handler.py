"""
Submission Handler API for AWS Ubuntu Server
Handles tool submissions and saves them to the database
Run this on AWS Ubuntu: python submission_handler.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import hashlib
from github_knowledge_extractor import GitHubKnowledgeExtractor

app = Flask(__name__)
CORS(app)  # Allow requests from Vercel frontend

# Data directories
DATA_DIR = "data"
TOOLS_DIR = f"{DATA_DIR}/tools"
CONTRIBUTIONS_DIR = f"{DATA_DIR}/contributions"
AGENTS_DIR = f"{DATA_DIR}/agents"

# Initialize GitHub extractor
extractor = GitHubKnowledgeExtractor()


def generate_agent_id(agent_name: str) -> str:
    """Generate unique agent ID"""
    return hashlib.md5(agent_name.encode()).hexdigest()[:12]


def save_json(filepath: str, data: dict):
    """Save data to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: str) -> dict:
    """Load data from JSON file"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Hardin Submission Handler",
        "version": "1.0.0",
        "location": "AWS Ubuntu"
    })


@app.route('/api/submit', methods=['POST'])
def submit_tool():
    """
    Accept tool submissions from the website
    
    Request body:
    {
        "url": "https://example.com or https://github.com/user/repo",
        "contributor_name": "John Doe",
        "contributor_email": "john@example.com" (optional)
    }
    """
    data = request.json
    
    # Validate request
    submitted_url = data.get('url')
    if not submitted_url:
        return jsonify({"error": "URL is required"}), 400
    
    contributor_name = data.get('contributor_name', 'Community User')
    agent_id = generate_agent_id(contributor_name)
    
    print(f"📥 New submission from: {contributor_name}")
    print(f"🔗 URL: {submitted_url}")
    
    # Check if it's a GitHub URL
    is_github = 'github.com' in submitted_url.lower()
    
    try:
        if is_github:
            # Extract from GitHub
            print("🔍 Extracting from GitHub...")
            profile = extractor.extract_repo_knowledge(submitted_url)
            
            if 'error' in profile:
                return jsonify({"error": profile['error']}), 400
        else:
            # Create basic profile for non-GitHub URLs
            from urllib.parse import urlparse
            parsed = urlparse(submitted_url)
            domain = parsed.netloc.replace('www.', '')
            tool_name = domain.split('.')[0].title()
            
            profile = {
                "name": tool_name,
                "url": submitted_url,
                "github_url": submitted_url,
                "description": f"AI tool hosted at {domain}",
                "tagline": f"Community-submitted AI tool",
                "category": "ai_tool",
                "topics": ["ai", "community-submitted"],
                "language": "Unknown",
                "stars": 0,
                "is_community_submission": True,
                "submission_url": submitted_url
            }
        
        # Add contribution metadata
        profile['contribution'] = {
            "discovered_by": contributor_name,
            "agent_id": agent_id,
            "discovered_at": datetime.now().isoformat(),
            "reason": "Community submission via web form"
        }
        
        # Save tool profile
        tool_name = profile.get('name', 'unknown').lower().replace(' ', '-').replace('/', '-')
        tool_file = f"{TOOLS_DIR}/{tool_name}.json"
        
        # Check if tool already exists
        if os.path.exists(tool_file):
            return jsonify({
                "status": "duplicate",
                "message": f"Tool '{profile.get('name')}' already exists in our database!",
                "tool_name": tool_name
            }), 409
        
        save_json(tool_file, profile)
        print(f"✅ Saved: {tool_file}")
        
        # Record contribution
        contribution_record = {
            "type": "discovery",
            "agent_id": agent_id,
            "agent_name": contributor_name,
            "tool_name": tool_name,
            "url": submitted_url,
            "timestamp": datetime.now().isoformat(),
            "status": "approved"
        }
        
        contribution_file = f"{CONTRIBUTIONS_DIR}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_id}.json"
        save_json(contribution_file, contribution_record)
        
        print(f"🎉 Tool '{profile.get('name')}' added successfully!")
        
        return jsonify({
            "status": "success",
            "message": f"Thank you! '{profile.get('name')}' has been added to our database!",
            "tool_name": tool_name,
            "profile": profile
        }), 201
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            "error": "Failed to process submission",
            "details": str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get submission statistics"""
    tool_count = len([f for f in os.listdir(TOOLS_DIR) if f.endswith('.json')])
    contribution_count = len([f for f in os.listdir(CONTRIBUTIONS_DIR) if f.endswith('.json')])
    
    return jsonify({
        "total_tools": tool_count,
        "total_contributions": contribution_count,
        "last_updated": datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("🚀 Hardin Submission Handler")
    print("📡 Starting server on AWS Ubuntu...")
    print("🔗 Endpoint: http://3.11.229.68:5002/api/submit")
    print("💡 This server handles tool submissions from the website")
    
    # Run on port 5002 (different from main API on 5001)
    app.run(debug=True, host='0.0.0.0', port=5002)
