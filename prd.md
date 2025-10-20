Designing an Automated Plex Invite Web Application
Overview and Inspiration

Sharing a Plex media server with friends can be streamlined by automating the invite process. Wizarr is a prime example of such an automation tool – it allows server owners to generate unique invite links that automatically add users to their Plex (or Jellyfin/Emby) server
docs.wizarr.dev
. Wizarr’s feature set includes a secure invite environment, single sign-on (SSO) support, tiered invite links, membership duration limits, and more
easypanel.io
. Inspired by Wizarr’s capabilities, we plan a simpler Python-based web application focused on automatically inviting friends to a Plex server via the Plex API. The goal is to let a friend submit a request (through a web form or unique link) and be added as a Plex friend with access to specified libraries, without manual intervention from the server owner. This app will be web-based (mobile-friendly) and use Python for the backend logic, leveraging Plex’s official APIs for inviting users.

Key Features and Requirements

Friend Invite Form: The core feature is a public-facing web form where a friend enters their Plex username or email to request access. Upon submission, the system will automatically send them a Plex server invite granting access to certain libraries. The libraries to share will be pre-defined in the app’s admin settings. The friend should then receive an invite notification or email from Plex and be able to access the shared libraries upon accepting. Notably, Plex allows inviting by username or email – if the email isn’t yet associated with a Plex account, the user can create a free Plex account when accepting the invite
support.plex.tv
.

Admin Configuration Panel: A private admin interface will allow the server owner (admin) to configure the app. Key settings include the Plex server credentials (such as an authentication token or login for the Plex account), the specific Plex libraries to share with new users, and basic controls like viewing pending invites or current shared users. The admin panel will be protected (e.g. via login or a secure token) to prevent unauthorized access. Through this interface, the admin can set which libraries (e.g. “Movies”, “TV Shows”) are shared by default when someone requests an invite. This essentially dictates the scope of media access for invited friends.

Web-Based & Mobile-Friendly UI: Both the invite request form and the admin panel will be accessible via a web browser, and the UI will be responsive to work on mobile devices. We will use a simple, clean web design (potentially with a lightweight CSS framework like Bootstrap or Tailwind) to ensure the pages render well on phones and tablets. Keeping the layout simple (minimal images, simple form inputs and buttons) will help maintain compatibility across devices.

Automation and Immediate Invites: The system will process invite requests automatically. As soon as a friend submits the form (or visits their invite link), the backend will call the Plex API to invite that user to the Plex server and share the configured libraries. There is no need for the admin to manually go into Plex to add the user – it happens in real-time. (However, we may include an optional approval step or invitation code in the future for security, as discussed later.) This automated invite leverages Plex’s “Friend” sharing mechanism under the hood – essentially the same as if the owner used Plex Web’s “Share Library” feature but triggered programmatically.

Python Technology Stack: The application will be implemented in Python (as per the requirement). We will use a Python web framework to handle HTTP requests and serve pages – a lightweight choice like Flask or FastAPI is suitable for this project. Flask is a simple option for rendering HTML templates and processing form submissions, while FastAPI could be used if we prefer a more API-driven approach with a separate frontend. Given the relatively simple requirements, Flask paired with Jinja2 templates is likely sufficient to build a form-based web UI. The Python PlexAPI library will be used to interact with Plex, since it provides convenient methods to authenticate and invite users via Plex’s API endpoints
python-plexapi.readthedocs.io
python-plexapi.readthedocs.io
. Using Python also means we can easily integrate any additional logic or data storage (like using an SQLite database or flat file for config) if needed.

System Architecture

The application will follow a classic web-app architecture with a clear separation between frontend and backend, albeit both components are part of a single server application. Here is an overview of the design:

Client (Frontend): A web interface that includes two main views: (1) the Invite Request Form for friends, and (2) the Admin Dashboard for the server owner. The frontend will be delivered as HTML/CSS/JavaScript to the user’s browser. The invite form will collect the friend’s Plex identifier (email or username) and perhaps a note or CAPTCHA if we want to prevent abuse. The admin dashboard will allow configuration input (like selecting libraries to share). Simple HTML forms will post data to the backend. We will ensure the HTML/CSS is responsive for mobile browsers by using a mobile-first design (e.g., a single-column layout on small screens).

