# 🔐 Authentication Setup Guide

## Quick Setup

### Step 1: Set Username and Password

1. **Open your `.env` file** (create it if it doesn't exist in the project root)

2. **Add these lines**:
   ```env
   APP_USERNAME=your_username
   APP_PASSWORD_HASH=your_password_hash_here
   ```

3. **Generate a password hash**:
   - Run this Python command to generate a hash:
   ```python
   import hashlib
   password = "YourSecurePassword123!"
   hash_value = hashlib.sha256(password.encode()).hexdigest()
   print(hash_value)
   ```
   - Copy the hash and paste it as `APP_PASSWORD_HASH` in your `.env` file

### Step 2: Default Credentials (If Not Set)

If you don't set environment variables, the app uses:
- **Username**: `admin`
- **Password**: `Luminate2025!`

**⚠️ IMPORTANT**: Change these defaults for production use!

## How It Works

1. **User visits the app** → Sees login page
2. **Enters credentials** → App checks against stored hash
3. **If correct** → User can access the app
4. **If wrong** → Shows error message

## Security Features

- ✅ Passwords are hashed (not stored in plain text)
- ✅ Session-based authentication (logout clears access)
- ✅ Credentials stored in environment variables (not in code)

## For Production Deployment

### Option 1: Streamlit Cloud

1. Deploy to Streamlit Cloud
2. Add secrets in Streamlit Cloud dashboard:
   ```
   APP_USERNAME=your_username
   APP_PASSWORD_HASH=your_hash_here
   ```

### Option 2: Environment Variables

Set these on your server:
```bash
export APP_USERNAME=your_username
export APP_PASSWORD_HASH=your_hash_here
```

## Multiple Users

Currently, the app supports one username/password. For multiple users, you would need to:
- Store user credentials in a database
- Use a more advanced authentication library (like `streamlit-authenticator`)
- Implement user management features

For now, you can:
- Share the same credentials with your team
- Or create different deployments with different credentials

## Troubleshooting

**"Invalid username or password"**
- Check your `.env` file has correct values
- Make sure password hash matches the password you're using
- Regenerate the hash if needed

**"Can't login"**
- Verify environment variables are loaded
- Check that `.env` file is in the project root
- Restart the Streamlit app after changing `.env`

