# 🔄 Git & GitHub Setup Guide for Cursor

## Why Use Git/GitHub?

- **Backup**: Your code is safely stored in the cloud
- **Version Control**: See what changed and when
- **Collaboration**: Share code with teammates
- **Recovery**: Can restore previous versions if something breaks

## Step-by-Step Setup

### Step 1: Install Git (if not already installed)

1. **Check if Git is installed**:
   - Open terminal in Cursor (`` Ctrl + ` ``)
   - Run: `git --version`
   - If you see a version number, Git is installed ✅
   - If you get an error, install Git from: https://git-scm.com/download/win

### Step 2: Configure Git (First Time Only)

```bash
git config --global user.name "Joshua Swann"
git config --global user.email "joshua.swann@themlc.com"
```

### Step 3: Initialize Git Repository

1. **Open terminal in Cursor** (`` Ctrl + ` ``)
2. **Navigate to your project** (if not already there):
   ```bash
   cd "C:\Users\JoshuaSwann\Luminate API"
   ```
3. **Initialize Git**:
   ```bash
   git init
   ```

### Step 4: Create GitHub Repository

1. **Go to GitHub**: https://github.com
2. **Sign in** (or create account if needed)
3. **Click the "+" icon** (top right) → "New repository"
4. **Repository settings**:
   - Name: `luminate-api-analyzer` (or any name you like)
   - Description: "Luminate Music API analyzer for detecting manipulation"
   - **Visibility**: Choose **Private** (to protect your API credentials)
   - **DO NOT** check "Initialize with README" (we already have files)
5. **Click "Create repository"**

### Step 5: Connect Local Repository to GitHub

After creating the GitHub repo, GitHub will show you commands. Use these:

```bash
# Add all files to Git
git add .

# Make your first commit
git commit -m "Initial commit: Luminate API analyzer"

# Connect to GitHub (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/luminate-api-analyzer.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Note**: GitHub will ask for your username and password (or personal access token).

### Step 6: Set Up Personal Access Token (for authentication)

GitHub requires a token instead of password:

1. **Go to GitHub** → Click your profile (top right) → **Settings**
2. **Developer settings** (bottom left) → **Personal access tokens** → **Tokens (classic)**
3. **Generate new token (classic)**
4. **Settings**:
   - Note: "Luminate API Project"
   - Expiration: Choose your preference (90 days, 1 year, etc.)
   - **Scopes**: Check `repo` (full control of private repositories)
5. **Generate token** and **COPY IT** (you won't see it again!)
6. **Use this token** as your password when Git asks

### Step 7: Verify Setup

```bash
# Check status
git status

# View remote connection
git remote -v
```

## Daily Usage

### Making Changes and Saving to GitHub

After you make changes to your code:

```bash
# 1. See what changed
git status

# 2. Add changed files
git add .

# 3. Commit with a message describing what you changed
git commit -m "Fixed 204 error handling and added error log"

# 4. Push to GitHub
git push
```

### Viewing Change History

```bash
# See commit history
git log

# See what changed in a file
git diff filename.py
```

## Using Git in Cursor UI

Cursor has built-in Git support:

1. **Source Control Panel**:
   - Click the **Source Control icon** in the left sidebar (looks like a branch)
   - Or press `Ctrl+Shift+G`

2. **Staging Changes**:
   - Files with changes show up in "Changes"
   - Click the **+** next to files to stage them
   - Or click **+** next to "Changes" to stage all

3. **Committing**:
   - Type a commit message in the box at the top
   - Click the checkmark (✓) or press `Ctrl+Enter`

4. **Pushing**:
   - Click the **...** menu (three dots)
   - Select **Push** (or **Sync** to pull and push)

## Important: Protecting Credentials

Your `.gitignore` file already protects sensitive files:
- `.env` files (credentials)
- Python cache files
- IDE settings

**NEVER commit**:
- API keys
- Passwords
- Personal tokens
- `.env` files

## Quick Reference Commands

```bash
# Check status
git status

# Add all changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push

# Pull latest changes (if working on multiple computers)
git pull

# See commit history
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1

# See what files changed
git diff
```

## Troubleshooting

### "Repository not found"
- Check the remote URL: `git remote -v`
- Verify you have access to the GitHub repository
- Make sure the repository name is correct

### "Authentication failed"
- Use a Personal Access Token instead of password
- Make sure token has `repo` scope

### "Nothing to commit"
- All changes are already committed
- Or no files have been modified

### "Merge conflicts"
- This happens if you edited the same file on GitHub and locally
- Cursor will help you resolve conflicts
- Usually just need to choose which version to keep

## Best Practices

1. **Commit often**: Small, frequent commits are better than large ones
2. **Good commit messages**: Describe what changed and why
   - Good: "Fixed 204 error handling - now logs as error when data exists on web"
   - Bad: "fix"
3. **Pull before push**: If working on multiple computers, pull first
4. **Review before commit**: Check what you're committing with `git status`

## Next Steps

Once set up, your code will be:
- ✅ Backed up on GitHub
- ✅ Version controlled (can see all changes)
- ✅ Accessible from anywhere
- ✅ Shareable with teammates (if you give them access)

---

**Need Help?** Git can be confusing at first. The Cursor UI makes it easier, but if you get stuck, the terminal commands above will always work!