Server (Backend): A Python web server (running Flask or a similar framework) will handle incoming HTTP requests. It will serve the HTML pages for the form and admin panel, and provide endpoints (routes) for form submissions. When a friend submits the invite form, the backend route will validate the input and then trigger the Plex invite logic. Similarly, when an admin submits changes in the admin panel (e.g., updating which libraries to share), the backend will update the configuration accordingly. The server is the brains of the operation: it talks to the Plex API and contains the rules for who to invite and what to share.

Plex API Integration: The backend communicates with Plex’s servers using the Plex API. We will obtain the Plex admin account’s API token (an authentication token that grants access to manage the Plex server) and store it securely on the server (for example, as an environment variable or in a config file not exposed publicly). With this token, our app can call Plex endpoints to manage shares. The Python PlexAPI library simplifies this by providing high-level methods – for instance, we can login or instantiate an account object and call inviteFriend(...) with the user’s email and the list of library sections to share
python-plexapi.readthedocs.io
. Internally, this results in an HTTP POST to Plex’s “shared server” API. (In raw terms, Plex expects a request to https://plex.tv/api/servers/<SERVER_ID>/shared_servers with the server’s ID, library section IDs, and either an invited user’s Plex ID or an invited email
reddit.com
reddit.com
.) The invite call will cause Plex to send an invite on behalf of the admin to the specified user. We’ll use this API call to automate the sharing. If using PlexAPI, the workflow would be: connect to Plex server via PlexServer(base_url, token), then call account = plex.myPlexAccount() and account.inviteFriend(user=email_or_username, server=plex, sections=[list_of_sections])
python-plexapi.readthedocs.io
python-plexapi.readthedocs.io
. This shares the chosen libraries with that user automatically.

Data Storage: For a simple implementation, we might not need a complex database. The app’s configuration (Plex token, selected libraries, admin credentials for the dashboard) can be stored in a small SQLite database or a JSON/YAML configuration file. However, as the app grows, we could incorporate a database to track invites or user info. Wizarr, for example, uses a dedicated Postgres database and even a Redis queue for jobs
wizarr.org
wizarr.org
, but our design can start lighter weight. Initially, the number of configuration items is small, so even environment variables or a .env file could suffice (e.g., PLEX_TOKEN, SERVER_ID, LIBRARIES_TO_SHARE, ADMIN_PASSWORD). If we choose to allow viewing current users or logging requests, a database table or two (for user invites or audit logs) might be introduced.

Session Management and Security: The app will likely maintain a simple session for the admin panel (e.g., using Flask’s session or cookies after admin login) to keep the admin logged in. The friend-facing form probably doesn’t need sessions – it’s a one-time interaction. We will ensure that only authorized access to the admin routes is possible (by checking a password or secret). For simplicity, the admin could log in with a preset password defined in config, or we integrate a minimal user system.

Diagram Note: Conceptually, the architecture flow is: Friend’s Browser –> (HTTP request) –> Python Web App –> (calls) –> Plex API –> Plex Server. The Plex server then sends an invite email to the friend. In the opposite direction, the admin interacts with the Python Web App via the admin UI to configure it (which might involve the app fetching data from Plex, like library lists or existing shares, to display).

Frontend Design (User and Admin Interfaces)

Invite Request Form (User View): This will be a simple webpage served by the app, explaining that the user can request access to the Plex server. It will have a form with fields such as: “Plex Username or Email” (the identifier for invite) and possibly a “Submit” button. Optionally, we could include a disclaimer or terms (e.g., “By requesting access, you agree to only use for personal viewing,” etc., depending on the audience). Upon submission, the form posts to a backend route (e.g., /request-invite). On success, the user might be shown a confirmation message like “Invite sent! Please check your Plex account or email to accept the invitation.” If an error occurs (e.g., invalid input or server error), a friendly error message will be displayed.

To ensure mobile compatibility, the form page will use responsive design. This means using relative widths or a single-column layout on small screens. For example, the input field and submit button will be large enough to tap on mobile, and the layout will stack vertically. We might use CSS media queries or a framework grid system to achieve this without much custom code. The page will avoid heavy graphics; it will rely on standard HTML elements which naturally adapt to different screen sizes.

