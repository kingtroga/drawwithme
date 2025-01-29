# Copyright (c) 2025 AYEBATARIWALATE YEKOROGHA. All rights reserved.
import requests
from django.db import models
from django.conf import settings
import json
from django.core.exceptions import ValidationError
import numpy as np
from typing import List
import openai
import os


def get_embedding(text):
    """
    Get embeddings from OpenAI API with error handling.
    Can handle both single text and lists of texts.

    Args:
        text: Either a single string or a list of strings to get embeddings for.

    Returns:
        For single text: List[float] - a single embedding array.
        For list of texts: List[List[float]] - list of embedding arrays.
    """
    model = "text-embedding-3-large" #for more accuracy

    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
    
    try:
        is_single_text = isinstance(text, str)
        texts_to_process = [text] if is_single_text else text

        response = openai.embeddings.create(
            model=model,
            input=texts_to_process,
        )

        # Extract embeddings from response
        embeddings = [item.embedding for item in response.data]

        return embeddings[0] if is_single_text else embeddings

    except openai.OpenAIError as e:
        raise Exception(f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error while getting embedding: {str(e)}")

def validate_json(value):
    """Validate that the value is JSON serializable"""
    if value is None:
        return
    try:
        json.dumps(value)
    except (TypeError, ValueError):
        raise ValidationError('Value must be JSON serializable')

class BasicJSONField(models.TextField):
    """Simple TextField that serializes/deserializes JSON objects"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('validators', []).append(validate_json)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return None

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, (dict, list, bool, int, float, str)):
            return value
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return None

    def get_prep_value(self, value):
        if value is None:
            return value
        return json.dumps(value)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)
    
def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    v1 = np.array(v1)
    v2 = np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))