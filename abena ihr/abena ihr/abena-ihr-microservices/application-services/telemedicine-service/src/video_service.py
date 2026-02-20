from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import logging
from dataclasses import dataclass

app = FastAPI(title="Telemedicine Video Service")

class VideoQuality(str, Enum):
    LOW = "low"      # 480p
    MEDIUM = "medium"  # 720p
    HIGH = "high"    # 1080p
    ULTRA = "ultra"  # 4K

class RecordingStatus(str, Enum):
    NOT_RECORDING = "not_recording"
    RECORDING = "recording"
    PAUSED = "paused"
    STOPPED = "stopped"

class VideoSession(BaseModel):
    id: str
    consultation_id: str
    patient_id: str
    provider_id: str
    status: str
    quality: VideoQuality
    recording_status: RecordingStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    recording_url: Optional[str] = None
    metadata: Dict[str, Any] = {}

@dataclass
class WebRTCConnection:
    session_id: str
    patient_connection: Optional[WebSocket] = None
    provider_connection: Optional[WebSocket] = None
    ice_candidates: List[Dict] = None
    sdp_offers: Dict[str, str] = None

class VideoService:
    def __init__(self):
        self.active_sessions: Dict[str, VideoSession] = {}
        self.webrtc_connections: Dict[str, WebRTCConnection] = {}
        self.recording_sessions: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)

    def create_video_session(self, consultation_id: str, patient_id: str, 
                           provider_id: str, quality: VideoQuality = VideoQuality.MEDIUM) -> VideoSession:
        session_id = str(uuid.uuid4())
        
        session = VideoSession(
            id=session_id,
            consultation_id=consultation_id,
            patient_id=patient_id,
            provider_id=provider_id,
            status="created",
            quality=quality,
            recording_status=RecordingStatus.NOT_RECORDING,
            metadata={
                "created_at": datetime.now().isoformat(),
                "quality_settings": self._get_quality_settings(quality)
            }
        )
        
        self.active_sessions[session_id] = session
        self.webrtc_connections[session_id] = WebRTCConnection(
            session_id=session_id,
            ice_candidates=[],
            sdp_offers={}
        )
        
        return session

    def _get_quality_settings(self, quality: VideoQuality) -> Dict[str, Any]:
        settings = {
            VideoQuality.LOW: {
                "width": 854,
                "height": 480,
                "bitrate": 500000,
                "framerate": 24
            },
            VideoQuality.MEDIUM: {
                "width": 1280,
                "height": 720,
                "bitrate": 1500000,
                "framerate": 30
            },
            VideoQuality.HIGH: {
                "width": 1920,
                "height": 1080,
                "bitrate": 3000000,
                "framerate": 30
            },
            VideoQuality.ULTRA: {
                "width": 3840,
                "height": 2160,
                "bitrate": 8000000,
                "framerate": 30
            }
        }
        return settings[quality]

    def start_session(self, session_id: str) -> VideoSession:
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session.status = "active"
        session.start_time = datetime.now()
        
        self.logger.info(f"Video session {session_id} started")
        return session

    def end_session(self, session_id: str) -> VideoSession:
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session.status = "ended"
        session.end_time = datetime.now()
        
        # Stop recording if active
        if session.recording_status == RecordingStatus.RECORDING:
            self.stop_recording(session_id)
        
        # Clean up WebRTC connections
        if session_id in self.webrtc_connections:
            del self.webrtc_connections[session_id]
        
        self.logger.info(f"Video session {session_id} ended")
        return session

    def start_recording(self, session_id: str) -> VideoSession:
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        if session.status != "active":
            raise ValueError("Can only record active sessions")
        
        session.recording_status = RecordingStatus.RECORDING
        recording_id = str(uuid.uuid4())
        
        self.recording_sessions[session_id] = {
            "recording_id": recording_id,
            "start_time": datetime.now(),
            "file_path": f"/recordings/{recording_id}.webm"
        }
        
        self.logger.info(f"Recording started for session {session_id}")
        return session

    def stop_recording(self, session_id: str) -> VideoSession:
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session.recording_status = RecordingStatus.STOPPED
        
        if session_id in self.recording_sessions:
            recording_info = self.recording_sessions[session_id]
            recording_info["end_time"] = datetime.now()
            session.recording_url = recording_info["file_path"]
            del self.recording_sessions[session_id]
        
        self.logger.info(f"Recording stopped for session {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[VideoSession]:
        return self.active_sessions.get(session_id)

    def get_active_sessions(self) -> List[VideoSession]:
        return [session for session in self.active_sessions.values() 
                if session.status == "active"]

    def update_quality(self, session_id: str, quality: VideoQuality) -> VideoSession:
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session.quality = quality
        session.metadata["quality_settings"] = self._get_quality_settings(quality)
        
        return session

video_service = VideoService()

@app.post("/sessions")
async def create_video_session(session_data: Dict[str, Any]):
    try:
        session = video_service.create_video_session(
            consultation_id=session_data["consultation_id"],
            patient_id=session_data["patient_id"],
            provider_id=session_data["provider_id"],
            quality=VideoQuality(session_data.get("quality", "medium"))
        )
        return {"session": session}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/sessions/{session_id}/start")
async def start_video_session(session_id: str):
    try:
        session = video_service.start_session(session_id)
        return {"session": session}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/sessions/{session_id}/end")
async def end_video_session(session_id: str):
    try:
        session = video_service.end_session(session_id)
        return {"session": session}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/sessions/{session_id}/recording/start")
async def start_recording(session_id: str):
    try:
        session = video_service.start_recording(session_id)
        return {"session": session}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/sessions/{session_id}/recording/stop")
async def stop_recording(session_id: str):
    try:
        session = video_service.stop_recording(session_id)
        return {"session": session}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = video_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session": session}

@app.get("/sessions")
async def get_active_sessions():
    sessions = video_service.get_active_sessions()
    return {"sessions": sessions}

@app.put("/sessions/{session_id}/quality")
async def update_quality(session_id: str, quality: VideoQuality):
    try:
        session = video_service.update_quality(session_id, quality)
        return {"session": session}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# WebSocket endpoint for WebRTC signaling
@app.websocket("/ws/{session_id}/{participant_type}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, participant_type: str):
    await websocket.accept()
    
    if session_id not in video_service.webrtc_connections:
        await websocket.close(code=4004, reason="Session not found")
        return
    
    connection = video_service.webrtc_connections[session_id]
    
    # Assign connection based on participant type
    if participant_type == "patient":
        connection.patient_connection = websocket
    elif participant_type == "provider":
        connection.provider_connection = websocket
    else:
        await websocket.close(code=4000, reason="Invalid participant type")
        return
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle WebRTC signaling
            if message["type"] == "offer":
                connection.sdp_offers[participant_type] = message["sdp"]
                # Forward to other participant
                target_ws = connection.provider_connection if participant_type == "patient" else connection.patient_connection
                if target_ws:
                    await target_ws.send_text(json.dumps({
                        "type": "offer",
                        "sdp": message["sdp"],
                        "from": participant_type
                    }))
            
            elif message["type"] == "answer":
                target_ws = connection.provider_connection if participant_type == "patient" else connection.patient_connection
                if target_ws:
                    await target_ws.send_text(json.dumps({
                        "type": "answer",
                        "sdp": message["sdp"],
                        "from": participant_type
                    }))
            
            elif message["type"] == "ice-candidate":
                connection.ice_candidates.append({
                    "candidate": message["candidate"],
                    "from": participant_type
                })
                # Forward to other participant
                target_ws = connection.provider_connection if participant_type == "patient" else connection.patient_connection
                if target_ws:
                    await target_ws.send_text(json.dumps({
                        "type": "ice-candidate",
                        "candidate": message["candidate"],
                        "from": participant_type
                    }))
    
    except WebSocketDisconnect:
        # Clean up connection
        if participant_type == "patient":
            connection.patient_connection = None
        else:
            connection.provider_connection = None
        
        video_service.logger.info(f"WebSocket disconnected for {participant_type} in session {session_id}") 