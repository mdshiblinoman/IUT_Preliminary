import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # 1. register org and admin
        resp = await client.post("http://localhost:8000/auth/register", json={
            "org_name": "test_org", "username": "admin", "password": "pw"
        })
        print("register admin", resp.status_code, resp.text)
        
        # 2. register member
        resp = await client.post("http://localhost:8000/auth/register", json={
            "org_name": "test_org", "username": "user2", "password": "pw"
        })
        print("register member", resp.status_code, resp.text)
        
        # 3. login admin
        resp = await client.post("http://localhost:8000/auth/login", json={
            "org_name": "test_org", "username": "admin", "password": "pw"
        })
        admin_token = resp.json()["access_token"]
        
        # 4. login member
        resp = await client.post("http://localhost:8000/auth/login", json={
            "org_name": "test_org", "username": "user2", "password": "pw"
        })
        member_token = resp.json()["access_token"]
        
        # 5. create room
        resp = await client.post("http://localhost:8000/rooms", json={
            "name": "Room 1", "capacity": 10, "hourly_rate_cents": 1000
        }, headers={"Authorization": f"Bearer {admin_token}"})
        room_id = resp.json()["id"]
        
        # 6. Concurrent booking same room, same time, DIFFERENT users
        async def book(token):
            return await client.post("http://localhost:8000/bookings", json={
                "room_id": room_id,
                "start_time": "2030-01-01T10:00:00Z",
                "end_time": "2030-01-01T11:00:00Z"
            }, headers={"Authorization": f"Bearer {token}"})
            
        results = await asyncio.gather(book(admin_token), book(member_token))
        for r in results:
            print("booking result", r.status_code, r.text)

asyncio.run(main())
