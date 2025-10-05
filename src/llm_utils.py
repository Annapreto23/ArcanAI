# llm_utils.py
from typing import List, Optional, Dict
from pydantic import BaseModel, create_model
from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["openai"]["api_key"])


class PositionMeaning(BaseModel):
    position: str
    meaning: str

class CardInterpretation(BaseModel):
    position: str
    card: str
    interpretation: str

class ReadingResponse(BaseModel):
    positions_meaning: List[PositionMeaning]
    cards_interpretation: List[CardInterpretation]
    synthesis: str


class LLMHandler:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def query_llm(self, messages, response_model=ReadingResponse):
        """Query the LLM with a defined response model."""
        response = client.chat.completions.parse(
            model=self.model,
            messages=messages,
            response_format=response_model
        )
        return response.choices[0].message.parsed
