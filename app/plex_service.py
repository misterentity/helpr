from plexapi.myplex import MyPlexAccount
from plexapi.exceptions import BadRequest, Unauthorized, NotFound
import logging
from config import Config

logger = logging.getLogger(__name__)

class PlexService:
    """Service class for Plex API operations."""
    
    def __init__(self):
        self.account = None
        self.server = None
    
    def _ensure_connected(self):
        """Ensure connection is established, reconnect only if necessary."""
        if self.account is None or self.server is None:
            self.connect_to_plex()
    
    def connect_to_plex(self):
        """Establish connection to Plex server using token and server name."""
        try:
            self.account = MyPlexAccount(token=Config.PLEX_TOKEN)
            self.server = self.account.resource(Config.PLEX_SERVER_NAME).connect()
            logger.info(f"Successfully connected to Plex server: {Config.PLEX_SERVER_NAME}")
            return True
        except Unauthorized:
            logger.error("Invalid Plex token")
            raise ValueError("Invalid Plex token. Please check your PLEX_TOKEN configuration.")
        except NotFound:
            logger.error(f"Plex server not found: {Config.PLEX_SERVER_NAME}")
            raise ValueError(f"Plex server '{Config.PLEX_SERVER_NAME}' not found. Please check your PLEX_SERVER_NAME configuration.")
        except Exception as e:
            logger.error(f"Error connecting to Plex: {str(e)}")
            raise ValueError(f"Error connecting to Plex: {str(e)}")
    
    def get_libraries(self):
        """Fetch available library sections from the Plex server."""
        self._ensure_connected()
        
        try:
            sections = self.server.library.sections()
            libraries = [{'title': section.title, 'type': section.type} for section in sections]
            logger.info(f"Retrieved {len(libraries)} libraries from Plex")
            return libraries
        except Exception as e:
            logger.error(f"Error fetching libraries: {str(e)}")
            raise ValueError(f"Error fetching libraries: {str(e)}")
    
    def send_invite(self, email_or_username, library_names, allow_downloads=False):
        """Send a Plex invite to the specified user with selected libraries."""
        self._ensure_connected()
        
        try:
            # Get library sections to share
            sections = []
            if library_names:
                all_sections = self.server.library.sections()
                sections = [section for section in all_sections if section.title in library_names]
            
            # Set sections to None if empty to avoid API issues
            sections_arg = sections if sections else None
            
            # Send the invite
            self.account.inviteFriend(
                user=email_or_username,
                server=self.server,
                sections=sections_arg,
                allowSync=allow_downloads,
                allowCameraUpload=False,
                allowChannels=False,
                filterMovies=None,
                filterTelevision=None,
                filterMusic=None
            )
            
            logger.info(f"Successfully sent invite to {email_or_username} with {len(sections)} libraries (downloads: {allow_downloads})")
            return True
            
        except BadRequest as e:
            error_msg = str(e)
            if "already has access" in error_msg.lower() or "already invited" in error_msg.lower():
                logger.warning(f"User {email_or_username} already has access or is already invited")
                raise ValueError(f"User '{email_or_username}' already has access or has already been invited.")
            else:
                logger.error(f"Bad request when inviting {email_or_username}: {error_msg}")
                raise ValueError(f"Invalid request: {error_msg}")
        except NotFound:
            logger.error(f"User not found: {email_or_username}")
            raise ValueError(f"Plex user '{email_or_username}' not found. Please ensure the username or email is correct.")
        except Exception as e:
            logger.error(f"Error sending invite to {email_or_username}: {str(e)}")
            raise ValueError(f"Error sending invite: {str(e)}")
    
    def send_invite_with_tier(self, email_or_username, tier):
        """Send a Plex invite with tier-specific settings."""
        library_names = tier.library_names if tier.library_names else []
        allow_downloads = tier.allow_downloads
        return self.send_invite(email_or_username, library_names, allow_downloads)
    
    def revoke_access(self, email_or_username):
        """Revoke a user's access to the Plex server."""
        self._ensure_connected()
        
        try:
            # Remove the user as a friend, which revokes their access
            self.account.removeFriend(user=email_or_username)
            logger.info(f"Successfully revoked access for {email_or_username}")
            return True
        except NotFound:
            logger.warning(f"User {email_or_username} not found when trying to revoke access")
            # User doesn't exist, so technically access is "revoked"
            return True
        except Exception as e:
            logger.error(f"Error revoking access for {email_or_username}: {str(e)}")
            raise ValueError(f"Error revoking access: {str(e)}")
    
    def update_user_permissions(self, email_or_username, library_names, allow_downloads):
        """Update an existing user's permissions (requires remove and re-invite)."""
        self._ensure_connected()
        
        try:
            # First, try to update (may not be supported by PlexAPI directly)
            # If not possible, we need to remove and re-invite
            logger.info(f"Updating permissions for {email_or_username}")
            
            # Get library sections to share
            sections = []
            if library_names:
                all_sections = self.server.library.sections()
                sections = [section for section in all_sections if section.title in library_names]
            
            sections_arg = sections if sections else None
            
            # Try to update friend permissions
            # Note: PlexAPI may require removing and re-inviting
            self.account.updateFriend(
                user=email_or_username,
                server=self.server,
                sections=sections_arg,
                allowSync=allow_downloads
            )
            
            logger.info(f"Successfully updated permissions for {email_or_username}")
            return True
        except AttributeError:
            # updateFriend may not exist, fall back to remove and re-invite
            logger.warning(f"updateFriend not available, removing and re-inviting {email_or_username}")
            try:
                self.revoke_access(email_or_username)
                self.send_invite(email_or_username, library_names, allow_downloads)
                return True
            except Exception as e:
                logger.error(f"Error updating permissions via remove/re-invite: {str(e)}")
                raise ValueError(f"Error updating permissions: {str(e)}")
        except Exception as e:
            logger.error(f"Error updating permissions for {email_or_username}: {str(e)}")
            raise ValueError(f"Error updating permissions: {str(e)}")
    
    def test_connection(self):
        """Test the Plex connection and return status."""
        try:
            self._ensure_connected()
            libraries = self.get_libraries()
            return {
                'success': True,
                'server_name': Config.PLEX_SERVER_NAME,
                'library_count': len(libraries),
                'message': f"Successfully connected to {Config.PLEX_SERVER_NAME}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Connection failed: {str(e)}"
            }

# Global instance
plex_service = PlexService()

