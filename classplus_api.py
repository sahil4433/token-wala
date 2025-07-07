
import aiohttp

BASE_URL = "https://api.classplusapp.com"

async def request_otp(email):
    async with aiohttp.ClientSession() as session:
        payload = {
            "email": email,
            "isNewApp": True,
            "userType": 1
        }
        headers = {
            "x-access-token": "",
            "x-client-id": "COACHING",
            "x-version": "1.4.36.1",
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        async with session.post(f"{BASE_URL}/v2/customer/auth/sendOtp", json=payload, headers=headers) as resp:
            return await resp.json()

async def verify_otp(email, otp):
    async with aiohttp.ClientSession() as session:
        payload = {
            "email": email,
            "otp": otp,
            "isNewApp": True,
            "userType": 1
        }
        headers = {
            "x-access-token": "",
            "x-client-id": "COACHING",
            "x-version": "1.4.36.1",
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        async with session.post(f"{BASE_URL}/v2/customer/auth/verifyOtp", json=payload, headers=headers) as resp:
            data = await resp.json()
            return data.get("data", {}).get("accessToken")