Admin Dashboard (Owner View): The admin interface might be a single page or a few pages accessible after logging in (or providing an admin key). It could include the following components:

A login screen (if using password auth) where the owner enters a password to access the admin area.

The main settings page where the owner can input or view the Plex API token (or we can instruct them to put it in a config file, to avoid exposing it on a web form), select which libraries to share, and set any other options. We can fetch the list of libraries from Plex automatically: using the Plex token, the app can call Plex for available library sections. The UI can present checkboxes or a multi-select list of library names (e.g., Movies, TV, Music, etc.) and the admin checks those that should be shared. These selections are saved to the app’s config.

Possibly an invitation log or status section: for instance, list recent invites sent or current pending invites. (Plex’s API allows querying pending invites
python-plexapi.readthedocs.io
python-plexapi.readthedocs.io
, so the app could show if an invite is still pending acceptance.) This helps the admin know who has used the invite form. This could be an enhancement beyond the initial scope, but is useful for monitoring.

The admin UI will also be designed for mobile-friendliness, though by nature it’s likely the admin might use it on desktop. Using a simple responsive admin template or just structuring forms in a vertical layout should suffice.

Both user and admin pages will include basic validation (client-side and server-side). For example, the invite form should ensure the email/username field isn’t empty and perhaps matches an email format if one is entered. Client-side, we can use HTML5 validation or a bit of JavaScript; server-side, the Flask route will double-check the input and handle errors gracefully.

Backend Implementation and Plex API Integration

The backend will handle two main operations: processing invite requests and managing configuration. We outline the key technical steps and functions for each:

1. Initial Setup & Plex Connection: On server startup, the application will load the Plex admin’s credentials. This will likely be a token (since using a Plex token is more secure than storing a username/password). The admin can obtain their Plex token from their account as described in Plex docs or Wizarr’s guide
docs.wizarr.dev
docs.wizarr.dev
. We’ll store this token in an environment variable or config file. Using the Plex token and the Plex server’s base URL (or machine ID), we initialize a Plex connection in code: e.g.,

from plexapi.myplex import MyPlexAccount  
account = MyPlexAccount(token=PLEX_TOKEN)  
plex_server = account.resource(SERVER_NAME).connect()  


This finds the Plex server by name (or we use PlexServer(BASE_URL, TOKEN) if we have a direct URL). The plex_server object gives us access to library sections and sharing functions.

2. Processing an Invite Request (Backend Route): When the friend submits the form (POST request to, say, /invite), the Flask view function will retrieve the submitted identifier (username or email). It will then call the Plex API to invite the user. We have two ways to do this: using PlexAPI library’s high-level function or making an HTTP request directly. Using PlexAPI is straightforward:

sections_to_share = [plex_server.library.section(lib_name) for lib_name in CONFIG_LIBRARIES]  
account.inviteFriend(user_input, plex_server, sections=sections_to_share)


Here, user_input is the string (email or Plex username) provided by the friend
python-plexapi.readthedocs.io
, and CONFIG_LIBRARIES is a list of library names or IDs stored from admin settings. The library.section() call gets the LibrarySection objects needed. The inviteFriend function sends the invite to that user on the specified server with those libraries shared. Under the hood, this translates to a Plex API call to create a share (as a pending invite). In raw HTTP terms, Plex would receive a request like:

POST https://plex.tv/api/servers/<ServerID>/shared_servers?X-Plex-Token=<token>  
Content-Type: application/json

{
  "server_id": <ServerID>,
  "shared_server": {
      "library_section_ids": [<IDs of Movies, IDs of Shows, ...>],
      "invited_email": "<friend_email_or_username>",
      "sharing_settings": {}
  }
}


This is effectively what the PlexAPI library does for us
reddit.com
reddit.com
. Plex will respond with success if the invite was created (or an error if something went wrong, e.g. invalid token or the user is already invited). Our backend should handle any exceptions (for instance, catching a PlexAPI exception if the invite fails) and report back to the user accordingly. On success, we can render a confirmation page saying the invite was sent.

