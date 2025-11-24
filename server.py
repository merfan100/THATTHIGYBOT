import asyncio
from flask import Flask
import nest_asyncio
import test2

nest_asyncio.apply()

app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot is running!"

async def run_flask():
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = ["0.0.0.0:10000"]
    await serve(app_web, config)

async def main():
    bot_task = asyncio.create_task(test2.main())
    flask_task = asyncio.create_task(run_flask())
    await asyncio.gather(bot_task, flask_task)

if __name__ == "__main__":
    asyncio.run(main())