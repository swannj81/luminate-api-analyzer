# 🚀 Setup & Sharing Guide

## 📁 Finding Your Code in Cursor

### Your Workspace Location
Your code is located at:
```
C:\Users\JoshuaSwann\Luminate API
```

### Viewing Files in Cursor

1. **File Explorer (Left Sidebar)**:
   - Look for the folder icon in the left sidebar
   - Click it to see all your project files
   - You should see:
     - `app.py` - Main Streamlit application (UI)
     - `luminate_client.py` - API client code
     - `analysis.py` - Detection logic
     - `config.py` - Configuration
     - `requirements.txt` - Dependencies
     - `README.md` - Documentation

2. **Opening Files**:
   - Click any file name to open it in the editor
   - Use `Ctrl+P` (Windows) to quickly search and open files by name

3. **Main Files to Know**:
   - **`app.py`** - This is your main UI file (Streamlit app)
   - **`config.py`** - Contains your API credentials
   - **`luminate_client.py`** - Handles API communication

## 🖥️ Running Streamlit Locally

### Step 1: Open Terminal in Cursor

1. **Method 1**: Press `` Ctrl + ` `` (backtick key, usually above Tab)
2. **Method 2**: Go to `Terminal` → `New Terminal` in the menu
3. **Method 3**: Right-click in the file explorer → `Open in Integrated Terminal`

### Step 2: Install Dependencies (First Time Only)

```bash
pip install -r requirements.txt
```

### Step 3: Run the Application

```bash
streamlit run app.py
```

### Step 4: Access the App

After running the command, you'll see:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

- **Click the Local URL** or open `http://localhost:8501` in your browser
- The app will open automatically in most cases

### Stopping the App

- Press `Ctrl+C` in the terminal to stop the Streamlit server

## 🌐 Sharing with Coworkers

You have several options to share the app with your team:

### Option 1: Local Network Sharing (Easiest - No Setup)

**Best for**: Quick sharing within your office network

1. **Find Your Network IP**:
   - When you run `streamlit run app.py`, look for the "Network URL"
   - It will look like: `http://192.168.1.100:8501`

2. **Share the Network URL**:
   - Give coworkers the Network URL
   - They can access it from any device on the same network

3. **Important Notes**:
   - ✅ Your computer must be running the app
   - ✅ Coworkers must be on the same network (same WiFi/office network)
   - ✅ Your firewall may need to allow connections (Windows will prompt you)
   - ❌ Won't work if coworkers are remote/at home

**To make it easier, you can configure Streamlit to always show the network URL:**

Create a file `.streamlit/config.toml`:
```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = false
```

### Option 2: Streamlit Cloud (Free & Easy)

**Best for**: Sharing with remote coworkers, always available

1. **Create a GitHub Account** (if you don't have one):
   - Go to https://github.com
   - Sign up for free

2. **Create a New Repository**:
   - Click "New" repository
   - Name it (e.g., "luminate-analyzer")
   - Make it **Private** (to protect your API credentials)
   - Don't initialize with README

3. **Upload Your Code** (but NOT credentials):
   - **IMPORTANT**: Create a `.env.example` file instead of `.env`
   - Add `.env` to `.gitignore` (already done)
   - Upload all files EXCEPT `.env`

4. **Deploy to Streamlit Cloud**:
   - Go to https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file to `app.py`
   - Add your secrets (API credentials) in the "Secrets" section:
     ```
     LUM_API_KEY=qrbtgVuVTgaJq0VbuE8y1lX1xaoKg9D2tQQu0yg7
     LUM_USERNAME=joshua.swann@themlc.com
     LUM_PASSWORD=Music2025!
     ```

5. **Share the Link**:
   - Streamlit Cloud gives you a URL like: `https://your-app.streamlit.app`
   - Share this with coworkers

**Pros**: 
- ✅ Free
- ✅ Always available
- ✅ Works from anywhere
- ✅ No need to keep your computer on

**Cons**:
- ❌ Requires GitHub account
- ❌ Public repos are visible (use private repo)

### Option 3: Deploy to Your Own Server

**Best for**: Full control, enterprise use

Options include:
- **Heroku** (paid, but easy)
- **AWS/Azure/GCP** (more complex, more control)
- **Docker** (containerize and deploy anywhere)

This requires more technical setup. Let me know if you want help with this option.

### Option 4: Use ngrok (Temporary Sharing)

**Best for**: Quick temporary sharing with remote users

1. **Install ngrok**:
   - Download from https://ngrok.com
   - Extract and add to PATH

2. **Run Streamlit**:
   ```bash
   streamlit run app.py
   ```

3. **In a new terminal, run ngrok**:
   ```bash
   ngrok http 8501
   ```

4. **Share the ngrok URL**:
   - ngrok gives you a URL like: `https://abc123.ngrok.io`
   - Share this with coworkers
   - Works from anywhere, but URL changes each time (unless paid)

**Pros**: 
- ✅ Quick setup
- ✅ Works remotely
- ✅ No account needed

**Cons**:
- ❌ URL changes (free version)
- ❌ Temporary (stops when you close ngrok)

## 🔒 Security Considerations

### When Sharing:

1. **API Credentials**:
   - Never commit `.env` file to GitHub
   - Use Streamlit Cloud "Secrets" for cloud deployments
   - For local network sharing, credentials stay on your machine (safe)

2. **Network Security**:
   - Local network sharing is generally safe within your office
   - For external sharing, use Streamlit Cloud or ngrok (HTTPS)

3. **Access Control**:
   - Streamlit Cloud: Can add password protection
   - Local network: Anyone on network can access (consider firewall rules)

## 📝 Quick Reference

### Daily Use Commands

```bash
# Navigate to project folder
cd "C:\Users\JoshuaSwann\Luminate API"

# Run the app
streamlit run app.py

# Stop the app
Ctrl+C
```

### Troubleshooting

**"Command not found: streamlit"**
- Run: `pip install streamlit`

**"Port 8501 already in use"**
- Another Streamlit app is running
- Stop it or use: `streamlit run app.py --server.port 8502`

**"Can't access from other computer"**
- Check Windows Firewall settings
- Ensure both computers are on same network
- Try the Network URL instead of localhost

**"Module not found"**
- Run: `pip install -r requirements.txt`

## 🎯 Recommended Setup for Your Team

**For Quick Office Sharing**: Use **Option 1** (Local Network)
- Easiest setup
- No external services needed
- Works great for same-office teams

**For Remote Team Members**: Use **Option 2** (Streamlit Cloud)
- Free and reliable
- Always available
- Professional URL

**For Both**: Run locally for office, deploy to Streamlit Cloud for remote access!

---

**Need Help?** Check the main `README.md` for more detailed information about the application itself.

