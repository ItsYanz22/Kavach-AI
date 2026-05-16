"""
KAVACH AI 2.0 - PRODUCTION-GRADE CYBERSECURITY LEARNING PLATFORM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next-generation backend for interactive scam detection & cyber awareness.

FEATURES:
✅ User authentication with JWT
✅ Learning platform with progress tracking
✅ Multi-agent orchestration (Infiltrator, Forensic, Mentor)
✅ Real-time WebSocket War Room simulations
✅ Fallback scenario engine (when LLM unavailable)
✅ Structured production logging
✅ Comprehensive error recovery
✅ Cloud Run optimized
✅ Anti-spam session management
✅ Achievement/XP system
✅ Debug endpoints for troubleshooting

ARCHITECTURE:
- Main app with lifecycle management
- Health checks & diagnostics
- Auth routers (signup, login, refresh)
- Learning routers (modules, progress, simulations)
- Debug/diagnostic routers
- WebSocket handler
- Static SPA serving
- Error middleware

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager
import asyncio
import json
import uuid
from datetime import datetime
from backend.auth.auth import TokenManager

# ────────────────────────────────────────────────────────────────────────────
# STEP 0: Setup Logging (First Priority)
# ────────────────────────────────────────────────────────────────────────────

from backend.logs_structured import setup_logging, get_logger, log_startup
from backend.config import EnvConfig

# Initialize logging
setup_logging(level=EnvConfig.LOG_LEVEL)
logger = get_logger(__name__)

logger.info("")
logger.info("=" * 80)
logger.info("🚀 KAVACH AI 2.0 - STARTUP SEQUENCE")
logger.info("=" * 80)
logger.info("")

# ────────────────────────────────────────────────────────────────────────────
# STEP 1: Load and Validate Configuration
# ────────────────────────────────────────────────────────────────────────────

try:
    logger.info("STEP 1: Loading configuration...")
    # EnvConfig already loaded on import
    is_valid, warnings = EnvConfig.validate_startup()
    
    for warning in warnings:
        logger.warning(f"  ⚠️  {warning}")
    
    log_startup("config", "ok")
except Exception as e:
    logger.error(f"❌ Configuration failed: {e}", exc_info=True)
    sys.exit(1)

# ────────────────────────────────────────────────────────────────────────────
# STEP 2: Initialize FastAPI
# ────────────────────────────────────────────────────────────────────────────

try:
    logger.info("STEP 2: Initializing FastAPI...")
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
    log_startup("fastapi", "ok")
except Exception as e:
    logger.error(f"❌ FastAPI initialization failed: {e}", exc_info=True)
    sys.exit(1)

# ────────────────────────────────────────────────────────────────────────────
# STEP 3: Initialize Database
# ────────────────────────────────────────────────────────────────────────────

try:
    logger.info("STEP 3: Initializing database...")
    from backend.database_models import init_db
    init_db()
    log_startup("database", "ok")
except Exception as e:
    logger.error(f"❌ Database initialization failed: {e}", exc_info=True)
    sys.exit(1)

# ────────────────────────────────────────────────────────────────────────────
# STEP 4: Import Backend Modules
# ────────────────────────────────────────────────────────────────────────────

try:
    logger.info("STEP 4: Loading backend modules...")
    
    from backend.schemas import ApiResponse
    logger.info("  ✓ schemas")
    
    from backend.services import agent_service
    logger.info("  ✓ services")
    
    from backend.websocket_manager import war_room_manager
    logger.info("  ✓ websocket_manager")
    
    from backend.fallback_scenarios import fallback_engine
    logger.info("  ✓ fallback_scenarios")
    
    log_startup("modules", "ok")
except Exception as e:
    logger.error(f"❌ Module import failed: {e}", exc_info=True)
    sys.exit(1)

# ────────────────────────────────────────────────────────────────────────────
# STEP 5: Import Routers
# ────────────────────────────────────────────────────────────────────────────

try:
    logger.info("STEP 5: Loading API routers...")
    
    from backend.routers.detection import router as detection_router
    logger.info("  ✓ detection router")
    
    from backend.routers.auth import router as auth_router
    logger.info("  ✓ auth router")
    
    from backend.routers.learning import router as learning_router
    logger.info("  ✓ learning router")
    
    from backend.routers.debug import router as debug_router
    logger.info("  ✓ debug router")
    
    log_startup("routers", "ok")
except Exception as e:
    logger.error(f"❌ Router import failed: {e}", exc_info=True)
    sys.exit(1)

# ────────────────────────────────────────────────────────────────────────────
# LIFECYCLE MANAGEMENT
# ────────────────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifecycle: startup → yield → shutdown"""
    
    # STARTUP
    logger.info("\n" + "=" * 80)
    logger.info("📌 STARTUP HOOKS")
    logger.info("=" * 80)
    
    try:
        logger.info("Starting WebSocket cleanup task...")
        war_room_manager.start_cleanup()
        logger.info("✅ WebSocket manager ready")
        
        logger.info("✅ All startup hooks completed")
        
        logger.info("=" * 80)
        logger.info("✅ KAVACH AI 2.0 IS READY TO SERVE")
        logger.info("=" * 80 + "\n")
    
    except Exception as e:
        logger.error(f"❌ Startup hook failed: {e}", exc_info=True)
        raise
    
    yield  # App runs here
    
    # SHUTDOWN
    logger.info("\n" + "=" * 80)
    logger.info("🛑 SHUTDOWN HOOKS")
    logger.info("=" * 80)
    
    try:
        logger.info("Stopping WebSocket cleanup task...")
        await war_room_manager.stop_cleanup()
        logger.info("✅ Cleanup complete")
    except Exception as e:
        logger.error(f"⚠️  Shutdown error: {e}")


