"""
GitHub Knowledge Extractor
Automatically extracts high-quality information from GitHub repos
Parses READMEs, docs, and code to build comprehensive tool profiles
"""

import requests
import re
import json
from typing import Dict, List, Optional
from datetime import datetime
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GitHubKnowledgeExtractor:
    """
    Extracts structured knowledge from GitHub repositories
    Uses GitHub token for higher rate limits (5000/hour vs 60/hour)
    """
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.raw_url = "https://raw.githubusercontent.com"
        self.session = requests.Session()
        
        # Get GitHub token from environment
        github_token = os.getenv('GITHUB_TOKEN')
        
        headers = {
            'User-Agent': 'AI-Tool-Search-Engine/1.0',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Add token if available
        if github_token:
            headers['Authorization'] = f'token {github_token}'
            print("✅ Using GitHub token - 5000 requests/hour")
        else:
            print("⚠️  No GitHub token - limited to 60 requests/hour")
        
        self.session.headers.update(headers)
    
    def extract_repo_knowledge(self, github_url: str) -> Dict:
        """
        Main method: Extract all knowledge from a GitHub repo
        
        Args:
            github_url: Full GitHub URL (e.g., https://github.com/user/repo)
        
        Returns:
            Comprehensive tool profile with extracted knowledge
        """
        print(f"🔍 Extracting knowledge from: {github_url}")
        
        # Parse GitHub URL
        owner, repo = self._parse_github_url(github_url)
        if not owner or not repo:
            return {"error": "Invalid GitHub URL"}
        
        # Extract all knowledge components
        knowledge = {
            "basic_info": self._get_basic_info(owner, repo),
            "readme_analysis": self._analyze_readme(owner, repo),
            "documentation": self._extract_documentation(owner, repo),
            "code_analysis": self._analyze_code_structure(owner, repo),
            "community_metrics": self._get_community_metrics(owner, repo),
            "usage_examples": self._extract_usage_examples(owner, repo),
            "dependencies": self._extract_dependencies(owner, repo),
            "extracted_at": datetime.now().isoformat()
        }
        
        # Generate structured profile
        profile = self._generate_tool_profile(knowledge)
        
        return profile
    
    def _parse_github_url(self, url: str) -> tuple:
        """Extract owner and repo from GitHub URL"""
        pattern = r'github\.com/([^/]+)/([^/]+)'
        match = re.search(pattern, url)
        if match:
            return match.group(1), match.group(2).replace('.git', '')
        return None, None
    
    def _get_basic_info(self, owner: str, repo: str) -> Dict:
        """Get basic repository information"""
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data.get("name"),
                    "full_name": data.get("full_name"),
                    "description": data.get("description"),
                    "stars": data.get("stargazers_count"),
                    "forks": data.get("forks_count"),
                    "watchers": data.get("watchers_count"),
                    "language": data.get("language"),
                    "license": data.get("license", {}).get("name") if data.get("license") else None,
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "homepage": data.get("homepage"),
                    "topics": data.get("topics", []),
                    "open_issues": data.get("open_issues_count"),
                    "default_branch": data.get("default_branch", "main")
                }
            else:
                print(f"⚠️  Rate limit or error: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Error getting basic info: {e}")
            return {}
    
    def _analyze_readme(self, owner: str, repo: str) -> Dict:
        """
        Intelligently parse README to extract key information
        """
        readme_content = self._get_readme_content(owner, repo)
        
        if not readme_content:
            return {"error": "No README found"}
        
        analysis = {
            "raw_content": readme_content[:5000],  # First 5000 chars
            "sections": self._extract_sections(readme_content),
            "installation": self._extract_installation(readme_content),
            "usage": self._extract_usage(readme_content),
            "features": self._extract_features(readme_content),
            "requirements": self._extract_requirements(readme_content),
            "examples": self._extract_code_examples(readme_content),
            "links": self._extract_links(readme_content),
            "badges": self._extract_badges(readme_content)
        }
        
        return analysis
    
    def _get_readme_content(self, owner: str, repo: str) -> Optional[str]:
        """Fetch README content from repository"""
        readme_files = ['README.md', 'README.MD', 'readme.md', 'README', 'README.rst']
        
        for readme_file in readme_files:
            try:
                url = f"{self.raw_url}/{owner}/{repo}/main/{readme_file}"
                response = self.session.get(url)
                
                if response.status_code == 200:
                    return response.text
                
                # Try master branch if main doesn't work
                url = f"{self.raw_url}/{owner}/{repo}/master/{readme_file}"
                response = self.session.get(url)
                
                if response.status_code == 200:
                    return response.text
            except:
                continue
        
        return None
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract markdown sections from README"""
        sections = {}
        
        # Find all headers and their content
        lines = content.split('\n')
        current_section = "introduction"
        current_content = []
        
        for line in lines:
            if line.startswith('#'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.lstrip('#').strip().lower().replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _extract_installation(self, content: str) -> List[str]:
        """Extract installation commands"""
        installation_commands = []
        
        # Look for common installation patterns
        patterns = [
            r'pip install ([^\s\n]+)',
            r'npm install ([^\s\n]+)',
            r'yarn add ([^\s\n]+)',
            r'go get ([^\s\n]+)',
            r'cargo install ([^\s\n]+)',
            r'gem install ([^\s\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            installation_commands.extend(matches)
        
        # Also extract code blocks in installation sections
        install_section = re.search(r'##\s*Install.*?\n(.*?)(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if install_section:
            code_blocks = re.findall(r'```(?:bash|shell|sh)?\n(.*?)```', install_section.group(1), re.DOTALL)
            installation_commands.extend([block.strip() for block in code_blocks])
        
        return list(set(installation_commands))  # Remove duplicates
    
    def _extract_usage(self, content: str) -> List[str]:
        """Extract usage examples"""
        usage_examples = []
        
        # Find usage/quickstart sections
        usage_section = re.search(r'##\s*(Usage|Quick\s*Start|Getting\s*Started).*?\n(.*?)(?=##|\Z)', 
                                 content, re.DOTALL | re.IGNORECASE)
        
        if usage_section:
            # Extract code blocks
            code_blocks = re.findall(r'```(?:python|javascript|js|typescript|ts|bash|shell)?\n(.*?)```', 
                                    usage_section.group(2), re.DOTALL)
            usage_examples.extend([block.strip() for block in code_blocks])
        
        return usage_examples
    
    def _extract_features(self, content: str) -> List[str]:
        """Extract feature list"""
        features = []
        
        # Look for features section
        features_section = re.search(r'##\s*Features.*?\n(.*?)(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
        
        if features_section:
            # Extract bullet points
            bullets = re.findall(r'[-*]\s+(.+)', features_section.group(1))
            features.extend([bullet.strip() for bullet in bullets])
        
        return features
    
    def _extract_requirements(self, content: str) -> Dict:
        """Extract requirements and dependencies"""
        requirements = {
            "python_version": None,
            "node_version": None,
            "system_requirements": [],
            "dependencies": []
        }
        
        # Python version
        python_match = re.search(r'Python\s*([0-9.]+)', content, re.IGNORECASE)
        if python_match:
            requirements["python_version"] = python_match.group(1)
        
        # Node version
        node_match = re.search(r'Node\.?js\s*([0-9.]+)', content, re.IGNORECASE)
        if node_match:
            requirements["node_version"] = node_match.group(1)
        
        # System requirements
        req_section = re.search(r'##\s*Requirements.*?\n(.*?)(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if req_section:
            bullets = re.findall(r'[-*]\s+(.+)', req_section.group(1))
            requirements["system_requirements"] = [b.strip() for b in bullets]
        
        return requirements
    
    def _extract_code_examples(self, content: str) -> List[Dict]:
        """Extract all code examples with context"""
        examples = []
        
        # Find all code blocks with language
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            language = match.group(1) or "unknown"
            code = match.group(2).strip()
            
            examples.append({
                "language": language,
                "code": code[:500]  # Limit to 500 chars
            })
        
        return examples
    
    def _extract_links(self, content: str) -> Dict[str, List[str]]:
        """Extract important links"""
        links = {
            "documentation": [],
            "demo": [],
            "tutorial": [],
            "other": []
        }
        
        # Extract markdown links
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        
        for text, url in markdown_links:
            text_lower = text.lower()
            if any(word in text_lower for word in ['doc', 'documentation', 'guide']):
                links["documentation"].append(url)
            elif any(word in text_lower for word in ['demo', 'example', 'playground']):
                links["demo"].append(url)
            elif any(word in text_lower for word in ['tutorial', 'learn', 'course']):
                links["tutorial"].append(url)
            else:
                links["other"].append(url)
        
        return links
    
    def _extract_badges(self, content: str) -> List[str]:
        """Extract badge information (CI/CD, coverage, etc.)"""
        badges = []
        
        # Find badge URLs
        badge_pattern = r'!\[([^\]]*)\]\((https://[^\)]+)\)'
        matches = re.findall(badge_pattern, content)
        
        for alt_text, url in matches:
            badges.append({
                "type": alt_text,
                "url": url
            })
        
        return badges
    
    def _extract_documentation(self, owner: str, repo: str) -> Dict:
        """Check for documentation files"""
        doc_files = ['docs/', 'documentation/', 'DOCUMENTATION.md', 'CONTRIBUTING.md']
        found_docs = []
        
        for doc_file in doc_files:
            try:
                url = f"{self.base_url}/repos/{owner}/{repo}/contents/{doc_file}"
                response = self.session.get(url)
                
                if response.status_code == 200:
                    found_docs.append(doc_file)
            except:
                continue
        
        return {
            "has_docs": len(found_docs) > 0,
            "doc_locations": found_docs
        }
    
    def _analyze_code_structure(self, owner: str, repo: str) -> Dict:
        """Analyze repository structure"""
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/contents"
            response = self.session.get(url)
            
            if response.status_code == 200:
                contents = response.json()
                
                structure = {
                    "has_tests": any('test' in item['name'].lower() for item in contents),
                    "has_examples": any('example' in item['name'].lower() for item in contents),
                    "has_docs": any('doc' in item['name'].lower() for item in contents),
                    "has_ci": any(item['name'] in ['.github', '.gitlab-ci.yml', '.travis.yml'] for item in contents),
                    "file_count": len([item for item in contents if item['type'] == 'file']),
                    "folder_count": len([item for item in contents if item['type'] == 'dir'])
                }
                
                return structure
        except:
            pass
        
        return {}
    
    def _get_community_metrics(self, owner: str, repo: str) -> Dict:
        """Get community engagement metrics"""
        metrics = {
            "contributors": 0,
            "recent_commits": 0,
            "open_prs": 0,
            "closed_prs": 0
        }
        
        try:
            # Get contributors count
            url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
            response = self.session.get(url)
            if response.status_code == 200:
                metrics["contributors"] = len(response.json())
            
            # Get recent commits (last 30 days)
            url = f"{self.base_url}/repos/{owner}/{repo}/commits"
            response = self.session.get(url, params={"per_page": 100})
            if response.status_code == 200:
                commits = response.json()
                metrics["recent_commits"] = len(commits)
            
            time.sleep(0.5)  # Rate limit protection
        except:
            pass
        
        return metrics
    
    def _extract_usage_examples(self, owner: str, repo: str) -> List[str]:
        """Look for example files"""
        example_files = []
        
        try:
            # Check for examples directory
            url = f"{self.base_url}/repos/{owner}/{repo}/contents/examples"
            response = self.session.get(url)
            
            if response.status_code == 200:
                contents = response.json()
                example_files = [item['name'] for item in contents if item['type'] == 'file']
        except:
            pass
        
        return example_files
    
    def _extract_dependencies(self, owner: str, repo: str) -> Dict:
        """Extract dependencies from package files"""
        dependencies = {
            "python": [],
            "javascript": [],
            "other": []
        }
        
        # Check for requirements.txt (Python)
        try:
            url = f"{self.raw_url}/{owner}/{repo}/main/requirements.txt"
            response = self.session.get(url)
            if response.status_code == 200:
                deps = [line.split('==')[0].split('>=')[0].strip() 
                       for line in response.text.split('\n') 
                       if line.strip() and not line.startswith('#')]
                dependencies["python"] = deps[:20]  # Limit to 20
        except:
            pass
        
        # Check for package.json (JavaScript)
        try:
            url = f"{self.raw_url}/{owner}/{repo}/main/package.json"
            response = self.session.get(url)
            if response.status_code == 200:
                package_data = json.loads(response.text)
                deps = list(package_data.get('dependencies', {}).keys())
                dependencies["javascript"] = deps[:20]  # Limit to 20
        except:
            pass
        
        return dependencies
    
    def _generate_tool_profile(self, knowledge: Dict) -> Dict:
        """
        Generate a comprehensive, structured tool profile
        from extracted knowledge
        """
        basic = knowledge.get("basic_info", {})
        readme = knowledge.get("readme_analysis", {})
        
        profile = {
            # Core Identity
            "name": basic.get("name"),
            "full_name": basic.get("full_name"),
            "tagline": basic.get("description"),
            "category": self._infer_category(basic, readme),
            
            # Detailed Description
            "description": self._generate_description(readme),
            "features": readme.get("features", []),
            "use_cases": self._infer_use_cases(basic, readme),
            
            # Technical Details
            "language": basic.get("language"),
            "license": basic.get("license"),
            "installation": readme.get("installation", []),
            "requirements": readme.get("requirements", {}),
            "dependencies": knowledge.get("dependencies", {}),
            
            # Quality Indicators
            "stars": basic.get("stars"),
            "forks": basic.get("forks"),
            "contributors": knowledge.get("community_metrics", {}).get("contributors"),
            "last_updated": basic.get("updated_at"),
            "has_tests": knowledge.get("code_analysis", {}).get("has_tests"),
            "has_docs": knowledge.get("documentation", {}).get("has_docs"),
            "has_ci": knowledge.get("code_analysis", {}).get("has_ci"),
            
            # Resources
            "github_url": f"https://github.com/{basic.get('full_name')}",
            "homepage": basic.get("homepage"),
            "documentation_links": readme.get("links", {}).get("documentation", []),
            "demo_links": readme.get("links", {}).get("demo", []),
            
            # Examples
            "usage_examples": readme.get("usage", []),
            "code_examples": readme.get("examples", []),
            
            # Metadata
            "topics": basic.get("topics", []),
            "created_at": basic.get("created_at"),
            "extracted_at": knowledge.get("extracted_at"),
            
            # Search Optimization
            "keywords": self._generate_keywords(basic, readme),
            "search_text": self._generate_search_text(basic, readme)
        }
        
        return profile
    
    def _infer_category(self, basic: Dict, readme: Dict) -> str:
        """Infer tool category from available information"""
        text = f"{basic.get('description', '')} {basic.get('topics', [])}".lower()
        
        categories = {
            "chatbot": ["chatbot", "chat", "conversation", "dialogue"],
            "llm_framework": ["llm", "language model", "gpt", "transformer"],
            "agent": ["agent", "autonomous", "multi-agent"],
            "rag": ["rag", "retrieval", "vector", "embedding"],
            "automation": ["automation", "workflow", "orchestration"],
            "data_processing": ["data", "processing", "etl", "pipeline"],
            "computer_vision": ["vision", "image", "detection", "opencv"],
            "nlp": ["nlp", "natural language", "text processing"],
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return "other"
    
    def _generate_description(self, readme: Dict) -> str:
        """Generate a clean description from README"""
        sections = readme.get("sections", {})
        
        # Try to get introduction or first section
        intro = sections.get("introduction", "")
        if not intro and sections:
            intro = list(sections.values())[0]
        
        # Clean and truncate
        description = intro.replace('\n', ' ').strip()
        if len(description) > 500:
            description = description[:497] + "..."
        
        return description
    
    def _infer_use_cases(self, basic: Dict, readme: Dict) -> List[str]:
        """Infer use cases from description and features"""
        use_cases = []
        
        text = f"{basic.get('description', '')} {readme.get('features', [])}".lower()
        
        use_case_keywords = {
            "customer_support": ["customer support", "helpdesk", "support bot"],
            "document_qa": ["document", "qa", "question answering", "pdf"],
            "code_generation": ["code generation", "coding", "programming"],
            "data_analysis": ["data analysis", "analytics", "insights"],
            "content_creation": ["content", "writing", "generation"],
            "research": ["research", "information", "knowledge"],
        }
        
        for use_case, keywords in use_case_keywords.items():
            if any(keyword in text for keyword in keywords):
                use_cases.append(use_case)
        
        return use_cases
    
    def _generate_keywords(self, basic: Dict, readme: Dict) -> List[str]:
        """Generate searchable keywords"""
        keywords = set()
        
        # Add topics
        keywords.update(basic.get("topics", []))
        
        # Add language
        if basic.get("language"):
            keywords.add(basic.get("language").lower())
        
        # Extract from description
        desc = basic.get("description", "").lower()
        important_words = re.findall(r'\b[a-z]{4,}\b', desc)
        keywords.update(important_words[:10])
        
        return list(keywords)
    
    def _generate_search_text(self, basic: Dict, readme: Dict) -> str:
        """Generate full-text search content"""
        parts = [
            basic.get("name", ""),
            basic.get("description", ""),
            " ".join(basic.get("topics", [])),
            " ".join(readme.get("features", [])),
            readme.get("sections", {}).get("introduction", "")
        ]
        
        return " ".join(parts).lower()


# Example usage
if __name__ == "__main__":
    extractor = GitHubKnowledgeExtractor()
    
    # Test with popular AI tools
    test_repos = [
        "https://github.com/langchain-ai/langchain",
        "https://github.com/Significant-Gravitas/AutoGPT",
        "https://github.com/joaomdmoura/crewAI"
    ]
    
    for repo_url in test_repos:
        print(f"\n{'='*60}")
        profile = extractor.extract_repo_knowledge(repo_url)
        
        print(f"\n📦 Tool: {profile.get('name')}")
        print(f"📝 Description: {profile.get('tagline')}")
        print(f"⭐ Stars: {profile.get('stars')}")
        print(f"🏷️  Category: {profile.get('category')}")
        print(f"💻 Language: {profile.get('language')}")
        print(f"📚 Features: {len(profile.get('features', []))}")
        print(f"🔗 Has Docs: {profile.get('has_docs')}")
        
        # Save to JSON
        filename = f"data/tools/{profile.get('name', 'unknown').lower()}.json"
        print(f"\n💾 Saving to: {filename}")
        
        time.sleep(1)  # Rate limit protection
