from fastapi import FastAPI

app = FastAPI()

@app.post("/receive-webhook")
async def receive_webhook(data: dict):
    print(f"Received webhook: {data}")
    return {"message": f"Webhook received"}
