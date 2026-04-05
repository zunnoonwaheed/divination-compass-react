# Complete Setup Instructions for Swiss Ephemeris API

## ✅ What's Been Completed

1. **Fixed all code errors in main.py**
2. **Added CORS support** for your frontend (thedivinatoryreport.com)
3. **Created astrocartography endpoint** for ley lines mapping
4. **Pushed to GitHub** - All changes are now in your repository

## 🚀 Railway Deployment Steps

### Step 1: Configure Environment Variable in Railway

1. Go to your Railway project: https://railway.com/project/75201da3-321f-4d4a-935b-9cb9b8056504
2. Click on your service/deployment
3. Go to the **Variables** tab
4. Click **"+ New Variable"**
5. Add this variable:
   - **Variable Name**: `MAPBOX_TOKEN`
   - **Value**: `pk.eyJ1IjoibnVpbGx1bSIsImEiOiJjbW5leXg4NjYwNGdiMnFvdGNtbmx0eGF5In0.QNGwTpC2JCQuwVAB155qWw`

6. Click **"Add"** to save

### Step 2: Verify Build Settings (if needed)

Railway should auto-detect Python, but verify these settings:

- **Build Command**: Should be empty (Railway auto-detects from requirements.txt)
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

If the start command isn't set, add it in the **Settings** → **Deploy** section.

### Step 3: Trigger Deployment

Railway should automatically deploy after the GitHub push. If not:
1. Go to the **Deployments** tab
2. Click **"Deploy"** or **"Redeploy"**

### Step 4: Get Your Railway URL

After deployment completes (usually 2-3 minutes):
1. Go to the **Settings** tab
2. Under **Domains**, you'll see your Railway URL like:
   ```
   https://swiss-ephemeris-api-production.up.railway.app
   ```
3. Copy this URL - you'll need it for your frontend

### Step 5: Test Your API

Once deployed, test these endpoints (replace with your actual Railway URL):

**Test 1: API Status**
```bash
curl https://your-railway-url.up.railway.app/
```

**Test 2: Mapbox Token**
```bash
curl https://your-railway-url.up.railway.app/api/mapbox-token
```

**Test 3: Natal Chart**
```bash
curl "https://your-railway-url.up.railway.app/api/natal-chart?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060"
```

**Test 4: Astrocartography (Ley Lines)**
```bash
curl "https://your-railway-url.up.railway.app/api/astrocartography?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060"
```

## 🌐 Update Your Frontend (Lovable)

### Step 6: Configure Frontend API URL

In your Lovable project (https://thedivinatoryreport.com), update the API base URL:

1. Find your API configuration file (usually in `src/config` or similar)
2. Update the API URL to your Railway deployment:

```javascript
// Example configuration
const API_BASE_URL = "https://your-railway-url.up.railway.app";

// Or if using environment variables
VITE_API_URL="https://your-railway-url.up.railway.app"
```

### Step 7: Update API Calls in Frontend

Make sure your frontend is making these calls:

**For Natal Chart:**
```javascript
const response = await fetch(
  `${API_BASE_URL}/api/natal-chart?date=${date}&time=${time}&latitude=${lat}&longitude=${lon}`
);
const data = await response.json();
```

**For Mapbox Token:**
```javascript
const response = await fetch(`${API_BASE_URL}/api/mapbox-token`);
const { token } = await response.json();
```

**For Astrocartography (Ley Lines):**
```javascript
const response = await fetch(
  `${API_BASE_URL}/api/astrocartography?date=${date}&time=${time}&latitude=${lat}&longitude=${lon}`
);
const { lines, birth_location } = await response.json();
```

## 📊 Available API Endpoints

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/` | GET | API info & documentation | ✅ Ready |
| `/api/natal-chart` | GET | Calculate natal chart positions | ✅ Ready |
| `/api/astrocartography` | GET | Calculate astrocartography ley lines | ✅ Ready |
| `/api/mapbox-token` | GET | Get Mapbox API token | ✅ Ready |
| `/api/generate-astrology` | POST | AI readings (optional) | ⚠️ Requires ANTHROPIC_API_KEY |

## 🔍 Troubleshooting

### Issue: Railway deployment fails
- Check the **Logs** tab in Railway for error messages
- Verify `requirements.txt` is in the repository
- Ensure `MAPBOX_TOKEN` is set in Variables

### Issue: CORS errors in browser
- Open browser console (F12)
- If you see CORS errors, verify the frontend domain is in the `allow_origins` list in `main.py`
- Currently configured domains:
  - `https://thedivinatoryreport.com`
  - `http://localhost:3000`
  - `http://localhost:5173`

### Issue: "MAPBOX_TOKEN not set" error
- Go to Railway Variables and verify `MAPBOX_TOKEN` is set
- Redeploy after adding the variable

### Issue: Natal chart or ley lines not loading
- Check Railway logs for errors
- Test the endpoint directly with curl (see Step 5)
- Verify the frontend is calling the correct Railway URL

### Issue: Frontend shows "Failed to fetch"
- Verify Railway deployment is running (green status)
- Check that the Railway URL is correct in your frontend
- Open browser Network tab to see the exact error

## 📱 Testing the Full Report Page

Once everything is deployed:

1. Go to: https://thedivinatoryreport.com/full-report
2. Enter birth details (date, time, location)
3. Verify:
   - ✅ Natal chart loads correctly
   - ✅ Astrocartography map displays with ley lines
   - ✅ No fetch errors in browser console

## 🎉 Success Criteria

Your deployment is complete when:
- ✅ Railway shows "Deployed" status (green)
- ✅ All API endpoints return data (test with curl)
- ✅ Frontend loads natal chart without errors
- ✅ Astrocartography map displays ley lines
- ✅ No CORS errors in browser console

## 📞 Need Help?

If you encounter issues:
1. Check Railway logs in the **Logs** tab
2. Check browser console for frontend errors (F12)
3. Verify all environment variables are set
4. Test API endpoints directly with curl

## 🔐 Security Notes

- ✅ `.env` file is gitignored (not pushed to GitHub)
- ✅ Mapbox token is stored in Railway environment variables
- ✅ CORS is restricted to your specific domain
- ✅ Anthropic API key is optional and not required

---

**Your Railway Project**: https://railway.com/project/75201da3-321f-4d4a-935b-9cb9b8056504
**Your GitHub Repo**: https://github.com/allinonebrandz/swiss-ephemeris-api
**Your Frontend**: https://thedivinatoryreport.com/full-report
