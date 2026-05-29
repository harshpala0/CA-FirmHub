# Vercel Deployment Instructions

## 🚀 Quick Deploy (60 seconds)

### Step 1: Go to Vercel
Visit **[vercel.com](https://vercel.com)** and sign in with GitHub

### Step 2: Import Repository
- Click **"Add New"** → **"Project"**
- Click **"Import Git Repository"**
- Paste: `https://github.com/harshpala0/CA-FirmHub`
- Click **"Import"**

### Step 3: Deploy
- Vercel auto-detects Python
- Click **"Deploy"**
- Wait 2-5 minutes for build to complete

### ✅ Done!
Your app is now **live** at a Vercel URL (e.g., `ca-firmhub.vercel.app`)

---

## 📋 Environment Variables (Optional)

Add these in Vercel **Project Settings → Environment Variables**:

```
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here
FIRM_NAME=Your CA Firm Name
FIRM_REG_NO=CA/RFO/12345
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🌐 Access Your App

**URL Format**: `https://ca-firmhub.vercel.app`

**Default Credentials** (pre-configured):
- Admin: `admin` / `admin123`
- Team Leader: `team.leader` / `audit123`
- Member: `member1` / `audit123`

---

## 🔄 Auto-Deployment

**Git Push → Automatic Deployment**

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update app"
   git push origin main
   ```
3. Vercel automatically builds and deploys
4. Your live app updates within 2-5 minutes

---

## 📊 Monitor Your Deployment

**Vercel Dashboard**:
- View live logs
- Check deployment history
- Rollback if needed
- See performance metrics

---

## ⚠️ Important Notes

### Database
- **Current**: SQLite (works perfectly for Vercel)
- **For scale**: Migrate to PostgreSQL/Supabase

### File Storage
- Uploads stored in `/tmp` (Vercel ephemeral storage)
- Files persist during request/session
- For permanent storage: Use AWS S3 or Vercel Blob

### Performance
- **Free Tier**: Generous serverless limits
- **Paid**: Scale to handle any traffic

---

## 🎯 Next Steps

1. ✅ Deploy to Vercel (see above)
2. 📝 Add your firm details in environment variables
3. 🔒 Change default passwords
4. 🌍 Set custom domain (optional)
5. 📊 Share URL with your team

---

## 💡 Tips

- **Preview URL**: Vercel creates preview deployments for PR
- **Rollback**: One-click rollback to previous versions
- **Analytics**: Built-in performance monitoring
- **Logs**: Real-time deployment and runtime logs

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check Vercel logs for errors |
| Database error | Ensure `requirements.txt` has all dependencies |
| Static files not loading | Verify `static/` directory exists |
| Can't login | Check default credentials above |

---

**You're all set! Deploy now at [vercel.com](https://vercel.com) 🚀**
