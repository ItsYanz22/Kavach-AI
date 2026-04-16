import os
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# Trigger Uvicorn Hot-Reload: true

from agents.agent_manager import AgentManager
from schemas import MessageInput
from database import log_detection, get_history

app = FastAPI(
    title="Kavach AI – Cyber Safety Simulator",
    description="Backend API for the Kavach AI Cyber-Safety Ecosystem",
    version="1.0.0",
)

# ──────────────────────────────────────────────
# CORS – allow frontend requests from any origin
# ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Initialize AI Agents
# ──────────────────────────────────────────────
infiltrator = AgentManager("Infiltrator")
forensic = AgentManager("Forensic")
mentor = AgentManager("Mentor")


# ──────────────────────────────────────────────
# Helper – standardised API envelope
# ──────────────────────────────────────────────
def api_response(success: bool, data: dict, message: str = ""):
    return {"success": success, "data": data, "message": message}


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────


@app.get("/health")
def health():
    return api_response(True, {"status": "ok"}, "Server healthy")


# 🔍 DETECT – Forensic Agent classifies a message
@app.post("/detect")
def detect(data: MessageInput):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        prompt = (
            "Classify the following message as SCAM or SAFE.\n"
            "Return ONLY a valid JSON object with the exact schema below, NO markdown formatting, NO backticks:\n"
            "{\n"
            "  \"classification\": \"Scam\" or \"Safe\",\n"
            "  \"confidence\": 0.95,\n"
            "  \"reason\": \"summary\"\n"
            "}\n"
            f"Message:\n{data.text}"
        )
        result = forensic.send_message(prompt)

        if "System Alert: LLM Rate Limit Reached" in result:
            raise HTTPException(status_code=429, detail="LLM Rate Limit Reached. Please restart the backend server so it reads the new .env key.")

        import json
        start = result.find('{')
        end = result.rfind('}')
        if start != -1 and end != -1:
            clean_res = result[start:end+1]
        else:
            clean_res = result
        
        try:
            res_json = json.loads(clean_res)
            classification = res_json.get("classification", "Suspicious")
            confidence = float(res_json.get("confidence", 0.5))
            reason = res_json.get("reason", "Analyzed by AI")
        except json.JSONDecodeError:
            classification, confidence, reason = "Suspicious", 0.5, "Format error or fallback logic"

        log_detection(data.text, classification, confidence)
        
        # NOTE: map back to uppercase so we don't break old frontend if it relied on it
        upper_class = "SCAM" if "scam" in classification.lower() else "SAFE"

        return api_response(True, {
            "classification": upper_class,
            "confidence": confidence,
            "reason": reason,
        })

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.post("/explain")
def explain(data: MessageInput):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        # Request the structured JSON response for the frontend UI
        prompt = (
            f"Analyze the following scam message in deep detail.\n"
            f"Message: {data.text}\n\n"
            f"Return ONLY a valid JSON object matching this schema exactly (no markdown formatting, no backticks):\n"
            "{\n"
            '  "message_parts": [\n'
            '    { "text": "plain text part ", "highlight_index": null },\n'
            '    { "text": "highlighted part", "highlight_index": 0 }\n'
            "  ],\n"
            '  "highlights": [\n'
            "    {\n"
            '      "label": "Tactic Name (e.g. Suspicious Link)",\n'
            '      "color": "danger" or "warning" or "cyber",\n'
            '      "icon": "Link" or "Clock" or "Building" or "AlertTriangle",\n'
            '      "tooltip": "Why this is suspicious",\n'
            '      "text": "The exact text being highlighted"\n'
            "    }\n"
            "  ],\n"
            '  "reasons": [\n'
            '    "Detailed reason 1", "Detailed reason 2"\n'
            "  ]\n"
            "}\n"
            "CRITICAL: The concatenated 'text' fields in 'message_parts' MUST recreate the original message EXACTLY. highlight_index must perfectly correspond to the highlights array indices."
        )
        result = forensic.send_message(prompt)
        
        import json
        start = result.find('{')
        end = result.rfind('}')
        if start != -1 and end != -1:
            clean_res = result[start:end+1]
        else:
            clean_res = result
        
        return api_response(True, json.loads(clean_res))

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Explain failed: {str(e)}")


# 🛡️ ACTION – Mentor Agent recommends steps
@app.post("/action")
def action(data: MessageInput):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        result = mentor.send_message(
            f"What should the user do about this message? Provide a numbered "
            f"list of recommended actions:\n{data.text}"
        )
        return api_response(True, {"actions": result})

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Action failed: {str(e)}")


