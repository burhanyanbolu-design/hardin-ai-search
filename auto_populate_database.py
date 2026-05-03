"""
Automated Database Population Bot
Discovers and adds AI tools from GitHub automatically
Run once to seed database, then daily for updates
"""

import requests
import json
import time
import os
from datetime import datetime
from github_knowledge_extractor import GitHubKnowledgeExtractor

class DatabasePopulationBot:
    """
    Automatically discovers and adds AI tools to database
    No manual work needed!
    """
    
    def __init__(self):
        self.extractor = GitHubKnowledgeExtractor()
        self.tools_dir = "data/tools"
        self.github_api = "https://api.github.com"
        
        # Create directory if doesn't exist
        os.makedirs(self.tools_dir, exist_ok=True)
        
        # Search queries for finding AI tools
        self.search_queries = [
            # LLM & Chatbots
            "llm framework language:python stars:>100",
            "chatbot framework language:python stars:>100",
            "gpt wrapper language:python stars:>100",
            "openai api language:python stars:>100",
            
            # Agents
            "autonomous agent language:python stars:>100",
            "ai agent framework stars:>100",
            "multi agent system stars:>100",
            
            # RAG & Vector DBs
            "rag retrieval augmented generation stars:>100",
            "vector database language:python stars:>100",
            "embedding search stars:>100",
            
            # Tools & Frameworks
            "langchain stars:>100",
            "llama index stars:>100",
            "semantic kernel stars:>100",
            
            # Automation
            "ai automation language:python stars:>100",
            "workflow automation ai stars:>100",
            
            # Computer Vision
            "computer vision ai language:python stars:>100",
            "object detection language:python stars:>100",
            
            # NLP
            "natural language processing language:python stars:>100",
            "text generation language:python stars:>100"
        ]
    
    def search_github_repos(self, query, max_results=10):
        """Search GitHub for repos matching query"""
        print(f"\n🔍 Searching: {query}")
        
        url = f"{self.github_api}/search/repositories"
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': max_results
        }
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                repos = data.get('items', [])
                print(f"   Found {len(repos)} repositories")
                return repos
            elif response.status_code == 403:
                print("   ⚠️  Rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
                return []
            else:
                print(f"   ❌ Error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    def is_tool_already_added(self, repo_name):
        """Check if tool already exists in database"""
        tool_filename = f"{repo_name.lower().replace('/', '-').replace(' ', '-')}.json"
        return os.path.exists(f"{self.tools_dir}/{tool_filename}")
    
    def add_tool_to_database(self, repo):
        """Extract knowledge and add tool to database"""
        repo_full_name = repo.get('full_name')
        repo_url = repo.get('html_url')
        
        # Check if already added
        if self.is_tool_already_added(repo_full_name):
            print(f"   ⏭️  Already exists: {repo_full_name}")
            return False
        
        print(f"\n📦 Processing: {repo_full_name}")
        print(f"   ⭐ Stars: {repo.get('stargazers_count', 0):,}")
        print(f"   📝 {repo.get('description', 'No description')[:80]}...")
        
        try:
            # Extract knowledge from GitHub
            profile = self.extractor.extract_repo_knowledge(repo_url)
            
            if 'error' in profile:
                print(f"   ❌ Error extracting: {profile['error']}")
                return False
            
            # Save to database
            tool_name = repo_full_name.lower().replace('/', '-').replace(' ', '-')
            filename = f"{self.tools_dir}/{tool_name}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Added: {profile.get('name')}")
            print(f"   💾 Saved to: {filename}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def populate_database(self, tools_per_query=10, delay_between_queries=5):
        """
        Main method: Populate database with AI tools
        
        Args:
            tools_per_query: How many tools to fetch per search query
            delay_between_queries: Seconds to wait between queries (rate limit protection)
        """
        print("\n" + "="*60)
        print("🤖 AUTOMATED DATABASE POPULATION BOT")
        print("="*60)
        print(f"\n📊 Configuration:")
        print(f"   Search queries: {len(self.search_queries)}")
        print(f"   Tools per query: {tools_per_query}")
        print(f"   Delay between queries: {delay_between_queries}s")
        print(f"\n🎯 Estimated tools to discover: {len(self.search_queries) * tools_per_query}")
        print(f"⏱️  Estimated time: {(len(self.search_queries) * delay_between_queries) / 60:.1f} minutes")
        
        input("\n⏸️  Press Enter to start...")
        
        total_added = 0
        total_skipped = 0
        start_time = time.time()
        
        for i, query in enumerate(self.search_queries, 1):
            print(f"\n{'='*60}")
            print(f"Query {i}/{len(self.search_queries)}")
            print(f"{'='*60}")
            
            # Search GitHub
            repos = self.search_github_repos(query, max_results=tools_per_query)
            
            # Process each repo
            for repo in repos:
                if self.add_tool_to_database(repo):
                    total_added += 1
                else:
                    total_skipped += 1
                
                # Small delay to avoid rate limits
                time.sleep(2)
            
            # Delay between queries
            if i < len(self.search_queries):
                print(f"\n⏳ Waiting {delay_between_queries}s before next query...")
                time.sleep(delay_between_queries)
        
        # Summary
        elapsed_time = time.time() - start_time
        
        print("\n" + "="*60)
        print("📊 POPULATION COMPLETE!")
        print("="*60)
        print(f"\n✅ Tools added: {total_added}")
        print(f"⏭️  Tools skipped (already exist): {total_skipped}")
        print(f"⏱️  Time taken: {elapsed_time/60:.1f} minutes")
        print(f"💾 Database location: {self.tools_dir}/")
        
        # List all tools
        all_tools = [f for f in os.listdir(self.tools_dir) if f.endswith('.json')]
        print(f"\n📦 Total tools in database: {len(all_tools)}")
        
        return total_added
    
    def update_existing_tools(self):
        """Update information for existing tools"""
        print("\n" + "="*60)
        print("🔄 UPDATING EXISTING TOOLS")
        print("="*60)
        
        all_tools = [f for f in os.listdir(self.tools_dir) if f.endswith('.json')]
        print(f"\n📦 Found {len(all_tools)} tools to update")
        
        updated = 0
        
        for i, filename in enumerate(all_tools, 1):
            print(f"\n[{i}/{len(all_tools)}] Updating {filename}...")
            
            try:
                # Load existing tool
                with open(f"{self.tools_dir}/{filename}", 'r', encoding='utf-8') as f:
                    tool_data = json.load(f)
                
                github_url = tool_data.get('github_url')
                if not github_url:
                    print("   ⏭️  No GitHub URL, skipping")
                    continue
                
                # Re-extract knowledge
                profile = self.extractor.extract_repo_knowledge(github_url)
                
                if 'error' not in profile:
                    # Preserve contribution history
                    if 'contribution' in tool_data:
                        profile['contribution'] = tool_data['contribution']
                    if 'experiences' in tool_data:
                        profile['experiences'] = tool_data['experiences']
                    
                    # Save updated profile
                    with open(f"{self.tools_dir}/{filename}", 'w', encoding='utf-8') as f:
                        json.dump(profile, f, indent=2, ensure_ascii=False)
                    
                    print(f"   ✅ Updated: {profile.get('name')}")
                    updated += 1
                else:
                    print(f"   ❌ Error: {profile['error']}")
                
                time.sleep(3)  # Rate limit protection
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n✅ Updated {updated} tools")
        return updated
    
    def discover_trending_tools(self):
        """Find trending AI tools from GitHub"""
        print("\n" + "="*60)
        print("🔥 DISCOVERING TRENDING TOOLS")
        print("="*60)
        
        # Search for recently created popular repos
        queries = [
            "ai created:>2024-01-01 stars:>500",
            "llm created:>2024-01-01 stars:>500",
            "gpt created:>2024-01-01 stars:>500",
            "agent created:>2024-01-01 stars:>500"
        ]
        
        trending_tools = []
        
        for query in queries:
            repos = self.search_github_repos(query, max_results=5)
            
            for repo in repos:
                if not self.is_tool_already_added(repo.get('full_name')):
                    trending_tools.append(repo)
            
            time.sleep(5)
        
        print(f"\n🔥 Found {len(trending_tools)} trending tools")
        
        # Add them
        added = 0
        for repo in trending_tools:
            if self.add_tool_to_database(repo):
                added += 1
            time.sleep(3)
        
        print(f"\n✅ Added {added} trending tools")
        return added


def main():
    """Main entry point"""
    bot = DatabasePopulationBot()
    
    print("\n" + "="*60)
    print("🤖 AI TOOL DATABASE POPULATION BOT")
    print("="*60)
    print("\nWhat would you like to do?")
    print("\n1. 🌱 Seed Database (First time - add 100+ tools)")
    print("2. 🔄 Update Existing Tools (Refresh data)")
    print("3. 🔥 Discover Trending Tools (Find new popular tools)")
    print("4. 🚀 Full Run (Seed + Trending)")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        # Seed database
        bot.populate_database(tools_per_query=10, delay_between_queries=5)
        
    elif choice == '2':
        # Update existing
        bot.update_existing_tools()
        
    elif choice == '3':
        # Find trending
        bot.discover_trending_tools()
        
    elif choice == '4':
        # Full run
        print("\n🚀 Running full population...")
        added = bot.populate_database(tools_per_query=10, delay_between_queries=5)
        
        if added > 0:
            print("\n🔥 Now discovering trending tools...")
            time.sleep(10)
            bot.discover_trending_tools()
    
    else:
        print("❌ Invalid choice")
        return
    
    print("\n" + "="*60)
    print("✅ DONE!")
    print("="*60)
    print("\n📋 Next steps:")
    print("   1. Check data/tools/ directory")
    print("   2. Start API server: python api_contribution.py")
    print("   3. Open index.html in browser")
    print("   4. Deploy to production!")
    print("\n💡 Tip: Run this bot daily to keep database fresh")


if __name__ == "__main__":
    main()
