import aiohttp
import random
import string
import time

API = "https://www.1secmail.com/api/v1/"

def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain = "1secmail.com"
    return f"{name}@{domain}", name, domain

async def fetch_messages(login, domain):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API}?action=getMessages&login={login}&domain={domain}") as resp:
            return await resp.json()

async def fetch_message_content(login, domain, message_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API}?action=readMessage&login={login}&domain={domain}&id={message_id}") as resp:
            return await resp.json()

async def get_otp_from_inbox(email):
    name, domain = email.split("@")
    for _ in range(10):  # Try for ~50 seconds
        messages = await fetch_messages(name, domain)
        for msg in messages:
            if "otp" in msg['subject'].lower() or "classplus" in msg['from'].lower():
                content = await fetch_message_content(name, domain, msg['id'])
                otp = ''.join(filter(str.isdigit, content.get("body", "")))
                if len(otp) >= 4:
                    return otp[:6]
        time.sleep(5)
    return None