# ────────────────────────────────────────────────────────────────────────────
# CREATE FASTAPI APP
# ────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Kavach AI 2.0 - Cyber Safety Learning Platform",
    description="Production-grade multi-agent backend for interactive scam education",
    version="2.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ────────────────────────────────────────────────────────────────────────────
# MIDDLEWARE
# ────────────────────────────────────────────────────────────────────────────

# CORS Configuration
# ────────────────────────────────────────────────────────────────────────────
# PRODUCTION DEPLOYMENT:
# - Cloud Run: Frontend and backend served from same origin → minimal CORS needed
# - Docker local: Set CORS_ORIGINS env var with comma-separated list
# - Direct network: Use regex for local IP ranges
#
# DEVELOPMENT:
# - Frontend runs on :5173 or :8080 via Vite dev server
# - Backend runs on :8000
# - Need CORS to allow cross-port requests
#
# SECURITY:
# - Never use allow_origins=["*"] with credentials=True (security risk)
# - In production, be explicit about allowed origins
# - Cloud Run: Use environment variable to set domain dynamically
#
# CORS Configuration
CORS_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Support production environment origins via env var
cors_env = os.environ.get("CORS_ORIGINS", "")
if cors_env:
    CORS_ORIGINS.extend([o.strip() for o in cors_env.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    # Support local network IPs via regex (essential for multiple dev environments)
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\..*|10\..*|172\.1[6-9]\..*|172\.2[0-9]\..*|172\.3[0-1]\..*):[0-9]+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600,
)

logger.info(f"✅ CORS configured with {len(CORS_ORIGINS)} origins")
if CORS_ORIGINS:
    for origin in CORS_ORIGINS:
        logger.info(f"   - {origin}")

# ────────────────────────────────────────────────────────────────────────────
# ROUTERS
# ────────────────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(learning_router)
app.include_router(detection_router)
app.include_router(debug_router)

# ────────────────────────────────────────────────────────────────────────────
# HEALTH CHECK
# ────────────────────────────────────────────────────────────────────────────


@app.get("/health")
async def health_check():
    """Liveness probe for Cloud Run."""
    return {
        "status": "healthy",
        "environment": EnvConfig.ENVIRONMENT,
        "ai_available": bool(EnvConfig.GROQ_API_KEY),
    }


