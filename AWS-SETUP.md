# 🤖 Hardin Bot Army - AWS Ubuntu Setup

## Deploy Bot Army to AWS EC2

### Step 1: Connect to Your AWS Server

```bash
ssh -i your-key.pem ubuntu@your-server-ip
```

---

### Step 2: Install Dependencies

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and Git
sudo apt install python3 python3-pip git -y

# Install Python packages
pip3 install Flask Flask-CORS requests schedule
```

---

### Step 3: Clone Repository

```bash
# Clone your repository
git clone https://github.com/burhanyanbolu-design/hardin-ai-search.git
cd hardin-ai-search

# Or if already cloned, pull latest
cd hardin-ai-search
git pull
```

---

### Step 4: Configure Git (for auto-commits)

```bash
# Set up Git credentials
git config --global user.name "Hardin Bot Army"
git config --global user.email "your-email@example.com"

# Set up GitHub authentication
# Option 1: Use Personal Access Token
git config --global credential.helper store

# Then do a git push once and enter your token
# Token will be saved for future pushes
```

---

### Step 5: Create Bot Army Service

Create a systemd service to run bot army 24/7:

```bash
sudo nano /etc/systemd/system/hardin-bot-army.service
```

Paste this:

```ini
[Unit]
Description=Hardin Bot Army - AI Tool Discovery
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/hardin-ai-search
ExecStart=/usr/bin/python3 bot_army.py
Restart=always
RestartSec=3600
StandardOutput=append:/home/ubuntu/hardin-bot-army.log
StandardError=append:/home/ubuntu/hardin-bot-army-error.log

[Install]
WantedBy=multi-user.target
```

Save and exit (Ctrl+X, Y, Enter)

---

### Step 6: Create Auto-Push Script

Create a script to automatically push discoveries to GitHub:

```bash
nano /home/ubuntu/hardin-ai-search/auto_push.sh
```

Paste this:

```bash
#!/bin/bash

cd /home/ubuntu/hardin-ai-search

# Check if there are new tools
if [ -n "$(git status --porcelain data/tools/)" ]; then
    # Count new tools
    NEW_TOOLS=$(git status --porcelain data/tools/ | wc -l)
    
    # Add new tools
    git add data/tools/*.json
    
    # Commit with timestamp
    git commit -m "Bot army discovered $NEW_TOOLS new tools - $(date '+%Y-%m-%d %H:%M')"
    
    # Push to GitHub
    git push origin main
    
    echo "Pushed $NEW_TOOLS new tools to GitHub"
else
    echo "No new tools discovered"
fi
```

Make it executable:

```bash
chmod +x /home/ubuntu/hardin-ai-search/auto_push.sh
```

---

### Step 7: Set Up Cron Job for Auto-Push

Push discoveries to GitHub every hour:

```bash
crontab -e
```

Add this line:

```bash
0 * * * * /home/ubuntu/hardin-ai-search/auto_push.sh >> /home/ubuntu/auto-push.log 2>&1
```

This runs every hour at minute 0.

---

### Step 8: Start Bot Army

```bash
# Enable service to start on boot
sudo systemctl enable hardin-bot-army

# Start the service
sudo systemctl start hardin-bot-army

# Check status
sudo systemctl status hardin-bot-army

# View logs
tail -f /home/ubuntu/hardin-bot-army.log
```

---

## Management Commands

### Check Bot Army Status
```bash
sudo systemctl status hardin-bot-army
```

### View Live Logs
```bash
tail -f /home/ubuntu/hardin-bot-army.log
```

### Restart Bot Army
```bash
sudo systemctl restart hardin-bot-army
```

### Stop Bot Army
```bash
sudo systemctl stop hardin-bot-army
```

### View Auto-Push Logs
```bash
tail -f /home/ubuntu/auto-push.log
```

### Manual Push
```bash
cd /home/ubuntu/hardin-ai-search
./auto_push.sh
```

---

## How It Works

1. **Bot Army Runs 24/7** on AWS
2. **Discovers New Tools** continuously
3. **Saves to data/tools/** folder
4. **Cron Job Runs Every Hour** 
5. **Auto-Commits & Pushes** to GitHub
6. **Vercel Auto-Deploys** new tools
7. **Website Updates** automatically!

---

## Monitoring

### Check How Many Tools Discovered
```bash
ls -1 /home/ubuntu/hardin-ai-search/data/tools/*.json | wc -l
```

### Check Recent Discoveries
```bash
ls -lt /home/ubuntu/hardin-ai-search/data/tools/*.json | head -10
```

### Check Git Status
```bash
cd /home/ubuntu/hardin-ai-search
git status
```

---

## Troubleshooting

### Bot Army Not Running?
```bash
sudo systemctl status hardin-bot-army
sudo journalctl -u hardin-bot-army -n 50
```

### Git Push Failing?
```bash
# Check credentials
git config --list

# Test push manually
cd /home/ubuntu/hardin-ai-search
git push origin main
```

### Python Errors?
```bash
# Check Python version
python3 --version

# Reinstall dependencies
pip3 install --upgrade Flask Flask-CORS requests schedule
```

---

## Security Notes

- Keep your SSH key secure
- Use GitHub Personal Access Token (not password)
- Regularly update Ubuntu: `sudo apt update && sudo apt upgrade`
- Monitor logs for errors
- Set up AWS security groups properly

---

## Cost

- AWS EC2 t2.micro (Free Tier): **$0/month** for 12 months
- After free tier: **~$8-10/month**
- GitHub: **Free**
- Vercel: **Free**

**Total: $0-10/month**

---

## Next Steps

1. ✅ Set up bot army on AWS
2. ✅ Monitor discoveries
3. ✅ Watch website grow automatically
4. ✅ Share your growing database!

---

**Your bot army is now running 24/7, discovering AI tools automatically! 🤖🚀**
