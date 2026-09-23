from fastapi import FastAPI
from fastapi.responses import FileResponse
from osint_engine import run_scan

app = FastAPI()

# Serve the web interface
@app.get("/")
def serve_frontend():
    return FileResponse("index.html")

# API endpoint that the frontend will call
@app.get("/api/scan")
async def scan_target(username: str):
    results = await run_scan(username)
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)