# Free 24/7 Hosting Guide

Here are the best **free** options to run your Waze incidents server 24/7:

## 🏆 Best Options (Recommended)

### 1. **Railway.app** ⭐ (Best for 24/7)
**Free Tier:** $5 credit/month (usually enough for small apps)
**24/7:** ✅ Yes
**Setup Time:** 5 minutes

**Steps:**
1. Go to [railway.app](https://railway.app) and sign up (GitHub login)
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub repository
4. Railway will auto-detect Python and deploy
5. Add environment variable: `WAZE_API_URL` = your API URL
6. Done! Your app will be live at `your-app.railway.app`

**Note:** Railway gives $5 free credit/month. For a simple Python server, this usually lasts the whole month.

---

### 2. **Render.com**
**Free Tier:** ✅ Free
**24/7:** ⚠️ Sleeps after 15 min inactivity (wakes on request)
**Setup Time:** 5 minutes

**Steps:**
1. Go to [render.com](https://render.com) and sign up
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python run.py`
   - **Environment:** Python 3
5. Add environment variable: `WAZE_API_URL` = your API URL
6. Deploy!

**Note:** Free tier sleeps after 15 min, but wakes up when someone visits. For continuous fetching, consider upgrading or use Railway.

---

### 3. **Fly.io**
**Free Tier:** ✅ Free (3 shared VMs)
**24/7:** ✅ Yes
**Setup Time:** 10 minutes

**Steps:**
1. Install Fly CLI: `iwr https://fly.io/install.ps1 -useb | iex` (PowerShell)
2. Sign up: `fly auth signup`
3. Create app: `fly launch` (in your project folder)
4. Deploy: `fly deploy`
5. Set environment: `fly secrets set WAZE_API_URL="your-url"`

---

### 4. **PythonAnywhere**
**Free Tier:** ✅ Free
**24/7:** ⚠️ Limited (web apps only, no always-on tasks)
**Setup Time:** 15 minutes

**Steps:**
1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your files via Files tab
3. Create a new Web app
4. Configure to run `run.py`
5. **Note:** Free tier doesn't support always-on background tasks well

---

## 🚀 Quick Deploy Setup

### For Railway/Render (Recommended):

1. **Create a GitHub repository** with your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Update `run.py`** to use environment variables:
   - Already supports `WAZE_API_URL` from config.json
   - You can add: `os.environ.get('WAZE_API_URL')` as fallback

3. **Deploy to Railway/Render** using the steps above

---

## 📝 Environment Variables to Set

When deploying, set these environment variables:

- `WAZE_API_URL` - Your Waze API endpoint URL
- `PORT` - Port number (usually auto-set by platform)

---

## ⚙️ Modifying for Cloud Deployment

The current `run.py` uses port 8000. Most platforms set `PORT` automatically. Update `run.py`:

```python
PORT = int(os.environ.get('PORT', 8000))
```

---

## 💡 Recommendation

**Use Railway.app** - It's the easiest and most reliable for 24/7 operation with a generous free tier.

**Alternative:** If Railway credit runs out, use **Render.com** (it will wake up when accessed, so data will still accumulate, just with slight delays).

---

## 🔧 Troubleshooting

- **Port issues:** Make sure your app reads `PORT` from environment
- **Data persistence:** Cloud platforms may reset files. Consider using a database (SQLite, PostgreSQL) for long-term storage
- **API limits:** Make sure your Waze API allows requests from cloud IPs

