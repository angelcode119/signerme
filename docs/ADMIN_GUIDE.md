# APK Studio - Admin Guide

Complete guide for administrators managing the APK Studio bot system.

## 📋 Table of Contents
- [Admin Access](#admin-access)
- [Admin Commands](#admin-commands)
- [Admin Panel](#admin-panel)
- [User Management](#user-management)
- [APK Management](#apk-management)
- [Statistics & Monitoring](#statistics--monitoring)
- [Broadcasting](#broadcasting)
- [Best Practices](#best-practices)

---

## 🔐 Admin Access

### Configuration
Add your Telegram User ID in `modules/config.py`:

```python
ADMIN_USER_IDS = [
    123456789,    # Your Telegram ID
    987654321,    # Another admin
]
```

### Finding Your User ID
1. Send `/start` to the bot
2. Your ID will be logged in `bot.log`
3. Or use Telegram bots like @userinfobot

---

## 📝 Admin Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/admin` | Open admin panel | `/admin` |
| `/broadcast <msg>` | Message all users | `/broadcast Hello everyone!` |
| `/help` | Show admin help | `/help` |

All standard user commands also available to admins.

---

## 🎛️ Admin Panel

### Access the Panel
Send `/admin` command to open the main admin panel.

### Main Menu Options

#### 1. 📊 Statistics
View comprehensive system statistics:
- **Total Users:** Registered users count
- **Active Users:** Users active in last 24h
- **Total Builds:** All-time build count
- **Today's Builds:** Builds in last 24h
- **Success Rate:** Overall success percentage
- **Queue Status:** Current builds in queue

**Weekly Activity Chart:**
- Visual bar chart of daily builds
- Last 7 days overview
- Activity trends

**Top Users:**
- Most active builders
- Build counts
- Success rates

**Storage Info:**
- APK storage usage
- Build logs size
- Total disk usage

#### 2. 👥 User Management
Complete user administration:

**View All Users:**
- Username
- Total builds
- Last activity
- Online status
- Ban status

**Filter Options:**
- 🟢 Online (last 10 min)
- 🟡 Active (last 1 hour)
- 🆕 New (last 24 hours)
- 🚫 Banned users

**User Actions:**
- View detailed profile
- Ban user
- Unban user
- View user's build history
- Check user statistics

**Ban System:**
- Custom ban reason
- Ban date tracking
- Instant effect
- Unban anytime

#### 3. 📱 APK Management
Manage available APKs:

**View APKs:**
- Display name
- File size
- Build count
- Active status
- Upload date

**Add APK:**
- ➕ Upload via Telegram
- 🔍 Scan data folder
- Automatic analysis
- Package name detection
- Version extraction

**APK Actions:**
- View statistics
- Toggle active/inactive
- Delete APK
- View usage history

**Upload Process:**
1. Click "➕ Upload APK"
2. Send APK file (max 100 MB)
3. Automatic analysis
4. Confirm details
5. APK added to system

#### 4. 📋 Queue Status
Monitor build queue:
- Active builds (realtime)
- Build progress
- User information
- Time elapsed
- APK being built

**Queue Limits:**
- Max 5 concurrent builds
- Fair queue system
- Auto-cleanup on timeout

---

## 👥 User Management

### Viewing Users

**User List Shows:**
- Username (@username)
- Build count
- Last activity (time ago)
- Status indicator
- Ban status

**Status Indicators:**
- 🟢 Online (< 10 min)
- 🟡 Active (< 1 hour)
- ⏰ Recent (< 24 hours)
- ⏳ Inactive (> 24 hours)

### Banning Users

**When to Ban:**
- Terms violation
- Abuse of service
- Suspicious activity
- Repeated failures
- Admin discretion

**How to Ban:**
1. Go to User Management
2. Select user
3. Click "🚫 Ban User"
4. Confirm action
5. (Optional) Add reason

**Ban Effects:**
- Immediate logout
- Cannot login
- Cannot build APKs
- Message: "Account banned"

### Unbanning Users

**How to Unban:**
1. Filter by "🚫 Banned"
2. Select user
3. Click "🔓 Unban User"
4. User can login again

### User Details

**Detailed View Shows:**
- Username
- User ID
- Total builds (Quick/Custom)
- Failed builds
- Success rate
- Average build time
- Total time spent
- First build date
- Last activity
- Most used APK
- Ban status & reason

---

## 📱 APK Management

### Adding APKs

**Method 1: Telegram Upload**
1. Click "➕ Upload APK"
2. Send APK file to bot
3. Wait for analysis
4. Review details
5. APK automatically added

**Method 2: Folder Scan**
1. Place APK in `data/` folder
2. Click "🔍 Scan Folder"
3. New APKs detected
4. Auto-added to database

**APK Requirements:**
- Valid APK file
- Max size: 100 MB (admin upload)
- Readable package name
- Extractable version info

### APK Information

**Each APK Shows:**
- Display name
- Package name
- Version name & code
- File size
- Build count
- Active status
- Upload date

### APK Actions

**Toggle Active/Inactive:**
- Hide APK from users
- Maintain in database
- Easy reactivation

**Delete APK:**
- Removes from database
- File remains in folder
- Requires confirmation
- Cannot be undone

**View Statistics:**
- Total builds with this APK
- Success/failure ratio
- Popular theme colors
- Average build time

---

## 📊 Statistics & Monitoring

### System Statistics

**Overall Metrics:**
- Total registered users
- Users online now
- Total builds (all-time)
- Today's builds
- This week's builds
- Success rate %
- Average build time

**Daily Activity:**
- 7-day activity chart
- Build count per day
- Visual representation
- Trend analysis

**Top Users:**
- Most active builders
- Build counts
- Success rates
- Username display

**Storage Metrics:**
- APK folder size
- Build logs size
- Total usage
- Available space

### Build Logs

**Log Location:** `logs/builds/`

**Log Format:**
```json
{
  "timestamp": "2025-11-10T12:00:00",
  "user_id": 123456789,
  "username": "user123",
  "apk_name": "Instagram",
  "duration": 45,
  "success": true,
  "is_custom": false,
  "error": null
}
```

**Daily Logs:**
- One file per day (YYYY-MM-DD.json)
- All build attempts
- Success/failure tracking
- Error details

### User Statistics

**Individual User Stats:**
- Total builds
- Quick vs Custom builds
- Failed builds
- Success rate
- Average time
- Total time spent
- First build date
- Last activity
- APK usage breakdown

---

## 📢 Broadcasting

### Sending Messages

**Command Format:**
```
/broadcast Your message here
```

**Features:**
- Reaches all registered users
- Supports markdown
- Shows progress
- Success/failure count
- Estimated time

**Use Cases:**
- System announcements
- Maintenance notices
- New features
- Important updates
- Service disruptions

**Best Practices:**
- Keep messages concise
- Use clear language
- Include action items
- Test with small group first
- Avoid spam

**Example Messages:**
```
/broadcast 🎉 New feature: Custom themes now available!

/broadcast ⚠️ Maintenance: Bot offline 10-11 PM today

/broadcast 🚀 Instagram APK updated to v280.0.0.0
```

---

## 🔧 Best Practices

### User Management
1. **Monitor Activity:** Check statistics daily
2. **Review Bans:** Periodic review of banned users
3. **Watch Patterns:** Identify suspicious behavior
4. **Quick Response:** Address issues promptly
5. **Fair Treatment:** Consistent ban policies

### APK Management
1. **Test APKs:** Verify before adding
2. **Update Regularly:** Keep APKs current
3. **Remove Outdated:** Clean old versions
4. **Monitor Usage:** Track popular APKs
5. **Check Integrity:** Verify file quality

### System Maintenance
1. **Daily Checks:** Review statistics
2. **Weekly Cleanup:** Remove old logs
3. **Monitor Storage:** Check disk space
4. **Update Documentation:** Keep guides current
5. **Backup Data:** Regular backups

### Security
1. **Protect Admin Access:** Keep IDs private
2. **Review Logs:** Check for abuse
3. **Monitor Builds:** Watch for patterns
4. **Secure Credentials:** Safe API keys
5. **Regular Audits:** Security reviews

---

## 🛠️ Troubleshooting

### Common Admin Issues

**"Admin panel not opening"**
- Verify User ID in config.py
- Restart bot
- Check logs for errors

**"Cannot upload APK"**
- Check file size (< 100 MB)
- Verify APK validity
- Check disk space
- Review bot permissions

**"Broadcast not working"**
- Check message format
- Review user database
- Check bot permissions
- Verify API limits

**"Statistics not updating"**
- Check log files
- Verify database write permissions
- Review stats_manager module
- Check file paths

### Emergency Procedures

**Bot Unresponsive:**
1. Check bot.log for errors
2. Restart bot process
3. Verify API connectivity
4. Check system resources

**Database Corruption:**
1. Stop bot
2. Backup current data
3. Restore from backup
4. Restart bot
5. Verify functionality

**User Issues:**
1. Check user details
2. Review build history
3. Check ban status
4. Test user experience
5. Provide resolution

---

## 📊 Metrics to Monitor

### Daily
- Total builds
- Success rate
- Active users
- Failed builds
- Queue status

### Weekly
- New users
- APK usage trends
- Build patterns
- Error rates
- Storage growth

### Monthly
- User retention
- Popular APKs
- System performance
- Feature usage
- Growth trends

---

## 🔍 Advanced Features

### Custom Statistics Queries
Access `logs/builds/` folder for custom analysis:
- Export to CSV
- Custom date ranges
- Advanced filtering
- Trend analysis

### Database Management
Files locations:
- `data/users.json` - User data
- `data/stats.json` - System stats
- `data/user_stats.json` - User statistics
- `data/apks.json` - APK database

**Backup Command:**
```bash
tar -czf backup-$(date +%Y%m%d).tar.gz data/ logs/
```

---

## 📞 Admin Support

### Resources
- Bot logs: `bot.log`
- Build logs: `logs/builds/`
- Configuration: `modules/config.py`
- This guide: `ADMIN_GUIDE.md`

### Getting Help
1. Check bot logs first
2. Review this documentation
3. Test in isolated environment
4. Document issues clearly
5. Contact senior admin

---

## 🔄 Regular Tasks

### Daily
- [ ] Review statistics
- [ ] Check active builds
- [ ] Monitor errors
- [ ] Respond to issues

### Weekly
- [ ] Review banned users
- [ ] Update APKs
- [ ] Clean old logs
- [ ] Check storage

### Monthly
- [ ] Generate reports
- [ ] Backup database
- [ ] Review performance
- [ ] Update documentation

---

**Admin Responsibilities:** Power comes with responsibility. Use admin features wisely and fairly.

*Last updated: 2025-11-10*
