#!/usr/bin/env python3
import asyncio
import aiosqlite

DB_NAME = "example.db"

async def async_fetch_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            users = await cursor.fetchall()
            return users  

async def async_fetch_older_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            older_users = await cursor.fetchall()
            return older_users  

async def fetch_concurrently():
    results = await asyncio.gather(
        async_fetch_users(),           
        async_fetch_older_users()
    )

    users, older_users = results

    for user in users:
        print(user)

    print()

    for user in older_users:
        print(user)

if __name__ == "__main__":
    asyncio.run(fetch_concurrently())  