@app.get("/ready")
async def readiness_check():
    """Readiness probe for Cloud Run."""
    try:
        # Check database
        from backend.database_models import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        # Check agents
        infiltrator_ready = agent_service.infiltrator.client is not None
        forensic_ready = agent_service.forensic.client is not None
        mentor_ready = agent_service.mentor.client is not None
        
        ready = (
            EnvConfig.GROQ_API_KEY is not None or
            fallback_engine is not None
        )
        
        return {
            "ready": ready,
            "database": "ok",
            "agents": {
                "infiltrator": "ready" if infiltrator_ready else "fallback",
                "forensic": "ready" if forensic_ready else "fallback",
                "mentor": "ready" if mentor_ready else "fallback",
            },
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


# ────────────────────────────────────────────────────────────────────────────
# WEBSOCKET WAR ROOM
# ────────────────────────────────────────────────────────────────────────────

@app.websocket("/ws/war-room")
async def websocket_war_room(websocket: WebSocket):
    """
    WebSocket handler for War Room interactive scam simulations.
    
    Features:
    - Real-time scenario generation
    - Anti-spam session control
    - Interactive Infiltrator agent
    - Error recovery with fallback
    - Automatic cleanup
    """
    
    session_id = str(uuid.uuid4())
    logger.info(f"[WS] New connection: {session_id}")
    
    try:
        # Connect session
        session = await war_room_manager.connect(session_id, websocket)
        
        # Welcome message
        await websocket.send_json({
            "event": "connected",
            "session_id": session_id,
            "message": "Welcome to War Room! Type 'start' to begin a scam scenario.",
        })
        
        logger.info(f"[WS] Session initialized: {session_id}")
        
        # Main message loop
        while True:
            try:
                # Receive user message
                user_input = await websocket.receive_text()
                
                # Parse input as JSON (WarRoom sends JSON objects)
                try:
                    data = json.loads(user_input)
                    user_message = data.get("message", "").strip().lower()
                    token = data.get("token")
                except json.JSONDecodeError:
                    user_message = user_input.strip().lower()
                    token = None
                
                logger.info(f"[WS] {session_id} → {user_message[:50]}")
                
                # START command
                if user_message == "start":
                    # Validate token if provided
                    if token:
                        try:
                            payload = TokenManager.verify_token(token)
                            session.user_id = payload.get("sub")
                        except Exception as e:
                            logger.warning(f"[WS] {session_id} provided invalid token: {e}")
                    
                    can_generate, reason = session.can_generate_new_scenario()
                    
                    if not can_generate:
                        await websocket.send_json({"error": reason})
                        continue
                    
                    try:
                        # Generate scenario (AI or fallback)
                        scenario = await agent_service.generate_scam_scenario()
                        session.start_scenario(scenario)
                        
                        await websocket.send_json({
                            "event": "scenario_start",
                            "scenario_id": f"scen_{session_id}_{int(datetime.utcnow().timestamp())}",
                            "sender": "Infiltrator",
                            "message": scenario.get("message"),
                            "amount": scenario.get("amount"),
                            "tip": scenario.get("tip"),
                            "scam_type": scenario.get("scenario_type"),
                            "risk_level": scenario.get("risk_level"),
                            "ui_title": scenario.get("ui_title"),
                            "ui_description": scenario.get("ui_description"),
                            "recommended_actions": scenario.get("recommended_actions", []),
                            "await_user_response": scenario.get("await_user_response", True),
                            "next_step": scenario.get("next_step")
                        })
                        
                        logger.info(f"[WS] {session_id}: Scenario started")
                    
                    except Exception as e:
                        logger.error(f"[WS] Scenario generation error: {e}")
                        # Send fallback
                        scenario = fallback_engine.generate_random_scenario()
                        session.start_scenario(scenario)
                        
                        await websocket.send_json({
                            "event": "scenario_start",
                            "sender": "Infiltrator",
                            "message": scenario.get("message"),
                            "scenario_type": scenario.get("scenario_type"),
                            "is_fallback": True,
                        })
                
                # User response to active scenario
                elif session.active_scenario:
                    try:
                        # Mark that user has responded to advance the state machine
                        session.record_user_response()
                        
                        next_message = await agent_service.continue_scenario(
                            session.active_scenario,
                            user_message
                        )
                        
                        await websocket.send_json({
                            "event": "scenario_continue",
                            "sender": "Infiltrator",
                            "message": next_message.get("message"),
                            "amount": next_message.get("amount"),
                            "tip": next_message.get("tip"),
                            "scam_type": next_message.get("scenario_type"),
                            "ui_title": next_message.get("ui_title"),
                            "ui_description": next_message.get("ui_description"),
                            "recommended_actions": next_message.get("recommended_actions", []),
                            "await_user_response": True,
                        })
                    
                    except Exception as e:
                        logger.error(f"[WS] Scenario error: {e}")
                        await websocket.send_json({"error": "Scenario error"})
                        session.resolve_scenario()
                
                else:
                    await websocket.send_json({
                        "message": "No active scenario. Type 'start' to begin."
                    })
            
            except WebSocketDisconnect:
                logger.info(f"[WS] Disconnected: {session_id}")
                break
            
            except Exception as e:
                logger.error(f"[WS] Error: {e}")
                try:
                    await websocket.send_json({"error": "Internal error"})
                except:
                    break
    
    finally:
        await war_room_manager.disconnect(session_id)
        logger.info(f"[WS] Cleaned up: {session_id}")


# ────────────────────────────────────────────────────────────────────────────
# STATIC FILE SERVING (Frontend SPA)
# ────────────────────────────────────────────────────────────────────────────

static_dir = Path(__file__).parent / "static"

if static_dir.exists():
    logger.info(f"✅ Production mode: Serving frontend from {static_dir}")
    
    # Mount assets (CSS, JS, Images)
    # We mount /assets specifically to avoid interference with /api
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    # SPA Fallback: Serve index.html for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Exclude API and WebSocket routes from fallback
        if full_path.startswith("api") or full_path.startswith("ws"):
            raise HTTPException(status_code=404, detail="API route not found")
        
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        
        return {"error": "Frontend build not found in static/"}

else:
    logger.warning(f"⚠️  Development mode: Static directory not found at {static_dir}")
    logger.info("   (This is normal if you are running frontend via 'npm run dev')")


# ────────────────────────────────────────────────────────────────────────────
# PRODUCTION STARTUP
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"\n🚀 Starting Uvicorn server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        timeout_keep_alive=30,
    )
