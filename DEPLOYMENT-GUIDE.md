# 🚀 Hardin - Deployment Guide

## Deploy to Production (Free!)

### Prerequisites
- GitHub account
- Vercel account (free - sign up at vercel.com)

---

## Step 1: Create GitHub Repository

### Option A: Using GitHub Website
1. Go to https://github.com/new
2. Repository name: `hardin-ai-search`
3. Description: "AI tool search engine powered by self-replicating bot army"
4. Make it **Public**
5. **Don't** initialize with README (we already have files)
6. Click "Create repository"

### Option B: Using Command Line
```bash
# In the ai-search-engine folder
git init
git add .
git commit -m "Initial commit - Hardin AI Search Engine"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/hardin-ai-search.git
git push -u origin main
```

---

## Step 2: Deploy to Vercel

### Using Vercel Website (Easiest)

1. **Go to:** https://vercel.com
2. **Sign up/Login** with GitHub
3. **Click:** "Add New" → "Project"
4. **Import** your GitHub repository: `hardin-ai-search`
5. **Configure:**
   - Framework Preset: Other
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
6. **Environment Variables:** (none needed for now)
7. **Click:** "Deploy"

### Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd ai-search-engine
vercel
```

---

## Step 3: Configure Custom Domain (Optional)

1. Buy domain: `hardin.ai` or `hardin.app` (Namecheap, GoDaddy, etc.)
2. In Vercel dashboard:
   - Go to your project
   - Settings → Domains
   - Add your custom domain
   - Follow DNS configuration instructions

---

## Step 4: Verify Deployment

Once deployed, test these URLs:

```
https://your-app.vercel.app/
https://your-app.vercel.app/api/health
https://your-app.vercel.app/api/stats
https://your-app.vercel.app/api/search?q=chatbot
```

---

## Step 5: Update Bot Army for Production

The bot army should run on your local machine or a server, not on Vercel (serverless has time limits).

**Options:**
1. **Run locally:** Keep `bot_army.py` running on your computer
2. **Use GitHub Actions:** Schedule bot runs (free)
3. **Use a VPS:** DigitalOcean, Linode ($5/month)
4. **Use Render.com:** Free tier for background workers

---

## Troubleshooting

### Deployment Fails
- Check `vercel.json` is correct
- Verify `requirements.txt` has all dependencies
- Check Vercel logs for errors

### API Not Working
- Verify environment variables
- Check CORS is enabled
- Test API endpoints directly

### Database Not Loading
- Ensure `data/tools/*.json` files are committed to Git
- Check file paths are correct
- Verify JSON files are valid

---

## Post-Deployment Checklist

- [ ] Site loads at Vercel URL
- [ ] Search works
- [ ] API endpoints respond
- [ ] Stats display correctly
- [ ] Tool cards open GitHub links
- [ ] Mobile responsive
- [ ] Share on Twitter/LinkedIn
- [ ] Submit to Hacker News
- [ ] Add to AI tool directories

---

## Monitoring & Analytics

### Add Google Analytics
1. Get tracking ID from analytics.google.com
2. Add to `index.html` before `</head>`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Monitor with Vercel
- View analytics in Vercel dashboard
- Check function logs
- Monitor bandwidth usage

---

## Continuous Deployment

Once set up, every push to GitHub automatically deploys:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push

# Vercel automatically deploys!
```

---

## Cost Breakdown

- **GitHub:** Free (public repo)
- **Vercel:** Free (100GB bandwidth, 100 serverless function hours)
- **Domain:** $10-15/year (optional)
- **Total:** $0-15/year

---

## Next Steps

1. ✅ Deploy to Vercel
2. ✅ Test all functionality
3. ✅ Share on social media
4. ✅ Submit to Hacker News
5. ✅ Run bot army to grow database
6. ✅ Monitor traffic and usage
7. ✅ Iterate based on feedback

---

**You're live! 🎉**

Share your link:
- Twitter: "Just launched Hardin - AI tool search engine powered by self-replicating bots! 🤖"
- LinkedIn: Professional announcement
- Hacker News: "Show HN: Hardin - AI Tool Search Engine"
- Reddit: r/artificial, r/MachineLearning, r/SideProject

Good luck! 🚀
