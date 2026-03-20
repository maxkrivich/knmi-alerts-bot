# ARCHITECTURE.md - System Design

## Overview

KNMI Alerts is a distributed system that monitors Dutch weather alerts from KNMI (Royal Netherlands Meteorological Institute) via MQTT, processes them, stores them in a database, and delivers them to users via Telegram with personalized filtering.

---

## System Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  KNMI Data Platform                         │
│            (MQTT Broker: mqtt.dataplatform.knmi.nl)         │
└────────────────┬────────────────────────────────────────────┘
                 │ Topic: dataplatform/file/v1/waarschuwingen_nederland_48h/1.0/#
                 │
        ┌────────▼────────┐
        │  report_checker │  (subscribe to MQTT alerts)
        │   (Container)   │
        └────────┬────────┘
                 │ Download & parse alert XML
                 │ Extract alerts via knmi_alerts module
                 │
        ┌────────▼────────┐
        │     Redis       │  (pub/sub channel)
        │  (Container)    │
        └────────┬────────┘
                 │ Publish alerts as JSON
                 │
        ┌────────▼────────┐
        │    notifier     │  (subscribe to Redis channel)
        │  (Container)    │
        └────────┬────────┘
                 │ Query database for subscribed users
                 │ Filter alerts by region & severity
                 │ Format Markdown messages
                 │
        ┌────────▼──────────────┐
        │   Telegram API        │
        └──────────┬─────────────┘
                   │
        ┌──────────▼──────────┐
        │  Users (on Telegram)│
        └─────────────────────┘

        ┌──────────────────────┐
        │     knmi_bot         │  (Telegram bot for user management)
        │    (Container)       │
        └──────────┬───────────┘
                   │ Handle /start, /region, /mute commands
                   │
        ┌──────────▼──────────┐
        │  PostgreSQL DB      │  (Persistent storage)
        │    (Container)      │
        └─────────────────────┘
```

---

## Core Components

### 1. **report_checker Service**
**Location:** `report_checker/`

**Responsibilities:**
- Subscribes to KNMI MQTT broker with secure token authentication
- Listens to alert file updates on the topic `dataplatform/file/v1/waarschuwingen_nederland_48h/1.0/#`
- Downloads alert XML files when notifications arrive
- Parses XML alerts using `knmi_alerts` module
- Publishes parsed alerts as JSON to Redis channel
- Handles graceful reconnection to MQTT (maintains session ID across restarts)

**Key Implementation:**
- Uses `paho-mqtt` library with MQTTv5 protocol
- WebSocket transport to MQTT broker over TLS/SSL
- Maintains connection state to replay missed events (QoS=1)
- Low-latency message processing to avoid blocking MQTT PUBACK messages

---

### 2. **notifier Service**
**Location:** `notifier/`

**Responsibilities:**
- Subscribes to Redis pub/sub channel for incoming alerts
- Retrieves user subscription preferences from PostgreSQL database
- Filters alerts based on:
  - User's subscribed region(s) (Dutch province)
  - Alert severity level (Red/Orange/Yellow)
  - User's mute/snooze settings
- Formats alerts into Markdown Telegram messages with:
  - Phenomenon name with emoji coding
  - Color-coded severity level
  - Start/end times in human-readable format
  - Alert description in English
  - Call-to-action button
- Sends Telegram messages via Telegram Bot API
- Handles failed deliveries (soft-deletes users who are unreachable)
- Stores alert report records in database via internal API

**Key Implementation:**
- Uses `telebot` library for Telegram API interaction
- Markdown formatting with emoji indicators for severity
- Graceful error handling: users are soft-deleted on unreachable errors
- Calls internal API (`API_URL`) to create/update alert reports

---

### 3. **knmi_bot Service**
**Location:** `knmi_bot/`

**Responsibilities:**
- Serves as Telegram chatbot for user interactions
- Handles command handlers:
  - `/start` - User registration
  - `/region` - User selects subscribed region(s)
  - `/mute` - User enables/disables alert delivery
- Creates and updates user records in PostgreSQL
- Manages soft-deleted users (reactivation on `/start`)

**Key Implementation:**
- Uses `telebot` library with command handlers
- Users stored in database with fields: `telegram_id`, `region(s)`, `mute_code`, `is_active`
- Regions are Dutch provinces: Drenthe, Flevoland, Friesland, etc.

---

