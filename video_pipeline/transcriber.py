"""
video_pipeline/transcriber.py
Audio extraction and speech-to-text transcription module.
Extracts 16kHz mono PCM WAV from input video via FFmpeg.
Provides FasterWhisperTranscriber (CPU int8) and deterministic MockTranscriber
for offline testing and CI/CD pipelines.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from video_pipeline.ffmpeg_resolver import get_ffmpeg_exe


class WordTimestamp(BaseModel):
    """Word-level alignment timestamp."""
    word: str
    start: float
    end: float
    probability: float = 1.0

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def get(self, item: str, default: Any = None) -> Any:
        return getattr(self, item, default)


class TranscriptSegment(BaseModel):
    """Timestamped subtitle/speech segment."""
    id: int = 1
    start: float
    end: float
    text: str
    words: List[WordTimestamp] = Field(default_factory=list)

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def get(self, item: str, default: Any = None) -> Any:
        return getattr(self, item, default)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "start": round(self.start, 3),
            "end": round(self.end, 3),
            "text": self.text,
            "words": [w.model_dump() for w in self.words],
        }


def extract_audio(
    video_path: Union[str, Path],
    output_wav: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Extract audio from video to 16kHz 16-bit mono PCM WAV for Whisper STT.
    """
    vid_path = Path(video_path).resolve()
    if not vid_path.exists():
        raise FileNotFoundError(f"Video file not found: {vid_path}")

    if output_wav is None:
        out_wav = vid_path.with_suffix(".wav")
    else:
        out_wav = Path(output_wav).resolve()

    out_wav.parent.mkdir(parents=True, exist_ok=True)
    exe = get_ffmpeg_exe()

    cmd = [
        exe,
        "-y",
        "-i", str(vid_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(out_wav),
    ]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg audio extraction failed: {proc.stderr}")

    if not out_wav.exists() or out_wav.stat().st_size == 0:
        raise RuntimeError(f"Audio file extraction produced empty output: {out_wav}")

    return out_wav


class MockTranscriber:
    """
    Deterministic speech-to-text engine for offline tests and rapid prototyping.
    Produces realistic GTA 6 gaming/trailer segments in <0.01 seconds.
    """

    DEFAULT_SEGMENTS = [
        {
            "id": 1,
            "start": 0.1,
            "end": 2.5,
            "text": "Look at this trailer, Vice City is finally back!",
            "words": [
                {"word": "Look", "start": 0.1, "end": 0.4},
                {"word": "at", "start": 0.4, "end": 0.6},
                {"word": "this", "start": 0.6, "end": 0.9},
                {"word": "trailer,", "start": 0.9, "end": 1.4},
                {"word": "Vice", "start": 1.5, "end": 1.8},
                {"word": "City", "start": 1.8, "end": 2.1},
                {"word": "is", "start": 2.1, "end": 2.2},
                {"word": "finally", "start": 2.2, "end": 2.4},
                {"word": "back!", "start": 2.4, "end": 2.5},
            ],
        },
        {
            "id": 2,
            "start": 2.6,
            "end": 5.4,
            "text": "The graphics and lighting are completely unbelievable.",
            "words": [
                {"word": "The", "start": 2.6, "end": 2.8},
                {"word": "graphics", "start": 2.8, "end": 3.4},
                {"word": "and", "start": 3.4, "end": 3.6},
                {"word": "lighting", "start": 3.6, "end": 4.1},
                {"word": "are", "start": 4.1, "end": 4.3},
                {"word": "completely", "start": 4.3, "end": 4.8},
                {"word": "unbelievable.", "start": 4.8, "end": 5.4},
            ],
        },
        {
            "id": 3,
            "start": 5.5,
            "end": 8.0,
            "text": "Look at the cars and neon sunsets along Ocean Drive.",
            "words": [
                {"word": "Look", "start": 5.5, "end": 5.8},
                {"word": "at", "start": 5.8, "end": 6.0},
                {"word": "the", "start": 6.0, "end": 6.2},
                {"word": "cars", "start": 6.2, "end": 6.6},
                {"word": "and", "start": 6.6, "end": 6.8},
                {"word": "neon", "start": 6.8, "end": 7.1},
                {"word": "sunsets", "start": 7.1, "end": 7.5},
                {"word": "along", "start": 7.5, "end": 7.7},
                {"word": "Ocean", "start": 7.7, "end": 7.9},
                {"word": "Drive.", "start": 7.9, "end": 8.0},
            ],
        },
        {
            "id": 4,
            "start": 8.1,
            "end": 10.5,
            "text": "Make sure to check the link in bio for the exclusive drop!",
            "words": [
                {"word": "Make", "start": 8.1, "end": 8.3},
                {"word": "sure", "start": 8.3, "end": 8.6},
                {"word": "to", "start": 8.6, "end": 8.7},
                {"word": "check", "start": 8.7, "end": 9.0},
                {"word": "the", "start": 9.0, "end": 9.1},
                {"word": "link", "start": 9.1, "end": 9.4},
                {"word": "in", "start": 9.4, "end": 9.6},
                {"word": "bio", "start": 9.6, "end": 9.9},
                {"word": "for", "start": 9.9, "end": 10.0},
                {"word": "the", "start": 10.0, "end": 10.1},
                {"word": "exclusive", "start": 10.1, "end": 10.3},
                {"word": "drop!", "start": 10.3, "end": 10.5},
            ],
        },
    ]

    def transcribe(
        self,
        video_path: Optional[Union[str, Path]] = None,
        audio_path: Optional[Union[str, Path]] = None,
    ) -> List[TranscriptSegment]:
        """Return deterministic transcript segments."""
        segments: List[TranscriptSegment] = []
        for raw in self.DEFAULT_SEGMENTS:
            words = [WordTimestamp(**w) for w in raw.get("words", [])]
            segments.append(
                TranscriptSegment(
                    id=raw["id"],
                    start=raw["start"],
                    end=raw["end"],
                    text=raw["text"],
                    words=words,
                )
            )
        return segments


class FasterWhisperTranscriber:
    """
    Live local Whisper speech-to-text using faster-whisper CTranslate2 INT8 model.
    """

    def __init__(
        self,
        model_size: str = "tiny",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None

    def _get_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
        return self._model

    def transcribe(
        self,
        video_path: Optional[Union[str, Path]] = None,
        audio_path: Optional[Union[str, Path]] = None,
    ) -> List[TranscriptSegment]:
        """Extract audio if needed and transcribe using faster-whisper."""
        if audio_path is None and video_path is not None:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                tmp_wav_path = Path(tmp_wav.name)
            try:
                extract_audio(video_path, tmp_wav_path)
                return self._transcribe_audio_file(tmp_wav_path)
            finally:
                if tmp_wav_path.exists():
                    tmp_wav_path.unlink()
        elif audio_path is not None:
            return self._transcribe_audio_file(Path(audio_path))
        else:
            raise ValueError("Either video_path or audio_path must be provided")

    def _transcribe_audio_file(self, wav_path: Path) -> List[TranscriptSegment]:
        model = self._get_model()
        segments_raw, _ = model.transcribe(
            str(wav_path),
            word_timestamps=True,
            language="en",
        )

        results: List[TranscriptSegment] = []
        for idx, seg in enumerate(segments_raw, start=1):
            words = []
            if hasattr(seg, "words") and seg.words:
                for w in seg.words:
                    words.append(
                        WordTimestamp(
                            word=w.word.strip(),
                            start=round(w.start, 3),
                            end=round(w.end, 3),
                            probability=round(w.probability, 3),
                        )
                    )
            results.append(
                TranscriptSegment(
                    id=idx,
                    start=round(seg.start, 3),
                    end=round(seg.end, 3),
                    text=seg.text.strip(),
                    words=words,
                )
            )
        return results


class Transcriber:
    """Unified transcriber entrypoint supporting both live Whisper and mock modes."""

    def __init__(self, mock_mode: bool = False, model_size: str = "tiny"):
        self.mock_mode = mock_mode
        self.model_size = model_size
        if mock_mode:
            self._engine = MockTranscriber()
        else:
            try:
                self._engine = FasterWhisperTranscriber(model_size=model_size)
            except Exception:
                self._engine = MockTranscriber()

    def transcribe(
        self,
        video_path: Optional[Union[str, Path]] = None,
        audio_path: Optional[Union[str, Path]] = None,
    ) -> List[TranscriptSegment]:
        return self._engine.transcribe(video_path=video_path, audio_path=audio_path)


def transcribe_video(
    video_path: Union[str, Path],
    mock: bool = True,
    model_size: str = "tiny",
) -> List[TranscriptSegment]:
    """Helper function to transcribe a video path."""
    trans = Transcriber(mock_mode=mock, model_size=model_size)
    return trans.transcribe(video_path=video_path)
