"""
Bot News Agent System
Bots stay active 24/7 monitoring for new AI tools
Like news agents watching for breaking stories
Automatically register new tools when they pass tests
"""

import time
import threading
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import requests
from bot_army import (
    BotArmyManager, ScoutBot, ExtractorBot, 
    ValidatorBot, WriterBot, MonitorBot
)


class NewsAgentBot:
    """
    News Agent Bot - Stays active monitoring for new tools
    Like a journalist watching for breaking news
    """
    
    def __init__(self, region: str):
        self.region = region  # e.g., "llm", "chatbot", "agent"
        self.is_active = True
        self.last_check = datetime.now()
        self.check_interval = 3600  # Check every hour
        self.discovered_tools = []
        
        # Region-specific keywords
        self.region_keywords = {
            'llm': ['llm', 'language model', 'gpt', 'transformer', 'llama', 'mistral'],
            'chatbot': ['chatbot', 'conversational ai', 'chat assistant', 'dialogue system'],
            'agent': ['autonomous agent', 'ai agent', 'multi-agent', 'agent framework'],
            'rag': ['rag', 'retrieval augmented', 'vector database', 'embedding', 'semantic search'],
            'automation': ['ai automation', 'workflow automation', 'orchestration', 'ai pipeline'],
            'vision': ['computer vision', 'image recognition', 'object detection', 'yolo', 'opencv'],
            'nlp': ['nlp', 'natural language processing', 'text analysis', 'sentiment'],
            'ml_ops': ['mlops', 'ml pipeline', 'model deployment', 'ml monitoring']
        }
        
        self.keywords = self.region_keywords.get(region, [])
        
    def log(self, message: str):
        """Log activity"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 📰 NewsAgent-{self.region}: {message}")
    
    def monitor(self):
        """Continuously monitor for new tools"""
        self.log(f"Starting monitoring for region: {self.region}")
        
        while self.is_active:
            try:
                # Check if it's time to scan
                if datetime.now() - self.last_check >= timedelta(seconds=self.check_interval):
                    self.log("🔍 Scanning for new tools...")
                    
                    # Search GitHub
                    new_tools = self._search_github()
                    
                    if new_tools:
                        self.log(f"📢 BREAKING: Found {len(new_tools)} new tools!")
                        
                        # Process each new tool
                        for tool in new_tools:
                            self._process_new_tool(tool)
                    else:
                        self.log("No new tools found")
                    
                    self.last_check = datetime.now()
                
                # Sleep for a bit
                time.sleep(60)  # Check every minute if it's time to scan
                
            except Exception as e:
                self.log(f"Error in monitoring: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _search_github(self) -> List[Dict]:
        """Search GitHub for new tools in this region"""
        new_tools = []
        
        for keyword in self.keywords[:3]:  # Limit to 3 keywords per scan
            try:
                # Search for recently created repos
                query = f"{keyword} created:>{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} stars:>50"
                
                url = "https://api.github.com/search/repositories"
                params = {
                    'q': query,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': 5
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    repos = data.get('items', [])
                    
                    for repo in repos:
                        # Check if we've seen this before
                        if not self._is_already_discovered(repo['html_url']):
                            new_tools.append({
                                'url': repo['html_url'],
                                'name': repo['full_name'],
                                'stars': repo['stargazers_count'],
                                'description': repo['description'],
                                'region': self.region,
                                'keyword': keyword
                            })
                
                time.sleep(3)  # Rate limit protection
                
            except Exception as e:
                self.log(f"Error searching for '{keyword}': {e}")
        
        return new_tools
    
    def _is_already_discovered(self, url: str) -> bool:
        """Check if tool was already discovered"""
        # Check in discovered list
        if any(tool['url'] == url for tool in self.discovered_tools):
            return True
        
        # Check in database
        tools_dir = "data/tools"
        if os.path.exists(tools_dir):
            for filename in os.listdir(tools_dir):
                if filename.endswith('.json'):
                    try:
                        with open(f"{tools_dir}/{filename}", 'r', encoding='utf-8') as f:
                            tool_data = json.load(f)
                            if tool_data.get('github_url') == url:
                                return True
                    except:
                        pass
        
        return False
    
    def _process_new_tool(self, tool: Dict):
        """Process a newly discovered tool"""
        self.log(f"Processing: {tool['name']}")
        
        # Add to discovered list
        self.discovered_tools.append(tool)
        
        # Trigger the bot army to process this tool
        # (This would integrate with the main bot army system)
        self.log(f"✅ Queued for processing: {tool['name']}")


class NewsAgentNetwork:
    """
    Network of News Agent Bots
    Each bot monitors a specific region
    Work together to cover all AI tool categories
    """
    
    def __init__(self):
        self.agents = {}
        self.bot_army = BotArmyManager()
        self.is_running = False
        
    def deploy_agents(self):
        """Deploy news agents to all regions"""
        print("\n" + "="*60)
        print("📰 DEPLOYING NEWS AGENT NETWORK")
        print("="*60)
        
        regions = ['llm', 'chatbot', 'agent', 'rag', 'automation', 'vision', 'nlp', 'ml_ops']
        
        for region in regions:
            agent = NewsAgentBot(region)
            self.agents[region] = agent
            print(f"✅ Deployed agent to region: {region}")
        
        print(f"\n🎉 Network deployed: {len(self.agents)} agents active")
    
    def start_network(self):
        """Start all news agents"""
        print("\n" + "="*60)
        print("🚀 STARTING NEWS AGENT NETWORK")
        print("="*60)
        
        self.is_running = True
        threads = []
        
        # Start each agent in its own thread
        for region, agent in self.agents.items():
            thread = threading.Thread(
                target=agent.monitor,
                daemon=True
            )
            thread.start()
            threads.append(thread)
            print(f"✅ Started agent: {region}")
        
        # Start bot army for processing
        print("\n🤖 Starting bot army for processing...")
        self.bot_army.create_initial_army()
        self.bot_army.start_army()
        
        print(f"\n🎉 Network is live! {len(threads)} agents monitoring 24/7")
        
        return threads
    
    def process_discovered_tools(self):
        """Process tools discovered by news agents"""
        while self.is_running:
            try:
                # Collect all discovered tools from agents
                all_discovered = []
                for agent in self.agents.values():
                    all_discovered.extend(agent.discovered_tools)
                
                # Process new tools
                for tool in all_discovered:
                    # Extract knowledge
                    self.bot_army.assign_task('extractor', {'repo_url': tool['url']})
                
                # Wait a bit
                time.sleep(300)  # Process every 5 minutes
                
            except Exception as e:
                print(f"Error processing discovered tools: {e}")
                time.sleep(60)
    
    def get_network_stats(self):
        """Get statistics from the network"""
        stats = {
            'total_agents': len(self.agents),
            'agents_active': sum(1 for agent in self.agents.values() if agent.is_active),
            'total_discovered': sum(len(agent.discovered_tools) for agent in self.agents.values()),
            'by_region': {}
        }
        
        for region, agent in self.agents.items():
            stats['by_region'][region] = {
                'discovered': len(agent.discovered_tools),
                'last_check': agent.last_check.strftime('%Y-%m-%d %H:%M:%S'),
                'active': agent.is_active
            }
        
        return stats
    
    def print_stats(self):
        """Print network statistics"""
        stats = self.get_network_stats()
        
        print("\n" + "="*60)
        print("📊 NEWS AGENT NETWORK STATISTICS")
        print("="*60)
        print(f"\n📰 Total Agents: {stats['total_agents']}")
        print(f"✅ Active Agents: {stats['agents_active']}")
        print(f"🔍 Total Discovered: {stats['total_discovered']}")
        
        print("\nBy Region:")
        for region, data in stats['by_region'].items():
            print(f"\n  {region.upper()}:")
            print(f"    Discovered: {data['discovered']}")
            print(f"    Last Check: {data['last_check']}")
            print(f"    Status: {'🟢 Active' if data['active'] else '🔴 Inactive'}")
    
    def stop_network(self):
        """Stop all agents"""
        print("\n⏹️  Stopping news agent network...")
        self.is_running = False
        
        for agent in self.agents.values():
            agent.is_active = False
        
        self.bot_army.stop_army()
        
        time.sleep(2)
        print("✅ Network stopped")


def run_news_agent_network():
    """Run the news agent network"""
    print("\n" + "="*60)
    print("📰 NEWS AGENT NETWORK - 24/7 MONITORING")
    print("="*60)
    print("\nThis system will:")
    print("  1. Deploy agents to all AI tool regions")
    print("  2. Monitor GitHub 24/7 for new tools")
    print("  3. Automatically process and validate")
    print("  4. Add to database if passes tests")
    print("\n⏰ Agents check every hour")
    print("🤖 Bot army processes discoveries")
    print("💾 Auto-saves to database")
    
    input("\n⏸️  Press Enter to start network...")
    
    # Create network
    network = NewsAgentNetwork()
    
    # Deploy agents
    network.deploy_agents()
    
    # Start network
    threads = network.start_network()
    
    # Start processing thread
    process_thread = threading.Thread(
        target=network.process_discovered_tools,
        daemon=True
    )
    process_thread.start()
    
    print("\n" + "="*60)
    print("✅ NETWORK IS LIVE!")
    print("="*60)
    print("\n📰 News agents are monitoring...")
    print("🤖 Bot army is ready to process...")
    print("💾 Database will auto-update...")
    print("\nPress Ctrl+C to stop")
    
    try:
        # Keep running and print stats every 10 minutes
        while True:
            time.sleep(600)  # 10 minutes
            network.print_stats()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping network...")
        network.stop_network()
        print("✅ Network stopped successfully")


if __name__ == "__main__":
    run_news_agent_network()