### 4. **PostgreSQL Database**
**Location:** `schema/`

**Responsibilities:**
- Persistent storage of:
  - User accounts and preferences
  - Alert history and reports
  - Mute/quiet hour settings
  - Alert metadata

**Schema Includes:**
- `users` table: ID, telegram_id, region, mute_code, created_at, updated_at, is_active
- `alerts` table: region, issue_date, alerts (JSON), created_at, updated_at

---

### 5. **Redis Pub/Sub Broker**
**Location:** Docker service

**Responsibilities:**
- Inter-service message queue between `report_checker` and `notifier`
- Decouples alert ingestion from alert delivery
- Allows both services to run independently and restart without losing messages

**Configuration:**
- Channel name: Environment variable `REDIS_CHANNEL`
- Messages published as JSON strings

---

## Data Flow

### Alert Processing Pipeline

```
1. KNMI System
   ↓ (MQTT message with alert file URL)
2. report_checker subscribes and receives notification
   ↓ (Downloads XML, parses alerts)
3. Alerts published to Redis channel as JSON
   ↓
4. notifier subscribes to Redis channel
   ↓ (Receives alert JSON)
5. notifier queries database for subscribed users
   ↓ (Filters by region & severity)
6. Format and send Telegram messages
   ↓
7. Update alert report in database
```

### User Interaction Pipeline

```
1. User sends /start to knmi_bot
   ↓
2. knmi_bot creates user in database
   ↓
3. User sends /region to select provinces
   ↓
4. knmi_bot updates user region preference
   ↓
5. User sends /mute to snooze alerts
   ↓
6. knmi_bot updates user mute_code
   ↓
7. When alerts arrive, notifier checks mute_code before sending
```

---

## Communication Patterns

### MQTT (report_checker ↔ KNMI)
- **Protocol:** MQTTv5 over WebSocket with TLS
- **Authentication:** Token-based (username: "token", password: NOTIFICATION_TOKEN)
- **QoS:** 1 (at-least-once delivery with replay on reconnect)
- **Topic:** `dataplatform/file/v1/waarschuwingen_nederland_48h/1.0/#`

### Redis Pub/Sub (report_checker ↔ notifier)
- **Pattern:** Publish-Subscribe asynchronous messaging
- **Channel:** Configured via `REDIS_CHANNEL` env var
- **Message Format:** JSON string with parsed alert data

### Database API (notifier ↔ PostgreSQL)
- **Protocol:** RESTful HTTP API served internally
- **Endpoints:** `/alerts` (GET, POST, PATCH)
- **Query Parameters:** region, issue_date filters

### Telegram API (notifier ↔ Users)
- **Protocol:** HTTPS REST API
- **Authentication:** Bot token from `telegram_bot_token` secret
- **Message Format:** Markdown with emoji formatting

---

## Deployment

### Docker Compose Services
- **report_checker** - Alert listener (always running)
- **notifier** - Alert dispatcher (always running)
- **knmi_bot** - User management bot (always running)
- **PostgreSQL** - Database (persistent volume)
- **Redis** - Pub/sub broker (in-memory)

### Environment Variables & Secrets
```
Secrets (from Docker secrets or .env):
- notification_client_id    # MQTT client ID
- notification_token        # MQTT authentication token
- open_data_api_token      # KNMI Open Data API token
- telegram_bot_token       # Telegram bot API token

Environment Variables:
- REDIS_CHANNEL            # Redis pub/sub channel name
- API_URL                  # Internal PostgreSQL API endpoint
- POSTGRES_*              # Database connection details
```

---

## Error Handling & Resilience

### MQTT Connection
- Automatic reconnection with clean session disabled
- Maintains session state for up to 1 hour
- Replays missed messages on reconnect (QoS 1)

### User Delivery
- Failed message sends trigger user soft-delete (not hard delete)
- Users can be reactivated by sending `/start` again
- Prevents repeatedly failing message attempts

### Database Operations
- Status code checking on all API requests
- 409 Conflict handled for duplicate alert reports
- Explicit error logging with context

---

## Security

- **Token Authentication:** MQTT and internal API use token-based auth
- **TLS/SSL:** All external connections encrypted
- **Docker Secrets:** Sensitive credentials injected at runtime
- **Gitleaks:** Pre-commit hook prevents secret commits
- **Input Validation:** Pre-commit hooks validate YAML, JSON, AST integrity
