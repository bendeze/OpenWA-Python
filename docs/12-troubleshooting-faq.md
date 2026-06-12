# 12 - Troubleshooting FAQ

This document outlines common issues when running the Hybrid OpenWA stack.

## General Issues

### Q: "ModuleNotFoundError: No module named 'schemas'"
**Cause:** You are running the python script directly without activating the virtual environment, or you are running the script from the wrong directory.
**Fix:** Always ensure you are inside the `api-gateway` folder and your virtual environment is active.
```bash
cd api-gateway
source venv/bin/activate
uvicorn main:app
```

### Q: "Redis ConnectionError"
**Cause:** Either the FastAPI Gateway or the Node Worker cannot connect to the Redis bus.
**Fix:** Ensure your Redis server is running locally on `localhost:6379`. If using Docker Compose, ensure both `.env` files point to `redis://redis:6379`.

## WA Worker Issues

### Q: Worker crashes immediately with "Failed to launch the browser process"
**Cause:** Puppeteer requires many native Linux libraries (like `libnss3`, `libatk1.0-0`, etc.) that might not be installed on your host OS or lightweight docker image.
**Fix:** Install the missing dependencies. On Debian/Ubuntu:
```bash
sudo apt-get install -yq gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget
```

### Q: "TimeoutError" when calling `client.messages.send_text()`
**Cause:** The FastAPI Gateway dispatched the RPC command to Redis, but the Node worker never responded within the 60 second timeout.
**Fix:** 
1. Check if `wa-worker` is actually running and connected to Redis.
2. Check the `wa-worker` console logs to see if Puppeteer is hung or if the WhatsApp session disconnected ungracefully.

### Q: QR Code won't scan or expires too fast
**Cause:** The WhatsApp multi-device beta refreshes QR codes rapidly.
**Fix:** Ensure you are calling `/api/sessions/{id}/qr` frequently via polling in your frontend interface until the status flips to `authenticated`.
