# System Patterns and Architecture

## Architecture Overview
Flask-based MVC web application with external Plex API integration.

```
User Browser ←→ Flask App ←→ Plex API
                    ↓
                 Database (SQLite/PostgreSQL)
```

## Key Components

### Application Factory Pattern
- `app/__init__.py`: Uses `create_app()` factory function
- Enables flexible configuration and testing
- Initializes extensions (SQLAlchemy, Flask-Login, CSRF, rate limiter)

### Blueprint Structure
- `app/routes/main.py`: Public routes (index, invite request)
- `app/routes/admin.py`: Admin routes (login, dashboard, settings)
- Clean separation of concerns

### Service Layer
- `app/plex_service.py`: Encapsulates all Plex API interactions
- `PlexService` class with methods:
  - `connect_to_plex()`: Establishes Plex connection
  - `get_libraries()`: Fetches available library sections
  - `send_invite()`: Sends invitation to user
  - `test_connection()`: Validates Plex connectivity
- **Global instance**: `plex_service` shared across requests

### Data Layer
- `app/models.py`: SQLAlchemy models and database utilities
- `InviteRequest` model: Tracks all invitation attempts
- Functions: `create_invite_request()`, `get_recent_invites()`, `get_invite_stats()`
- Database URI detection: SQLite for local, PostgreSQL for Azure

### Configuration Management
- `config.py`: Centralized configuration class
- Environment variables loaded via `python-dotenv`
- `config.json`: Stores selected libraries (mutable runtime config)
- Methods: `get_library_config()`, `set_library_config()`

## Security Patterns

### Authentication
- Flask-Login for session management
- `AdminUser` class implements UserMixin
- Password hashing with Werkzeug (pbkdf2:sha256)
- Login required decorator on admin routes

### CSRF Protection
- Flask-WTF CSRFProtect on all forms
- Automatic token generation and validation

### Rate Limiting
- Flask-Limiter with in-memory storage
- Global limits: 200/day, 50/hour
- Invite endpoint: 5/minute, 20/hour
- Key function: remote address (IP-based)

### Input Validation
- `app/utils.py`: Sanitization and validation helpers
- Email/username format validation
- Invite code verification
- URL safety checking for redirects

## Data Flow Patterns

### Invite Request Processing
1. User submits form → `main.request_invite()`
2. Validate and sanitize input
3. Check invite code (if required)
4. Load library configuration from `config.json`
5. Call `plex_service.send_invite()`
6. Log result to database via `create_invite_request()`
7. Render success or redirect with error

### Admin Dashboard Loading
1. User accesses `/admin/dashboard`
2. Check authentication
3. Fetch Plex libraries via `plex_service.get_libraries()`
4. Load configured libraries from `config.json`
5. Query database for recent invites and stats
6. Test Plex connection status
7. Render dashboard template with all data

### Library Configuration Update
1. Admin submits library selection form
2. Extract selected library names
3. Call `Config.set_library_config()` to update `config.json`
4. Redirect back to dashboard

## Error Handling Patterns
- Try/except blocks around all Plex API calls
- Specific exception handling for PlexAPI errors (BadRequest, Unauthorized, NotFound)
- Logging at multiple levels (info, warning, error)
- User-friendly error messages via Flask flash messages
- Database rollback on transaction errors
- Graceful degradation (e.g., empty lists if data unavailable)

## **PERFORMANCE OPTIMIZATION COMPLETED** ✅

### Problems Identified and Resolved
1. **Repeated Plex Connections**: `PlexService` was reconnecting to Plex on every method call
   - ✅ **FIXED**: Added `_ensure_connected()` private method that only reconnects if connection is None
   - ✅ **RESULT**: Connection now persists across method calls within same request
   - Files: `app/plex_service.py` lines 15-18
   
2. **Redundant API Calls**: Admin dashboard was making duplicate calls
   - ✅ **FIXED**: Removed redundant `test_connection()` call from dashboard
   - ✅ **FIXED**: Connection status now derived from existing `get_libraries()` result
   - ✅ **RESULT**: Dashboard now makes only ONE Plex API call instead of 2-3
   - Files: `app/routes/admin.py` lines 54-72

3. **Database Query Load**: Dashboard was querying 50 invite records
   - ✅ **OPTIMIZED**: Reduced query from 50 to 20 records
   - ✅ **RESULT**: Faster database queries and reduced memory usage
   - Files: `app/routes/admin.py` line 61

### Implementation Details

#### PlexService Connection Management (app/plex_service.py)
```python
def _ensure_connected(self):
    """Ensure connection is established, reconnect only if necessary."""
    if self.account is None or self.server is None:
        self.connect_to_plex()
```

All methods now call `_ensure_connected()` instead of manual connection checks:
- `get_libraries()` line 39
- `send_invite()` line 52
- `test_connection()` line 98

#### Dashboard Optimization (app/routes/admin.py)
```python
# Build connection status from successful library fetch (no redundant API call)
connection_status = {
    'success': True,
    'server_name': Config.PLEX_SERVER_NAME,
    'library_count': len(libraries),
    'message': f"Successfully connected to {Config.PLEX_SERVER_NAME}"
}
```

### Performance Impact
- **Before**: 2-3 Plex API connections per dashboard load
- **After**: Exactly 1 Plex API connection per dashboard load
- **Improvement**: 50-66% reduction in API calls
- **Expected load time**: < 2 seconds (from 3-5+ seconds)

### Deferred Optimizations
The following were considered but deemed unnecessary after primary fixes:
- **Caching Layer**: Not implemented - connection reuse should provide sufficient performance
- **Connection Pooling**: Not needed for single-user admin interface
- **Advanced DB Indexing**: Not required for small dataset

These can be revisited if performance metrics indicate the need.

