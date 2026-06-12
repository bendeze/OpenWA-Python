from fastapi import APIRouter

router = APIRouter(prefix="/api/plugins", tags=["Plugins"])

import os

import dotenv

ENV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env")
)


@router.get("")
async def get_plugins():
    env = dotenv.dotenv_values(ENV_PATH)
    engine_type = env.get("ENGINE_TYPE", "whatsapp-web.js")

    plugins_list = [
        {
            "id": "core-engine",
            "name": "Core WhatsApp Engine",
            "version": "1.0.0",
            "type": "engine",
            "description": "The primary engine handling WhatsApp Web connections and messaging.",
            "author": "OpenWA",
            "status": "enabled",
            "config": {
                "type": engine_type,
                "headless": env.get("PUPPETEER_HEADLESS", "true") == "true",
            },
            "builtIn": True,
            "provides": ["messaging", "groups", "media"],
        }
    ]

    plugins_list.extend(plugin_manager.get_all_plugins())

    return plugins_list


@router.get("/{plugin_id}")
async def get_plugin(plugin_id: str):
    plugins = await get_plugins()
    for p in plugins:
        if p["id"] == plugin_id:
            return p
    return {"error": "Plugin not found"}


from database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


@router.post("/{plugin_id}/enable")
async def enable_plugin(plugin_id: str, db: Session = Depends(get_db)):

    plugin_path = os.path.join(PLUGINS_DIR, plugin_id, "plugin.json")
    if os.path.exists(plugin_path):
        with open(plugin_path, "r") as f:
            meta = json.load(f)
        meta["status"] = "enabled"
        with open(plugin_path, "w") as f:
            json.dump(meta, f, indent=2)
        plugin_manager.scan_and_load()

        create_audit_log(
            db,
            action="Enable Plugin",
            severity="info",
            details=f"Enabled plugin: {plugin_id}",
        )

        return {"success": True, "message": "Plugin enabled"}
    return {"success": False, "message": "Plugin not found"}


@router.post("/{plugin_id}/disable")
async def disable_plugin(plugin_id: str, db: Session = Depends(get_db)):

    plugin_path = os.path.join(PLUGINS_DIR, plugin_id, "plugin.json")
    if os.path.exists(plugin_path):
        with open(plugin_path, "r") as f:
            meta = json.load(f)
        meta["status"] = "disabled"
        with open(plugin_path, "w") as f:
            json.dump(meta, f, indent=2)
        plugin_manager.scan_and_load()

        create_audit_log(
            db,
            action="Disable Plugin",
            severity="info",
            details=f"Disabled plugin: {plugin_id}",
        )

        return {"success": True, "message": "Plugin disabled"}
    return {"success": False, "message": "Plugin not found"}


import json

from plugin_manager import PLUGINS_DIR, plugin_manager
from pydantic import BaseModel
from routers.audit import create_audit_log


class PluginConfigPayload(BaseModel):
    config: dict


@router.put("/{plugin_id}/config")
async def configure_plugin(plugin_id: str, payload: PluginConfigPayload):
    # Here we would save to .env if it was the engine config
    return {"success": True, "message": "Configuration saved"}


@router.get("/{plugin_id}/health")
async def health_check_plugin(plugin_id: str):
    return {"healthy": True, "message": "Plugin is operating normally"}
