"""
Tests for Phase 7 Voice Interaction Module.
Validates voice capabilities discovery, text-to-speech audio synthesis,
and speech-to-text audio transcription endpoints.
"""
import sys
import os
import io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app
from app.services.voice_service import get_voice_service

client = TestClient(app)


def test_voice_capabilities():
    """Verify voice service capabilities, providers, and voices are reported."""
    res = client.get("/api/v1/voice/capabilities")
    assert res.status_code == 200
    data = res.json()
    assert "tts_engine" in data
    assert "stt_engine" in data
    assert "available_voices" in data
    assert isinstance(data["available_voices"], list)
    voice_ids = [v["id"] for v in data["available_voices"]]
    assert "alloy" in voice_ids
    assert "nova" in voice_ids


def test_voice_speak_endpoint():
    """Verify POST /api/v1/voice/speak generates valid audio stream."""
    res = client.post("/api/v1/voice/speak", json={
        "text": "Welcome to Nextserve Institute of Technology and Management.",
        "voice": "alloy",
        "speed": 1.0
    })
    assert res.status_code == 200
    assert res.headers["content-type"] in ["audio/mpeg", "audio/wav"]
    assert len(res.content) > 0


def test_voice_transcribe_endpoint():
    """Verify POST /api/v1/voice/transcribe accepts audio upload."""
    voice_svc = get_voice_service()
    # Generate valid synthetic WAV bytes from chime generator
    wav_bytes = voice_svc._generate_fallback_wav("Hello Nextserve test")

    audio_file = io.BytesIO(wav_bytes)
    res = client.post(
        "/api/v1/voice/transcribe",
        files={"file": ("test_input.wav", audio_file, "audio/wav")}
    )
    assert res.status_code == 200
    data = res.json()
    assert "text" in data
