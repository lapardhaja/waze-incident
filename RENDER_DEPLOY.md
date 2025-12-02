# Deploy to Render.com

## Quick Steps

1. **Go to [render.com](https://render.com)** and sign up/login (use GitHub to connect)

2. **Click "New +" → "Web Service"**

3. **Connect your GitHub repository:**
   - Select `lapardhaja/waze-incident`
   - Click "Connect"

4. **Configure the service:**
   - **Name:** `waze-incidents` (or any name you want)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python run.py`
   - **Plan:** Free (or paid if you want 24/7)

5. **Add Environment Variables:**
   Click "Environment" tab and add:
   - **Key:** `WAZE_API_URL`
   - **Value:** Your Waze API URL (from your config.json or Waze Partner Hub)
   
   Optional:
   - **Key:** `UPDATE_INTERVAL_SECONDS`
   - **Value:** `120` (or your preferred interval)

6. **Deploy!**
   - Click "Create Web Service"
   - Render will automatically:
     - Clone your repo
     - Install dependencies (`pip install -r requirements.txt`)
     - Start your app (`python run.py`)
   - Wait 2-3 minutes for first deploy

7. **Your site will be live at:**
   `https://waze-incidents.onrender.com` (or your custom name)

## Notes

- **Free tier:** Sleeps after 15 min of inactivity, wakes on first request
- **Data persistence:** The `data/` folder persists between deployments
- **Auto-deploy:** Every push to `main` branch auto-deploys
- **Logs:** Check "Logs" tab to see your app output

## Troubleshooting

- **Build fails:** Check that `requirements.txt` has all dependencies
- **App crashes:** Check logs for errors, verify `WAZE_API_URL` is set correctly
- **Port issues:** Already handled - `run.py` reads `PORT` from environment

