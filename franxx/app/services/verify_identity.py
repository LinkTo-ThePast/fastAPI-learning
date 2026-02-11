from app.config.settings import get_settings

class VerificationError(Exception):
	"""Whatsapp number is required when channel verification is external"""
	pass


async def verify_identity(photo_user: bytes, whatsapp_number: str) -> bool:
    """"""
    # 1. verify white list
    settings = get_settings()
    
    if not whatsapp_number:
        raise VerificationError("Whatsapp number is required when channel verification is external!")
    
    
    return True