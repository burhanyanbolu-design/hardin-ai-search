"""
Self-Replicating Bot Army System
Each bot specializes in a specific task
Bots clone themselves when busy
Work together like a swarm intelligence
"""

import threading
import queue
import time
import json
import os
from datetime import datetime
from typing import List, Dict
import requests
from github_knowledge_extractor import GitHubKnowledgeExtractor

# ============================================================================
# BOT ARMY CONFIGURATION
# ============================================================================

BOT_ARMY_CONFIG = {
    "initial_army_size": 10,  # Start with 10 bots
    "max_bots_per_type": 20,  # Max 20 bots of each type
    "clone_threshold": 5,  # Clone when queue has 5+ tasks
    "task_timeout": 300,  # 5 minutes per task
    "rest_time": 2,  # Seconds between tasks
}

# ============================================================================
# SPECIALIZED BOT TYPES
# ============================================================================

class BaseBot:
    """Base class for all bots"""
    
    def __init__(self, bot_id: str, bot_type: str):
        self.bot_id = bot_id
        self.bot_type = bot_type
        self.status = "idle"
        self.tasks_completed = 0
        self.created_at = datetime.now()
        self.is_alive = True
        
    def log(self, message: str):
        """Log bot activity"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🤖 {self.bot_type}-{self.bot_id}: {message}")
    
    def work(self, task: Dict):
        """Override in subclass"""
        raise NotImplementedError


class ScoutBot(BaseBot):
    """
    Scout Bot: Searches GitHub for new AI tools
    Specialization: Discovery and reconnaissance
    """
    
    def __init__(self, bot_id: str):
        super().__init__(bot_id, "Scout")
        self.github_api = "https://api.github.com"
        
    def work(self, task: Dict):
        """Search GitHub for tools matching keywords"""
        self.status = "working"
        keywords = task.get("keywords", [])
        
        self.log(f"Scouting for: {', '.join(keywords)}")
        
        discovered_repos = []
        
        for keyword in keywords:
            query = f"{keyword} language:python stars:>100"
            
            try:
                url = f"{self.github_api}/search/repositories"
                params = {
                    'q': query,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': 10
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    repos = data.get('items', [])
                    
                    for repo in repos:
                        discovered_repos.append({
                            'url': repo.get('html_url'),
                            'name': repo.get('full_name'),
                            'stars': repo.get('stargazers_count'),
                            'description': repo.get('description'),
                            'discovered_by': self.bot_id,
                            'keyword': keyword
                        })
                    
                    self.log(f"Found {len(repos)} repos for '{keyword}'")
                
                time.sleep(2)  # Rate limit protection
                
            except Exception as e:
                self.log(f"Error scouting '{keyword}': {e}")
        
        self.tasks_completed += 1
        self.status = "idle"
        
        return {
            'success': True,
            'discovered': discovered_repos,
            'count': len(discovered_repos)
        }


class ExtractorBot(BaseBot):
    """
    Extractor Bot: Extracts knowledge from GitHub repos
    Specialization: README parsing and data extraction
    """
    
    def __init__(self, bot_id: str):
        super().__init__(bot_id, "Extractor")
        self.extractor = GitHubKnowledgeExtractor()
        
    def work(self, task: Dict):
        """Extract knowledge from a GitHub repo"""
        self.status = "working"
        repo_url = task.get('repo_url')
        
        self.log(f"Extracting from: {repo_url}")
        
        try:
            profile = self.extractor.extract_repo_knowledge(repo_url)
            
            if 'error' not in profile:
                self.log(f"✅ Extracted: {profile.get('name')}")
                self.tasks_completed += 1
                self.status = "idle"
                
                return {
                    'success': True,
                    'profile': profile,
                    'repo_url': repo_url
                }
            else:
                self.log(f"❌ Error: {profile['error']}")
                self.status = "idle"
                return {'success': False, 'error': profile['error']}
                
        except Exception as e:
            self.log(f"❌ Exception: {e}")
            self.status = "idle"
            return {'success': False, 'error': str(e)}


class ValidatorBot(BaseBot):
    """
    Validator Bot: Validates tool quality
    Specialization: Quality control and filtering
    """
    
    def __init__(self, bot_id: str):
        super().__init__(bot_id, "Validator")
        
    def work(self, task: Dict):
        """Validate a tool profile"""
        self.status = "working"
        profile = task.get('profile')
        
        self.log(f"Validating: {profile.get('name')}")
        
        validation_results = {
            'has_name': bool(profile.get('name')),
            'has_description': bool(profile.get('description') or profile.get('tagline')),
            'has_stars': profile.get('stars', 0) >= 50,
            'has_license': bool(profile.get('license')),
            'has_readme': bool(profile.get('description')),
            'is_active': self._check_activity(profile),
            'has_docs': profile.get('has_docs', False),
        }
        
        # Calculate quality score
        score = sum(validation_results.values()) / len(validation_results)
        passed = score >= 0.6  # 60% threshold
        
        if passed:
            self.log(f"✅ PASSED (score: {score:.2f})")
        else:
            self.log(f"❌ FAILED (score: {score:.2f})")
        
        self.tasks_completed += 1
        self.status = "idle"
        
        return {
            'success': True,
            'passed': passed,
            'score': score,
            'validation_results': validation_results,
            'profile': profile
        }
    
    def _check_activity(self, profile: Dict) -> bool:
        """Check if repo is actively maintained"""
        last_updated = profile.get('last_updated')
        if not last_updated:
            return False
        
        try:
            from dateutil import parser
            updated_date = parser.parse(last_updated)
            days_since_update = (datetime.now(updated_date.tzinfo) - updated_date).days
            return days_since_update < 180  # Updated in last 6 months
        except:
            return True  # Assume active if can't parse


class WriterBot(BaseBot):
    """
    Writer Bot: Saves validated tools to database
    Specialization: Database operations and file I/O
    """
    
    def __init__(self, bot_id: str):
        super().__init__(bot_id, "Writer")
        self.tools_dir = "data/tools"
        os.makedirs(self.tools_dir, exist_ok=True)
        
    def work(self, task: Dict):
        """Write tool profile to database"""
        self.status = "working"
        profile = task.get('profile')
        
        tool_name = profile.get('name', 'unknown').lower().replace(' ', '-').replace('/', '-')
        filename = f"{self.tools_dir}/{tool_name}.json"
        
        # Check if already exists
        if os.path.exists(filename):
            self.log(f"⏭️  Already exists: {tool_name}")
            self.status = "idle"
            return {'success': True, 'action': 'skipped', 'reason': 'already_exists'}
        
        self.log(f"Writing: {tool_name}")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            
            self.log(f"✅ Saved: {filename}")
            self.tasks_completed += 1
            self.status = "idle"
            
            return {
                'success': True,
                'action': 'saved',
                'filename': filename,
                'tool_name': tool_name
            }
            
        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.status = "idle"
            return {'success': False, 'error': str(e)}


class KeywordBot(BaseBot):
    """
    Keyword Bot: Generates search keywords
    Specialization: Keyword research and trend analysis
    """
    
    def __init__(self, bot_id: str):
        super().__init__(bot_id, "Keyword")
        
        # Base keyword categories
        self.keyword_categories = {
            'llm': ['llm', 'language model', 'gpt', 'transformer', 'bert', 'llama'],
            'chatbot': ['chatbot', 'conversational ai', 'dialogue', 'chat assistant'],
            'agent': ['autonomous agent', 'ai agent', 'multi-agent', 'agent framework'],
            'rag': ['rag', 'retrieval augmented', 'vector database', 'embedding'],
            'automation': ['ai automation', 'workflow', 'orchestration', 'pipeline'],
            'vision': ['computer vision', 'image recognition', 'object detection', 'opencv'],
            'nlp': ['nlp', 'natural language', 'text processing', 'sentiment analysis'],
            'tools': ['ai tools', 'ml tools', 'ai framework', 'ml framework'],
        }
        
    def work(self, task: Dict):
        """Generate relevant keywords for searching"""
        self.status = "working"
        category = task.get('category', 'all')
        
        self.log(f"Generating keywords for: {category}")
        
        if category == 'all':
            # Generate keywords from all categories
            keywords = []
            for cat_keywords in self.keyword_categories.values():
                keywords.extend(cat_keywords)
        else:
            # Generate keywords for specific category
            keywords = self.keyword_categories.get(category, [])
        
        # Add variations
        expanded_keywords = self._expand_keywords(keywords)
        
        self.log(f"Generated {len(expanded_keywords)} keywords")
        self.tasks_completed += 1
        self.status = "idle"
        
        return {
            'success': True,
            'keywords': expanded_keywords,
            'count': len(expanded_keywords)
        }
    
    def _expand_keywords(self, keywords: List[str]) -> List[str]:
        """Expand keywords with variations"""
        expanded = set(keywords)
        
        # Add common suffixes
        suffixes = ['framework', 'library', 'tool', 'api', 'sdk']
        for keyword in keywords:
            for suffix in suffixes:
                expanded.add(f"{keyword} {suffix}")
        
        return list(expanded)


class MonitorBot(BaseBot):
    """
    Monitor Bot: Watches for new tools and trends
    Specialization: Real-time monitoring and alerts
    """
    
    def __init__(self, bot_id: str):
        super().__init__(bot_id, "Monitor")
        self.github_api = "https://api.github.com"
        
    def work(self, task: Dict):
        """Monitor GitHub for trending repos"""
        self.status = "working"
        
        self.log("Monitoring GitHub trending...")
        
        trending_repos = []
        
        # Check trending repos
        queries = [
            "ai created:>2024-01-01 stars:>500",
            "llm created:>2024-01-01 stars:>500",
            "agent created:>2024-01-01 stars:>500"
        ]
        
        for query in queries:
            try:
                url = f"{self.github_api}/search/repositories"
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
                        trending_repos.append({
                            'url': repo.get('html_url'),
                            'name': repo.get('full_name'),
                            'stars': repo.get('stargazers_count'),
                            'trending': True
                        })
                
                time.sleep(3)
                
            except Exception as e:
                self.log(f"Error monitoring: {e}")
        
        self.log(f"Found {len(trending_repos)} trending repos")
        self.tasks_completed += 1
        self.status = "idle"
        
        return {
            'success': True,
            'trending': trending_repos,
            'count': len(trending_repos)
        }


# ============================================================================
# BOT ARMY MANAGER
# ============================================================================

class BotArmyManager:
    """
    Manages the bot army
    - Creates initial army
    - Clones bots when needed
    - Distributes tasks
    - Monitors performance
    """
    
    def __init__(self):
        self.bots = {
            'scout': [],
            'extractor': [],
            'validator': [],
            'writer': [],
            'keyword': [],
            'monitor': []
        }
        
        self.task_queues = {
            'scout': queue.Queue(),
            'extractor': queue.Queue(),
            'validator': queue.Queue(),
            'writer': queue.Queue(),
            'keyword': queue.Queue(),
            'monitor': queue.Queue()
        }
        
        self.results = {
            'discovered': [],
            'extracted': [],
            'validated': [],
            'saved': []
        }
        
        self.is_running = False
        
    def create_initial_army(self):
        """Create the initial bot army"""
        print("\n" + "="*60)
        print("🤖 CREATING BOT ARMY")
        print("="*60)
        
        # Create 2 of each bot type
        bot_types = [
            (ScoutBot, 'scout', 3),
            (ExtractorBot, 'extractor', 2),
            (ValidatorBot, 'validator', 2),
            (WriterBot, 'writer', 1),
            (KeywordBot, 'keyword', 1),
            (MonitorBot, 'monitor', 1)
        ]
        
        for bot_class, bot_type, count in bot_types:
            for i in range(count):
                bot = bot_class(f"{bot_type}-{i+1}")
                self.bots[bot_type].append(bot)
                print(f"✅ Created: {bot.bot_type}-{bot.bot_id}")
        
        total_bots = sum(len(bots) for bots in self.bots.values())
        print(f"\n🎉 Army created: {total_bots} bots ready!")
        
    def clone_bot(self, bot_type: str):
        """Clone a bot when queue is busy"""
        current_count = len(self.bots[bot_type])
        max_count = BOT_ARMY_CONFIG['max_bots_per_type']
        
        if current_count >= max_count:
            return None
        
        # Create new bot
        bot_classes = {
            'scout': ScoutBot,
            'extractor': ExtractorBot,
            'validator': ValidatorBot,
            'writer': WriterBot,
            'keyword': KeywordBot,
            'monitor': MonitorBot
        }
        
        bot_class = bot_classes[bot_type]
        new_bot_id = f"{bot_type}-{current_count + 1}"
        new_bot = bot_class(new_bot_id)
        
        self.bots[bot_type].append(new_bot)
        
        print(f"\n🔄 CLONED: {new_bot.bot_type}-{new_bot.bot_id} (Total: {len(self.bots[bot_type])})")
        
        return new_bot
    
    def check_and_clone(self, bot_type: str):
        """Check if we need to clone bots"""
        queue_size = self.task_queues[bot_type].qsize()
        idle_bots = sum(1 for bot in self.bots[bot_type] if bot.status == 'idle')
        
        # Clone if queue is large and no idle bots
        if queue_size >= BOT_ARMY_CONFIG['clone_threshold'] and idle_bots == 0:
            self.clone_bot(bot_type)
    
    def assign_task(self, bot_type: str, task: Dict):
        """Assign a task to a bot"""
        self.task_queues[bot_type].put(task)
        self.check_and_clone(bot_type)
    
    def bot_worker(self, bot: BaseBot, bot_type: str):
        """Worker thread for a bot"""
        while self.is_running:
            try:
                # Get task from queue (with timeout)
                task = self.task_queues[bot_type].get(timeout=5)
                
                # Execute task
                result = bot.work(task)
                
                # Store result
                if result.get('success'):
                    if bot_type == 'scout':
                        self.results['discovered'].extend(result.get('discovered', []))
                    elif bot_type == 'extractor':
                        self.results['extracted'].append(result)
                    elif bot_type == 'validator':
                        if result.get('passed'):
                            self.results['validated'].append(result)
                    elif bot_type == 'writer':
                        if result.get('action') == 'saved':
                            self.results['saved'].append(result)
                
                # Mark task as done
                self.task_queues[bot_type].task_done()
                
                # Rest
                time.sleep(BOT_ARMY_CONFIG['rest_time'])
                
            except queue.Empty:
                # No tasks, rest
                time.sleep(1)
            except Exception as e:
                bot.log(f"Error in worker: {e}")
    
    def start_army(self):
        """Start all bots working"""
        print("\n" + "="*60)
        print("🚀 STARTING BOT ARMY")
        print("="*60)
        
        self.is_running = True
        threads = []
        
        # Start worker threads for each bot
        for bot_type, bots in self.bots.items():
            for bot in bots:
                thread = threading.Thread(
                    target=self.bot_worker,
                    args=(bot, bot_type),
                    daemon=True
                )
                thread.start()
                threads.append(thread)
        
        print(f"✅ Started {len(threads)} bot workers")
        
        return threads
    
    def stop_army(self):
        """Stop all bots"""
        print("\n⏹️  Stopping bot army...")
        self.is_running = False
        time.sleep(2)
        print("✅ Army stopped")
    
    def get_stats(self):
        """Get army statistics"""
        stats = {
            'total_bots': sum(len(bots) for bots in self.bots.values()),
            'bots_by_type': {k: len(v) for k, v in self.bots.items()},
            'tasks_completed': {},
            'queue_sizes': {},
            'results': {
                'discovered': len(self.results['discovered']),
                'extracted': len(self.results['extracted']),
                'validated': len(self.results['validated']),
                'saved': len(self.results['saved'])
            }
        }
        
        for bot_type, bots in self.bots.items():
            stats['tasks_completed'][bot_type] = sum(bot.tasks_completed for bot in bots)
            stats['queue_sizes'][bot_type] = self.task_queues[bot_type].qsize()
        
        return stats
    
    def print_stats(self):
        """Print army statistics"""
        stats = self.get_stats()
        
        print("\n" + "="*60)
        print("📊 BOT ARMY STATISTICS")
        print("="*60)
        print(f"\n🤖 Total Bots: {stats['total_bots']}")
        print("\nBots by Type:")
        for bot_type, count in stats['bots_by_type'].items():
            print(f"  {bot_type.capitalize()}: {count}")
        
        print("\nTasks Completed:")
        for bot_type, count in stats['tasks_completed'].items():
            print(f"  {bot_type.capitalize()}: {count}")
        
        print("\nQueue Sizes:")
        for bot_type, size in stats['queue_sizes'].items():
            print(f"  {bot_type.capitalize()}: {size}")
        
        print("\nResults:")
        print(f"  Discovered: {stats['results']['discovered']}")
        print(f"  Extracted: {stats['results']['extracted']}")
        print(f"  Validated: {stats['results']['validated']}")
        print(f"  Saved: {stats['results']['saved']}")


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

def run_bot_army_mission():
    """Run a complete bot army mission"""
    print("\n" + "="*60)
    print("🤖 BOT ARMY MISSION CONTROL")
    print("="*60)
    
    # Create army manager
    manager = BotArmyManager()
    
    # Create initial army
    manager.create_initial_army()
    
    # Start army
    threads = manager.start_army()
    
    # Phase 1: Generate keywords
    print("\n📋 Phase 1: Generating keywords...")
    manager.assign_task('keyword', {'category': 'all'})
    time.sleep(5)
    
    # Phase 2: Scout for tools
    print("\n🔍 Phase 2: Scouting for tools...")
    keywords = [
        'llm framework', 'chatbot', 'ai agent', 'rag', 
        'vector database', 'langchain', 'autonomous agent',
        'computer vision', 'nlp', 'text generation'
    ]
    
    # Assign scouting tasks
    for i in range(0, len(keywords), 3):
        keyword_batch = keywords[i:i+3]
        manager.assign_task('scout', {'keywords': keyword_batch})
    
    # Wait for scouting to complete
    print("⏳ Waiting for scouts...")
    time.sleep(30)
    
    # Phase 3: Extract knowledge
    print("\n📦 Phase 3: Extracting knowledge...")
    discovered = manager.results['discovered'][:20]  # Limit to 20 for demo
    
    for repo in discovered:
        manager.assign_task('extractor', {'repo_url': repo['url']})
    
    # Wait for extraction
    print("⏳ Waiting for extractors...")
    time.sleep(60)
    
    # Phase 4: Validate
    print("\n✅ Phase 4: Validating tools...")
    for result in manager.results['extracted']:
        if result.get('success'):
            manager.assign_task('validator', {'profile': result['profile']})
    
    # Wait for validation
    print("⏳ Waiting for validators...")
    time.sleep(20)
    
    # Phase 5: Write to database
    print("\n💾 Phase 5: Writing to database...")
    for result in manager.results['validated']:
        manager.assign_task('writer', {'profile': result['profile']})
    
    # Wait for writing
    print("⏳ Waiting for writers...")
    time.sleep(10)
    
    # Print final stats
    manager.print_stats()
    
    # Stop army
    manager.stop_army()
    
    print("\n" + "="*60)
    print("✅ MISSION COMPLETE!")
    print("="*60)
    print(f"\n🎉 Successfully added {len(manager.results['saved'])} tools to database!")


if __name__ == "__main__":
    run_bot_army_mission()
