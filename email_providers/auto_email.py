from .one_sec_mail import generate_random_email, get_otp_from_inbox

temp_email_map = {}

async def generate_temp_email_and_fetch_otp(action, email=None):
    if action == "init":
        temp_email, _, _ = generate_random_email()
        temp_email_map[temp_email] = True
        return temp_email
    elif action == "fetch" and email in temp_email_map:
        return await get_otp_from_inbox(email)
    return None
