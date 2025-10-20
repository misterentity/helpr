# Product Context

## Problem Statement
Plex server owners need an efficient way to grant library access to friends and family without manually sending each invitation through the Plex interface. The manual process is time-consuming and doesn't scale well.

## Solution
Helpr automates the Plex invitation process by providing:
1. A public-facing form where users can request access
2. Backend automation that immediately sends Plex invitations via API
3. Admin controls to manage which libraries are shared
4. Tracking and monitoring of all invitation activity

## User Personas

### Primary User: Plex Server Owner (Admin)
- **Needs**: Simple way to grant controlled access to their Plex server
- **Goals**: 
  - Automate repetitive invitation tasks
  - Control which content is shared
  - Monitor who has requested access
  - Prevent unauthorized access
- **Pain Points**: 
  - Manual Plex invitations are tedious
  - No easy way to restrict or track invitations
  - Want to share specific libraries, not entire server

### Secondary User: Friend/Family Member (Invite Requester)
- **Needs**: Easy way to request access to a Plex server
- **Goals**:
  - Quick access without bothering the server owner
  - Clear confirmation of invitation status
  - Simple, mobile-friendly interface
- **Pain Points**:
  - Having to message owner and wait for manual invite
  - Unclear if invitation was sent or received

## User Flows

### Invite Request Flow
1. User visits the public invite form
2. Enters Plex username or email address
3. (Optional) Enters invite code if required
4. Submits form
5. System validates input and sends Plex API request
6. User sees success page and receives Plex email
7. User accepts invitation through Plex

### Admin Configuration Flow
1. Admin logs into dashboard at /admin/login
2. Views current configuration and statistics
3. Selects which Plex libraries to share
4. Saves configuration
5. Tests Plex connection to verify settings
6. Monitors recent invitation requests

## UX Goals
- **Simplicity**: Minimal form fields, clear messaging
- **Responsiveness**: Works on mobile, tablet, and desktop
- **Feedback**: Clear success/error messages
- **Security**: Protected admin area, rate limiting
- **Performance**: Fast page loads and quick invitation processing

## Future Enhancements (Planned)
- Unique single-use invite links
- Tiered access levels (different library sets)
- Time-limited invitations that expire
- Integration with content request tools (Overseerr, Ombi)
- Email notifications to admin when invites are sent
- Discord/Slack webhooks for community integration

