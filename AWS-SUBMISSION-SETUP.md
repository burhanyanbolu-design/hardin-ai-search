# AWS Ubuntu Submission Handler Setup

This guide shows how to set up the submission handler on your AWS Ubuntu server.

## Why AWS Ubuntu?

- ✅ Can write files (unlike Vercel serverless)
- ✅ Can run bot army 24/7
- ✅ Can handle submissions in real-time
- ✅ Free tier available

## Setup Steps

### 1. Connect to AWS Ubuntu

```bash
ssh -i your-key.pem ubuntu@YOUR_AWS_IP
```

### 2. Navigate to Project Directory

```bash
cd hardin-ai-search
```

### 3. Pull Latest Changes

```bash
git pull origin main
```

### 4. Install Dependencies (if not already installed)

```bash
pip install flask flask-cors python-dotenv
```

### 5. Start Submission Handler

```bash
python submission_handler.py
```

You should see:
```
🚀 Hardin Submission Handler
📡 Starting server on AWS Ubuntu...
🔗 Endpoint: http://YOUR_AWS_IP:5001/api/submit
💡 This server handles tool submissions from the website
```

### 6. Run in Background (Optional)

To keep it running after you disconnect:

```bash
nohup python submission_handler.py > submission_handler.log 2>&1 &
```

Check if it's running:
```bash
ps aux | grep submission_handler
```

View logs:
```bash
tail -f submission_handler.log
```

Stop it:
```bash
pkill -f submission_handler.py
```

### 7. Update Frontend with AWS IP

Edit `index.html` and replace:
```javascript
const AWS_SUBMISSION_API = 'http://YOUR_AWS_IP:5001/api/submit';
```

With your actual AWS IP:
```javascript
const AWS_SUBMISSION_API = 'http://3.123.45.67:5001/api/submit';
```

### 8. Configure AWS Security Group

Allow incoming traffic on port 5001:

1. Go to AWS EC2 Console
2. Select your instance
3. Click "Security" tab
4. Click on the security group
5. Add inbound rule:
   - Type: Custom TCP
   - Port: 5001
   - Source: 0.0.0.0/0 (or your specific IPs)

### 9. Test the Endpoint

```bash
curl http://YOUR_AWS_IP:5001/api/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "Hardin Submission Handler",
  "version": "1.0.0",
  "location": "AWS Ubuntu"
}
```

### 10. Auto-Push to GitHub (Optional)

To automatically push new submissions to GitHub:

```bash
# Create a script
nano auto_push.sh
```

Add:
```bash
#!/bin/bash
cd /home/ubuntu/hardin-ai-search
git add data/tools/*.json data/contributions/*.json
git commit -m "Auto: New tool submissions"
git push origin main
```

Make executable:
```bash
chmod +x auto_push.sh
```

Run every hour with cron:
```bash
crontab -e
```

Add:
```
0 * * * * /home/ubuntu/hardin-ai-search/auto_push.sh
```

## Architecture

```
User Browser
    ↓
Vercel (Frontend - Read-only)
    ↓
AWS Ubuntu (Submission Handler - Can write)
    ↓
GitHub (Database)
    ↓
Vercel (Auto-deploys on push)
```

## Benefits

1. **Vercel**: Fast, free, global CDN for frontend
2. **AWS Ubuntu**: Handles submissions, runs bot army
3. **GitHub**: Free database, version control
4. **Auto-sync**: Changes on AWS → GitHub → Vercel

## Monitoring

Check submission logs:
```bash
tail -f submission_handler.log
```

Check new tools:
```bash
ls -lt data/tools/ | head -10
```

Check contributions:
```bash
ls -lt data/contributions/ | head -10
```

## Troubleshooting

**Port already in use:**
```bash
lsof -i :5001
kill -9 <PID>
```

**Permission denied:**
```bash
chmod +x submission_handler.py
```

**Module not found:**
```bash
pip install -r requirements.txt
```

## Next Steps

1. Start the submission handler on AWS
2. Get your AWS public IP
3. Update `index.html` with the IP
4. Push changes to GitHub
5. Test submissions on the live site!
