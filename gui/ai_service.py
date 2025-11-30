"""AI service adapter used by the chat experience."""

from __future__ import annotations

import os
from typing import List

try:
    import google.generativeai as genai
except ImportError:
    genai = None


SYSTEM_PROMPT = (
    "You are a friendly AI teammate in an AI community project. "
    "Answer concisely and keep suggestions actionable. "
    "Always respond in Korean."
)


class AIService:
    """Thin wrapper around Google Gemini API (with graceful degradation)."""

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "AIzaSyCRkRzxVLW3ARPUpV2CVsOHFCWVOmBktYc")
        self.model = None
        if genai and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                try:
                    self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
                except Exception:
                    try:
                        self.model = genai.GenerativeModel("gemini-2.0-flash")
                    except Exception:
                        self.model = genai.GenerativeModel("gemini-pro")
            except Exception as e:
                print(f"모델 초기화 실패: {e}")
                self.model = None

    @property
    def available(self) -> bool:
        return bool(genai and self.api_key and self.model)

    def reply(self, chat_history: List[str], user_message: str) -> str:
        """Return an AI generated response or a fallback message."""
        if not user_message.strip():
            return "무언가를 입력해야 제가 도와드릴 수 있어요."

        if not self.available:
            return (
                "AI 응답을 생성하려면 GEMINI_API_KEY 환경 변수를 설정해 주세요. "
                "임시로 규칙 기반 답변을 제공합니다: "
                f"'{user_message}' 에 대한 아이디어는 같은 주제를 정리해 보고 "
                "팀원들과 프로토콜을 맞추는 것입니다."
            )

        prompt = SYSTEM_PROMPT + "\n\n"
        if chat_history:
            prompt += "이전 대화:\n"
            for entry in chat_history[-5:]:
                prompt += f"- {entry}\n"
            prompt += "\n"
        prompt += f"사용자: {user_message}\nAI:"

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as exc:
            return (
                "AI 응답 생성 중 문제가 발생했습니다. "
                f"({exc}) - 잠시 후 다시 시도해 주세요."
            )


ai_service = AIService()