Additionally, the backend might log this event (e.g., append to a log file or database table: friend’s email, timestamp, result) for the admin’s records.

3. Admin Configuration Actions: For the admin panel, the backend will have routes like /admin (GET to show settings, POST to update settings). When the admin updates the library selections or other config, the backend saves these preferences. For example, if using a simple config file (YAML/JSON), it writes the new values; if using a database, it updates the relevant records. The admin may also trigger certain actions: e.g., a “Test Connection” button to verify the Plex token works (the backend can attempt a simple API call and return the status), or a “List Libraries” function to show available libraries (the backend can fetch plex_server.library.sections() and return names/IDs). These conveniences ensure the admin configured things correctly.

4. Handling Responses and Edge Cases: The backend must account for scenarios such as: the friend’s invite already exists or they are already a friend on Plex, the Plex server hitting the 100 user share limit, etc. If inviteFriend returns an error or raises an exception, we should catch it and show an error message on the form page (e.g., “Unable to send invite – please contact the server owner”). If the invite goes through, we simply confirm success. Plex does the heavy lifting from there (sending an email to the user with an invite link, as Plex normally would when you share a library). According to Plex’s official support, when you send an invite by email and the person doesn’t have an account, they’ll be prompted to create a Plex account when accepting the invitation
support.plex.tv
, so our app doesn’t need to worry about user account creation beyond sending the invite.

5. Email and Notifications: It’s worth noting that Plex itself handles notifying the user (via email or Plex app notification) once invited
support.plex.tv
support.plex.tv
. Our app doesn’t need to send emails to the friend; we trust Plex’s system. We could, however, customize the experience by showing the acceptance link directly on the success page (Plex gives a special acceptance URL after sending an invite
support.plex.tv
). In a manual invite, Plex shows the link which is same as what’s in the email. Potentially, we can retrieve that from the API (the Plex API might return the invite ID or URL). This could be a nice touch: after a successful invite, display “Click here to accept your invite now” linking to Plex’s accept URL, in case the email is delayed. This is an optional enhancement – initially, simply instructing the friend to check their email or Plex notifications is sufficient.

Security Considerations

Restricting Access to Invites: One concern is preventing random users from discovering the invite form and getting access to your Plex. If the app is hosted on the open internet, theoretically anyone who finds the URL could request an invite. While Plex limits sharing to 100 friends and is “intended for close friends”
support.plex.tv
, it’s wise to add some security. At minimum, we can implement a simple access code or password for the invite form. For example, the friend must also enter a pre-shared passphrase (given out by the server owner privately) to prove they are an authorized friend. Alternatively, we could require the friend to log in with their Plex account via OAuth (leveraging Plex’s SSO) before sending an invite, which is exactly what Wizarr’s SSO feature does
easypanel.io
. However, implementing Plex OAuth adds complexity; a simpler approach is a static invite code on the form or a unique URL per friend. Since the requirement “not at this phase” suggests we are keeping it simple for now, we may skip OAuth and instead could just keep the invite form URL unpublicized (shared manually with friends). In the future, integrating Plex OAuth login for invite requests would be ideal – then the app can automatically know the friend’s Plex username (since they logged in) and invite that account, skipping manual input.

Protecting the Admin Panel: The admin interface must be secured. We will enforce login protection for any admin routes. This can be done with a fixed username/password check in Flask (for example, using Flask-Login or a simple session after verifying credentials against config). Using HTTPS for accessing the admin panel (and the invite form) is important to protect the Plex token and any credentials in transit. The Plex token itself should never be exposed to the frontend; it stays on the server. We also ensure to follow Plex’s guidelines for token security: the token is like a password to the server
docs.wizarr.dev
, so our app won’t log it or send it to clients. If the token is ever compromised, the admin should regenerate it via Plex account settings
docs.wizarr.dev
.

Rate Limiting and Spam Prevention: If the invite form is public, someone could abuse it by sending many invites (potentially hitting Plex’s limit or spamming your server). We can add basic rate limiting – e.g., limit one invite request per IP per X minutes. Also, implementing a CAPTCHA on the invite form can deter automated abuse. Since this is for friends, even a simple question (“What’s the name of our shared hobby?”) could suffice as a check.

