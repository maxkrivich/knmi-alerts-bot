# PRODUCT.md - Feature Specification

## Overview

KNMI Alerts is a Telegram-based notification service that delivers Dutch weather alerts to users in real-time. Users subscribe to their region(s) of interest, receive alerts based on severity level, and can snooze notifications during off-hours.

---

## Product Vision

Enable Dutch residents and organizations to stay informed of critical weather warnings in their area via a simple, accessible Telegram interface.

**Target Users:**
- Dutch residents concerned about severe weather
- Organizations managing weather-dependent operations
- Emergency response coordinators

**Key Promise:**
Real-time, personalized weather alerts delivered directly to Telegram with zero friction.

---

## Core Features

### 1. User Registration & Onboarding

**Feature:** Get Started with Bot
- **User Action:** Send `/start` to Telegram bot
- **Bot Response:** Welcome message with region selection prompt
- **Backend Action:** Create new user record in database
- **Status:** User is now able to receive alerts

**Details:**
- One-time setup required per Telegram account
- Users are identified by their Telegram ID
- Soft-deleted users can reactivate with `/start`

---

### 2. Region Subscription Management

**Feature:** Select Provinces for Alerts
- **User Action:** Send `/region` command
- **Bot Response:** Inline keyboard with Dutch province options
- **Options:** 12 provinces + 2 water regions:
  - Drenthe, Flevoland, Friesland, Gelderland, Groningen, Limburg
  - Noord-Brabant, Noord-Holland, Overijssel, Utrecht, Zeeland, Zuid-Holland
  - Waddenzee, IJsselmeergebied, Waddeneilanden
- **User Selection:** Can select multiple regions
- **Backend Action:** Update user's region preference in database
- **Result:** User receives alerts only for selected region(s)

---

### 3. Alert Severity Filtering

**Feature:** Color-Coded Alert Levels
- **Three Severity Levels:**
  - 🔴 **Red** - Severe hazard, take immediate action
  - 🟠 **Orange** - Significant hazard, be prepared
  - 🟡 **Yellow** - Hazard conditions, be aware

**User Control:**
- Users can choose which severity levels to receive (e.g., Red & Orange only)
- Alert type depends on the weather phenomenon (wind, rain, snow, etc.)

---

### 4. Snooze/Mute Functionality

**Feature:** Quiet Hours / Snooze Alerts
- **User Action:** Send `/mute` command
- **Bot Response:** Confirmation that alerts are snoozed
- **Duration:** Configurable snooze period (default: until morning or custom hours)
- **Backend Action:** Update user's `mute_code` field
- **Effect:** Notifier checks mute status before sending messages
- **Resume:** User sends `/mute` again to re-enable alerts or automatic expiry

---

### 5. Real-Time Alert Delivery

**Feature:** Instant Notifications
- **Trigger:** New alert published to KNMI data platform
- **Latency:** Near-real-time delivery (seconds from alert detection)
- **Format:** Markdown-styled Telegram message with:
  - Weather phenomenon (e.g., "Heavy Wind")
  - Severity emoji (🔴 / 🟠 / 🟡)
  - Severity level text (Red/Orange/Yellow)
  - Start time (human-readable format)
  - End time (human-readable format)
  - Full alert description in English
  - Call-to-action button for more info

**Message Example:**
```
🌦️ *Weather Alert* 🌦️

🔴 *Phenomenon*: Heavy Wind Gusts
🔢 *Code* 🔴 red
⏰ *Start Time*: 2025-03-20 14:00 CET
⏳ *End Time*: 2025-03-20 22:00 CET

📢 *Description*:
Severe wind gusts up to 80 km/h expected in coastal areas. Secure loose outdoor items.

*Please click the button below to read more* 👇
```

---

### 6. Alert History & Reports

**Feature:** Database Recording
- **What's Stored:**
  - Alert content (phenomenon, times, description)
  - Region affected
  - Issue date
  - Severity level
  - Report creation and update timestamps
- **Use Cases:**
  - Historical reference
  - Pattern analysis
  - Debugging alert delivery

---

## User Workflows

### Workflow 1: New User Setup
```
1. User sends /start → Bot creates account
2. Bot prompts region selection
3. User selects region(s) → Bot confirms
4. User is ready to receive alerts
5. (Optional) User sends /mute to snooze immediately
```

### Workflow 2: Receiving Alert
```
1. KNMI publishes new alert via MQTT
2. report_checker downloads & parses XML
3. report_checker publishes to Redis
4. notifier receives alert
5. notifier queries database for subscribed users
6. notifier filters users by region & severity
7. notifier checks user's mute status
8. If not muted → send Telegram message
9. notifier logs alert report in database
```

### Workflow 3: Changing Preferences
```
1. User sends /region
2. Bot shows current regions
3. User selects new region(s)
4. Bot updates database
5. Next alert uses new preferences
```

### Workflow 4: Snoozing Alerts
```
1. User sends /mute
2. Bot updates user's mute_code in database
3. notifier checks mute_code before sending
4. User resumes alerts by sending /mute again (toggle) or waits for auto-expiry
```

---

## Technical Constraints & Considerations

### Current Limitations (MVP)
- **No custom quiet hours yet:** Snooze is binary (on/off), not time-based
- **Single account per Telegram ID:** No shared accounts
- **No alert history UI:** Users can't view past alerts in bot
- **No unsubscribe command:** Must use hard delete or contact admin
- **Telegram-only:** No email, SMS, or web dashboard
- **Dutch regions only:** Limited to KNMI's alert area

### Scalability Notes
- Redis pub/sub is not persistent; alerts in queue are lost on restart
- Consider message queue (RabbitMQ/Kafka) for production scale
- Database queries scale with number of users and regions

---

## Future Roadmap (Post-MVP)

### Phase 2: Enhanced User Control
- [ ] Granular quiet hours configuration (e.g., 22:00-07:00)
- [ ] Per-phenomenon subscriptions (wind alerts only, rain only, etc.)
- [ ] Alert history command `/history` in bot
- [ ] User preferences export/import
- [ ] Unsubscribe command `/unsubscribe`

### Phase 3: Expanded Channels
- [ ] Email notifications
- [ ] SMS alerts (opt-in)
- [ ] Web dashboard for analytics

### Phase 4: Advanced Features
- [ ] Machine learning to predict user alert preferences
- [ ] Integration with weather APIs for hyper-local forecasts
- [ ] Organizations/team accounts
- [ ] Alert aggregation (combine multiple phenomena into single message)

---

## Success Metrics

### Adoption
- Number of active users
- Regions covered (percentage of Dutch provinces with subscribers)
- Retention rate (users still active after 30/90/180 days)

### Engagement
- Alerts delivered per month
- Average alerts per user per month
- Mute/snooze toggle frequency

### Reliability
- Alert delivery success rate (% of intended recipients who receive)
- Message latency (time from KNMI alert to user notification)
- System uptime (target: 99.5%)
- User-reported false positives/negatives

---

## Data Privacy & Compliance

### Data Collection
- User's Telegram ID (required for messaging)
- User's chosen regions (for filtering)
- Mute status (for delivery control)
- Message delivery logs (for debugging)

### Data Retention
- User data retained as long as account is active
- Soft-deleted users' data retained for 30 days before purge
- Alert reports retained indefinitely for historical analysis
- No personal data shared with third parties

### GDPR Compliance
- Users can request data deletion by contacting admin
- Clear opt-in for all alerts
- No tracking or analytics cookies
- Secure token-based authentication
