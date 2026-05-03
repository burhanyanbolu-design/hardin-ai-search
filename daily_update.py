"""
Daily Database Update Bot
Runs automatically to keep database fresh
Can be scheduled with Windows Task Scheduler or cron
"""

import schedule
import time
from datetime import datetime
from auto_populate_database import DatabasePopulationBot

def daily_update():
    """Run daily update tasks"""
    print("\n" + "="*60)
    print(f"🤖 DAILY UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    bot = DatabasePopulationBot()
    
    # Task 1: Discover trending tools
    print("\n📊 Task 1: Discovering trending tools...")
    trending_added = bot.discover_trending_tools()
    
    # Task 2: Update random 10 existing tools
    print("\n📊 Task 2: Updating existing tools (sample)...")
    import os
    import random
    
    all_tools = [f for f in os.listdir(bot.tools_dir) if f.endswith('.json')]
    sample_tools = random.sample(all_tools, min(10, len(all_tools)))
    
    updated = 0
    for filename in sample_tools:
        try:
            import json
            with open(f"{bot.tools_dir}/{filename}", 'r', encoding='utf-8') as f:
                tool_data = json.load(f)
            
            github_url = tool_data.get('github_url')
            if github_url:
                profile = bot.extractor.extract_repo_knowledge(github_url)
                
                if 'error' not in profile:
                    # Preserve history
                    if 'contribution' in tool_data:
                        profile['contribution'] = tool_data['contribution']
                    if 'experiences' in tool_data:
                        profile['experiences'] = tool_data['experiences']
                    
                    with open(f"{bot.tools_dir}/{filename}", 'w', encoding='utf-8') as f:
                        json.dump(profile, f, indent=2, ensure_ascii=False)
                    
                    updated += 1
                    print(f"   ✅ Updated: {filename}")
            
            time.sleep(3)
        except Exception as e:
            print(f"   ❌ Error updating {filename}: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 DAILY UPDATE COMPLETE")
    print("="*60)
    print(f"🔥 Trending tools added: {trending_added}")
    print(f"🔄 Tools updated: {updated}")
    print(f"⏰ Next update: Tomorrow at same time")
    print("="*60)


def run_scheduler():
    """Run the scheduler"""
    print("\n" + "="*60)
    print("🤖 DAILY UPDATE SCHEDULER")
    print("="*60)
    print("\n📅 Schedule: Every day at 2:00 AM")
    print("🔄 Tasks:")
    print("   - Discover trending tools")
    print("   - Update 10 random existing tools")
    print("\n⏰ Scheduler is running...")
    print("   Press Ctrl+C to stop")
    print("="*60)
    
    # Schedule daily update at 2 AM
    schedule.every().day.at("02:00").do(daily_update)
    
    # Also run immediately on start
    print("\n🚀 Running initial update now...")
    daily_update()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


def run_once():
    """Run update once (for manual execution)"""
    daily_update()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run once and exit
        run_once()
    else:
        # Run scheduler
        try:
            run_scheduler()
        except KeyboardInterrupt:
            print("\n\n⏹️  Scheduler stopped")