# 🎭 SIMULATE – Infiltrator Agent generates a scam message
@app.post("/simulate")
def simulate():
    try:
        result = infiltrator.send_message(
            "Generate a realistic Indian scam message such as a UPI fraud, "
            "OTP phishing, digital arrest, or fake lottery. Make it convincing "
            "but use only placeholder links like safesim.link/example."
        )
        return api_response(True, {"message": result})

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


# 📜 HISTORY – past detections
@app.get("/history")
def history():
    try:
        rows = get_history()
        entries = [
            {
                "id": r[0],
                "message": r[1],
                "classification": r[2],
                "confidence": r[3],
                "timestamp": r[4],
            }
            for r in rows
        ]
        return api_response(True, {"history": entries})

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"History failed: {str(e)}")


# ──────────────────────────────────────────────
# 🏥 HEALTH SCORE – Mentor Agent evaluates session
# ──────────────────────────────────────────────
@app.get("/health-score")
def health_score():
    try:
        prompt = (
            "Evaluate the current session's overall security health. "
            "Return ONLY a valid JSON object with the exact schema below, NO markdown formatting, NO backticks:\n"
            "{\n"
            "  \"score\": 85,\n"
            "  \"alerts\": [\n"
            "    {\"time\": \"Just now\", \"text\": \"Simulation finished\", \"type\": \"safe\"}\n"
            "  ]\n"
            "}\n"
            "Make sure 'type' is one of 'safe', 'warning', or 'danger'."
        )
        result = mentor.send_message(prompt)
        import json
        clean_res = result.strip()
        if clean_res.startswith("```json"): clean_res = clean_res[7:]
        if clean_res.startswith("```"): clean_res = clean_res[3:]
        if clean_res.endswith("```"): clean_res = clean_res[:-3]
        
        return api_response(True, json.loads(clean_res.strip()))
    except Exception as e:
        traceback.print_exc()
        return api_response(True, {"score": 78, "alerts": [{"time": "System", "text": "Fallback score (Mentor error)", "type": "warning"}]})


from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

manager = ConnectionManager()

@app.websocket("/ws/war-room")
async def websocket_war_room(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        import json
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                user_msg = payload.get("message", "")
                
                # Append a hidden instruction so the LLM outputs JSON
                prompt = (
                    f"{user_msg}\n\n"
                    "Please respond with BOTH the visible chat message AND some metadata about the scenario in JSON format. "
                    "VARY the scam scenarios you generate widely (e.g. use phishing links, fake package deliveries, digital arrest threats, electricity disconnection). "
                    "Make sure the response strictly follows this JSON schema, NO markdown, NO backticks:\n"
                    "{\n"
                    '  "text": "The actual message text to send to the user",\n'
                    '  "amount": 12500,\n'
                    '  "tip": "A short, helpful tip explaining why this is a scam",\n'
                    '  "scam_type": "A brief name for the scenario e.g. Package Scam"\n'
                    "}"
                )
                agent_reply = infiltrator.send_message(prompt)
                
                start = agent_reply.find('{')
                end = agent_reply.rfind('}')
                if start != -1 and end != -1:
                    clean_res = agent_reply[start:end+1]
                else:
                    clean_res = agent_reply
                
                try:
                    res_json = json.loads(clean_res)
                    await websocket.send_json({
                        "sender": "Infiltrator",
                        "message": res_json.get("text", "Error parsing message"),
                        "amount": res_json.get("amount", 2847),
                        "tip": res_json.get("tip", "Be cautious with unknown messages."),
                        "scam_type": res_json.get("scam_type", "Unknown Scam")
                    })
                except Exception:
                    # Fallback if json parsing fails
                    await websocket.send_json({
                        "sender": "Infiltrator",
                        "message": agent_reply,
                        "amount": 2847,
                        "tip": "Real utility companies never threaten immediate disconnection via SMS.",
                        "scam_type": "Electricity Disconnection"
                    })
            except Exception:
                await websocket.send_json({"error": "Failed to process message."})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ──────────────────────────────────────────────
# Serve built frontend in production (Cloud Run)
# ──────────────────────────────────────────────
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

# ──────────────────────────────────────────────
# Run with:  uvicorn main:app --host 0.0.0.0 --port 8000
# Or:        python main.py
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)