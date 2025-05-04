# utils/jitsi.py - Optional utility file for advanced Jitsi features
import jwt
from datetime import datetime, timedelta
from django.conf import settings

class JitsiManager:
    @staticmethod
    def generate_meeting_link(room_name, user, moderator=False):
        """
        Generate a Jitsi meeting link with JWT authentication
        """
        if not room_name:
            raise ValueError("Room name is required")
            
        payload = {
            'context': {
                'user': {
                    'id': user.id,
                    'name': user.get_full_name(),
                    'email': user.email,
                }
            },
            'aud': 'jitsi',
            'iss': settings.JITSI_APP_ID,
            'sub': settings.JITSI_DOMAIN,
            'room': room_name,
            'exp': datetime.utcnow() + timedelta(hours=3),
            'moderator': moderator,
        }
        
        token = jwt.encode(payload, settings.JITSI_APP_SECRET, algorithm='HS256')
        
        return (
            f"https://{settings.JITSI_DOMAIN}/{room_name}"
            f"?jwt={token}"
            f"#userInfo.displayName={user.get_full_name()}"
            f"&config.prejoinPageEnabled=false"
        )
    
    @staticmethod
    def validate_jitsi_room(room_name, user):
        """
        Validate if a user has access to a Jitsi room
        """
        try:
            appointment = AppointmentRequest.objects.get(
                Q(jitsi_room_name=room_name),
                Q(athlete=user) | Q(specialist=user)
            )
            return appointment
        except AppointmentRequest.DoesNotExist:
            return None