"""FastAPI Router for Voice Interaction (api/routes/voice.py).

Implements Phase 7 Voice Interaction endpoints:
- POST /api/v1/voice/transcribe: Whisper audio speech-to-text
- POST /api/v1/voice/speak: TTS text-to-speech audio synthesis
- GET /api/v1/voice/capabilities: Voice engine metadata and supported voices
"""

from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.services.voice_service import voice_service

router = APIRouter(prefix="/voice", tags=["voice-interaction"])


class VoiceSpeakRequest(BaseModel):
    text: str = Field(..., description="Text content to synthesize into speech audio")
    voice: Optional[str] = Field("alloy", description="Voice profile: alloy, nova, echo, shimmer, onyx, fable")
    speed: Optional[float] = Field(1.0, description="Speech rate between 0.5 and 2.0")


@router.get("/capabilities", summary="Get voice engine capabilities and available voices")
def get_voice_capabilities():
    """Returns supported STT models, TTS voices, and audio formats."""
    return voice_service.get_capabilities()


@router.post("/transcribe", summary="Transcribe speech audio file via Whisper")
async def transcribe_audio_file(file: UploadFile = File(...)):
    """
    Ingests an uploaded microphone recording (webm, wav, mp3, ogg)
    and returns transcribed text using OpenAI Whisper.
    """
    try:
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty audio recording submitted."
            )

        filename = file.filename or "recording.webm"
        result = voice_service.transcribe_audio(audio_bytes=content, filename=filename)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech transcription failed: {str(exc)}"
        )


@router.post("/speak", summary="Convert text to speech audio via TTS")
def text_to_speech(payload: VoiceSpeakRequest):
    """
    Converts text response to MP3 audio stream using OpenAI TTS.
    Returns binary audio/mpeg stream for immediate playback in the browser.
    """
    try:
        is_live = voice_service.has_live_tts()
        audio_data = voice_service.synthesize_speech(
            text=payload.text,
            voice=payload.voice or "alloy",
            speed=payload.speed or 1.0
        )
        return Response(
            content=audio_data,
            media_type="audio/mpeg" if is_live else "audio/wav",
            headers={
                "Content-Disposition": "inline; filename=nextclaw_speech.mp3",
                "Cache-Control": "no-cache",
                "X-TTS-Engine": "openai_neural" if is_live else "fallback_chime",
                "X-Live-Speech": "true" if is_live else "false"
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text to speech synthesis failed: {str(exc)}"
        )