Error Handling & Logging: For transparency and debugging, the app should log actions and errors. If an invite fails or any exception occurs, it should be logged server-side so the admin can address it. The admin panel could even display these logs or at least a status indicator (e.g., “Plex API connection: OK” or “Invite last sent: 5 minutes ago to user@example.com”). Logging also helps in tracking how many invites have been sent and to whom, which is good for auditing access.

Future Enhancements (Beyond Current Phase)

While the initial design covers the basics, there are several enhancements we could plan for later, some of which mirror Wizarr’s advanced features:

Unique Invite Links: Instead of a general form, generate one-time invite URLs for specific people. For example, the admin could create an invite link that encodes a token; when the friend follows that link, it auto-fills their email (or uses the token to look up their intended identity) and triggers the invite. This approach (used by Wizarr) lets you more tightly control who can invite themselves (each link only works once)
easypanel.io
. It also feels seamless to the friend – they click a link and maybe just confirm their details to get access.

Tiered Access & Expiry: We could support the concept of invitation tiers or temporary access. For instance, a link that gives access only for 30 days, or links that correspond to different library sets (maybe “kids” tier that only shares the family-friendly library). Wizarr offers multi-tiered invitations with varying durations
easypanel.io
 – implementing this would require scheduling tasks to remove access after expiry (e.g., using a background scheduler or job queue, or leveraging Redis like Wizarr does for scheduled jobs
wizarr.org
wizarr.org
). This is more complex but useful if the server owner wants to periodically prune users or offer trials.

Integration with Request Tools: Many Plex admins use tools like Overseerr or Ombi for handling content requests. Our app could integrate a step to guide new users to those tools (Wizarr does this by showing instructions after invite
docs.wizarr.dev
easypanel.io
). We might, for example, include on the invite success page: “Here’s how to ask for new movies or shows...” with a link to the request app.

Discord or Community Integration: As a nicety, automatically inviting the user to a community Discord or forum once they join the server (Wizarr can invite to Discord servers too
easypanel.io
). This could be done via Discord webhooks or bots, but is clearly beyond the core scope.

Admin Notifications: Sending the admin an email or Discord message when someone uses the invite form could be helpful, so the admin knows who joined. This could be a simple email sent by our app or an entry in a Slack/Discord channel via webhook.

All these future enhancements would expand the system architecture (likely introducing background tasks, external APIs, user accounts, etc.), so we acknowledge them but will implement them in later phases. For now, our design focuses on immediate, automatic Plex invites via a web form, with basic configuration.

Conclusion

By combining the convenience of Wizarr’s invite automation with a tailored, lightweight Python implementation, we achieve an efficient solution for Plex library sharing. The planned web app will allow friends to request access and be instantly invited to the Plex server without manual steps, all through an easy web interface. We utilized Plex’s official API (via Python PlexAPI) to handle the heavy lifting of creating shares, as documented in Plex API references
reddit.com
. The design emphasizes simplicity, security, and compatibility: a minimal form-based UI that works on mobile browsers, a secure admin panel to control which content is shared, and safe storage of the Plex server credentials.

In summary, this technical design meets the requirements by providing: (1) a web-based, mobile-friendly invite form for friends, (2) automated backend logic in Python to send Plex invites to specified libraries, and (3) an admin interface for configuring the process. With this foundation in place, the Plex server owner can expand and customize the app in future iterations (adding features like unique invite links or SSO). This approach modernizes Plex sharing, making it as simple as sending a link or having a friend fill a form, to grant them instant access to your media
docs.wizarr.dev
, all while you retain control through the admin settings.

Sources: The design draws on Plex’s documented API capabilities for inviting friends
python-plexapi.readthedocs.io
reddit.com
 and takes inspiration from the open-source Wizarr project’s feature set
easypanel.io
, adapting those ideas into a Python web application context. The Plex support documentation confirms the invite flow (email invites and acceptance)
support.plex.tv
 which our app leverages. By researching these resources and following Plex’s best practices, we ensure the app will function reliably and align with Plex’s sharing mechanism.