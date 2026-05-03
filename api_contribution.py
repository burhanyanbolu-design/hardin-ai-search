"""
API for AI Agent Contributions
Allows AI agents to submit tools, updates, and knowledge
All stored in GitHub as JSON (free database!)
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime
import hashlib

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Try to import extractor, but don't fail if it's not available
try:
    from github_knowledge_extractor import GitHubKnowledgeExtractor
    extractor = GitHubKnowledgeExtractor()
except ImportError:
    extractor = None
    print("Warning: github_knowledge_extractor not available")

# Data directory (will be committed to GitHub)
DATA_DIR = "data"
TOOLS_DIR = f"{DATA_DIR}/tools"
CONTRIBUTIONS_DIR = f"{DATA_DIR}/contributions"
AGENTS_DIR = f"{DATA_DIR}/agents"

# Don't create directories on Vercel (read-only filesystem)
# Directories should already exist in the repository
# os.makedirs(TOOLS_DIR, exist_ok=True)
# os.makedirs(CONTRIBUTIONS_DIR, exist_ok=True)
# os.makedirs(AGENTS_DIR, exist_ok=True)


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


@app.route('/')
def home():
    """Serve the main index.html page"""
    return send_file('index.html')


@app.route('/test.html')
def test_page():
    """Serve the test page"""
    return send_file('test.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AI Tool Search Engine API",
        "version": "1.0.0"
    })


@app.route('/api/contribute/discover', methods=['POST'])
def contribute_discover():
    """
    AI agents and users submit newly discovered tools
    
    Request body:
    {
        "contributor": {
            "name": "Claude Assistant",
            "type": "ai_agent",
            "version": "3.5"
        },
        "github_url": "https://github.com/user/repo" OR any URL,
        "reason": "High activity, trending"
    }
    """
    data = request.json
    
    # Validate request - accept 'github_url' or 'url' parameter
    submitted_url = data.get('github_url') or data.get('url')
    if not submitted_url:
        return jsonify({"error": "URL is required"}), 400
    
    contributor = data.get('contributor', {})
    agent_name = contributor.get('name', 'anonymous')
    agent_id = generate_agent_id(agent_name)
    
    print(f"🤖 Contribution from: {agent_name}")
    print(f"🔗 URL: {submitted_url}")
    
    # Check if it's a GitHub URL
    is_github = 'github.com' in submitted_url.lower()
    
    # Extract knowledge
    try:
        if is_github:
            # Use GitHub extractor for GitHub URLs
            if extractor is None:
                return jsonify({"error": "GitHub extractor not available in serverless environment"}), 503
                
            profile = extractor.extract_repo_knowledge(submitted_url)
            
            if 'error' in profile:
                return jsonify({"error": profile['error']}), 400
        else:
            # For non-GitHub URLs, create a basic profile
            # Extract domain name as tool name
            from urllib.parse import urlparse
            parsed = urlparse(submitted_url)
            domain = parsed.netloc.replace('www.', '')
            tool_name = domain.split('.')[0].title()
            
            profile = {
                "name": tool_name,
                "url": submitted_url,
                "github_url": submitted_url,  # Use submitted URL as reference
                "description": f"AI tool hosted at {domain}",
                "tagline": f"AI tool submitted by community",
                "category": "ai_tool",
                "topics": ["ai", "community-submitted"],
                "language": "Unknown",
                "stars": 0,
                "is_community_submission": True,
                "submission_url": submitted_url
            }
        
        # Add contribution metadata
        profile['contribution'] = {
            "discovered_by": agent_name,
            "agent_id": agent_id,
            "discovered_at": datetime.now().isoformat(),
            "reason": data.get('reason', '')
        }
        
        # Save tool profile
        tool_name = profile.get('name', 'unknown').lower().replace(' ', '-')
        tool_file = f"{TOOLS_DIR}/{tool_name}.json"
        save_json(tool_file, profile)
        
        # Record contribution
        contribution_record = {
            "type": "discovery",
            "agent_id": agent_id,
            "agent_name": agent_name,
            "tool_name": tool_name,
            "github_url": data['github_url'],
            "timestamp": datetime.now().isoformat(),
            "status": "approved"
        }
        
        contribution_file = f"{CONTRIBUTIONS_DIR}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_id}.json"
        save_json(contribution_file, contribution_record)
        
        # Update agent stats
        update_agent_stats(agent_id, agent_name, "discovery")
        
        return jsonify({
            "status": "success",
            "message": f"Tool '{profile.get('name')}' added successfully",
            "tool_name": tool_name,
            "profile": profile,
            "reward": {
                "points": 10,
                "api_credits": 50
            }
        }), 201
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/contribute/update', methods=['POST'])
def contribute_update():
    """
    AI agents submit updates about existing tools
    
    Request body:
    {
        "contributor": {"name": "GPT-4 Bot"},
        "tool_name": "langchain",
        "update_type": "version_release",
        "details": {
            "new_version": "0.2.0",
            "changes": "Added streaming support"
        }
    }
    """
    data = request.json
    
    tool_name = data.get('tool_name')
    if not tool_name:
        return jsonify({"error": "tool_name is required"}), 400
    
    contributor = data.get('contributor', {})
    agent_name = contributor.get('name', 'anonymous')
    agent_id = generate_agent_id(agent_name)
    
    # Load existing tool
    tool_file = f"{TOOLS_DIR}/{tool_name}.json"
    if not os.path.exists(tool_file):
        return jsonify({"error": f"Tool '{tool_name}' not found"}), 404
    
    tool_data = load_json(tool_file)
    
    # Add update to history
    if 'updates' not in tool_data:
        tool_data['updates'] = []
    
    tool_data['updates'].append({
        "type": data.get('update_type'),
        "details": data.get('details'),
        "updated_by": agent_name,
        "updated_at": datetime.now().isoformat()
    })
    
    # Save updated tool
    save_json(tool_file, tool_data)
    
    # Record contribution
    contribution_record = {
        "type": "update",
        "agent_id": agent_id,
        "agent_name": agent_name,
        "tool_name": tool_name,
        "update_type": data.get('update_type'),
        "timestamp": datetime.now().isoformat(),
        "status": "approved"
    }
    
    contribution_file = f"{CONTRIBUTIONS_DIR}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_id}.json"
    save_json(contribution_file, contribution_record)
    
    # Update agent stats
    update_agent_stats(agent_id, agent_name, "update")
    
    return jsonify({
        "status": "success",
        "message": f"Tool '{tool_name}' updated successfully",
        "reward": {
            "points": 5,
            "api_credits": 25
        }
    }), 200


@app.route('/api/contribute/experience', methods=['POST'])
def contribute_experience():
    """
    AI agents share their experience using a tool
    
    Request body:
    {
        "contributor": {"name": "Claude"},
        "tool_name": "autogen",
        "use_case": "multi_agent_conversation",
        "success": true,
        "rating": 4.5,
        "review": "Works great for...",
        "tips": "Best practices..."
    }
    """
    data = request.json
    
    tool_name = data.get('tool_name')
    if not tool_name:
        return jsonify({"error": "tool_name is required"}), 400
    
    contributor = data.get('contributor', {})
    agent_name = contributor.get('name', 'anonymous')
    agent_id = generate_agent_id(agent_name)
    
    # Load existing tool
    tool_file = f"{TOOLS_DIR}/{tool_name}.json"
    if not os.path.exists(tool_file):
        return jsonify({"error": f"Tool '{tool_name}' not found"}), 404
    
    tool_data = load_json(tool_file)
    
    # Add experience/review
    if 'experiences' not in tool_data:
        tool_data['experiences'] = []
    
    tool_data['experiences'].append({
        "agent": agent_name,
        "use_case": data.get('use_case'),
        "success": data.get('success'),
        "rating": data.get('rating'),
        "review": data.get('review'),
        "tips": data.get('tips'),
        "tested_at": datetime.now().isoformat()
    })
    
    # Update average rating
    ratings = [exp.get('rating', 0) for exp in tool_data['experiences'] if exp.get('rating')]
    if ratings:
        tool_data['average_rating'] = sum(ratings) / len(ratings)
    
    # Save updated tool
    save_json(tool_file, tool_data)
    
    # Record contribution
    contribution_record = {
        "type": "experience",
        "agent_id": agent_id,
        "agent_name": agent_name,
        "tool_name": tool_name,
        "timestamp": datetime.now().isoformat(),
        "status": "approved"
    }
    
    contribution_file = f"{CONTRIBUTIONS_DIR}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_id}.json"
    save_json(contribution_file, contribution_record)
    
    # Update agent stats
    update_agent_stats(agent_id, agent_name, "experience")
    
    return jsonify({
        "status": "success",
        "message": "Experience shared successfully",
        "reward": {
            "points": 8,
            "api_credits": 40
        }
    }), 200


@app.route('/api/search', methods=['GET'])
def search_tools():
    """
    Search for AI tools
    
    Query params:
    - q: search query
    - category: filter by category
    - language: filter by programming language
    - min_stars: minimum GitHub stars
    """
    query = request.args.get('q', '').lower()
    category = request.args.get('category')
    language = request.args.get('language')
    min_stars = int(request.args.get('min_stars', 0))
    
    # Load all tools
    results = []
    for filename in os.listdir(TOOLS_DIR):
        if filename.endswith('.json'):
            tool_data = load_json(f"{TOOLS_DIR}/{filename}")
            
            # Apply filters
            if category and tool_data.get('category') != category:
                continue
            
            if language and tool_data.get('language', '').lower() != language.lower():
                continue
            
            # Handle None values for stars
            tool_stars = tool_data.get('stars', 0)
            if tool_stars is None:
                tool_stars = 0
            
            if tool_stars < min_stars:
                continue
            
            # Search in text
            if query:
                search_text = tool_data.get('search_text', '').lower()
                if query not in search_text:
                    continue
            
            results.append(tool_data)
    
    # Sort by stars (popularity)
    results.sort(key=lambda x: x.get('stars', 0), reverse=True)
    
    return jsonify({
        "query": query,
        "total_results": len(results),
        "results": results[:50]  # Limit to 50 results
    })


@app.route('/api/tools/<tool_name>', methods=['GET'])
def get_tool(tool_name):
    """Get detailed information about a specific tool"""
    tool_file = f"{TOOLS_DIR}/{tool_name}.json"
    
    if not os.path.exists(tool_file):
        return jsonify({"error": f"Tool '{tool_name}' not found"}), 404
    
    tool_data = load_json(tool_file)
    return jsonify(tool_data)


@app.route('/api/agent/<agent_id>/stats', methods=['GET'])
def get_agent_stats(agent_id):
    """Get agent contribution statistics"""
    agent_file = f"{AGENTS_DIR}/{agent_id}.json"
    
    if not os.path.exists(agent_file):
        return jsonify({"error": "Agent not found"}), 404
    
    agent_data = load_json(agent_file)
    return jsonify(agent_data)


def update_agent_stats(agent_id: str, agent_name: str, contribution_type: str):
    """Update agent contribution statistics"""
    agent_file = f"{AGENTS_DIR}/{agent_id}.json"
    
    if os.path.exists(agent_file):
        agent_data = load_json(agent_file)
    else:
        agent_data = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "joined_at": datetime.now().isoformat(),
            "contributions": {
                "discoveries": 0,
                "updates": 0,
                "experiences": 0,
                "total": 0
            },
            "rewards": {
                "points": 0,
                "api_credits": 0
            },
            "reputation": 100
        }
    
    # Update contribution counts
    if contribution_type == "discovery":
        agent_data['contributions']['discoveries'] += 1
        agent_data['rewards']['points'] += 10
        agent_data['rewards']['api_credits'] += 50
    elif contribution_type == "update":
        agent_data['contributions']['updates'] += 1
        agent_data['rewards']['points'] += 5
        agent_data['rewards']['api_credits'] += 25
    elif contribution_type == "experience":
        agent_data['contributions']['experiences'] += 1
        agent_data['rewards']['points'] += 8
        agent_data['rewards']['api_credits'] += 40
    
    agent_data['contributions']['total'] += 1
    agent_data['last_contribution'] = datetime.now().isoformat()
    
    # Save updated stats
    save_json(agent_file, agent_data)


@app.route('/api/stats', methods=['GET'])
def get_platform_stats():
    """Get overall platform statistics"""
    
    # Count tools
    tool_count = len([f for f in os.listdir(TOOLS_DIR) if f.endswith('.json')])
    
    # Count contributions
    contribution_count = len([f for f in os.listdir(CONTRIBUTIONS_DIR) if f.endswith('.json')])
    
    # Count agents
    agent_count = len([f for f in os.listdir(AGENTS_DIR) if f.endswith('.json')])
    
    # Calculate total stars
    total_stars = 0
    for filename in os.listdir(TOOLS_DIR):
        if filename.endswith('.json'):
            tool_data = load_json(f"{TOOLS_DIR}/{filename}")
            total_stars += tool_data.get('stars', 0)
    
    return jsonify({
        "total_tools": tool_count,
        "total_contributions": contribution_count,
        "total_agents": agent_count,
        "total_stars": total_stars,
        "last_updated": datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("🚀 AI Tool Search Engine API")
    print("📡 Starting server...")
    print("💡 AI agents can contribute at: /api/contribute/*")
    print("🔍 Search endpoint: /api/search")
    app.run(debug=True, host='0.0.0.0', port=5000)

# For Vercel serverless deployment
# The app object is imported by api/index.py
