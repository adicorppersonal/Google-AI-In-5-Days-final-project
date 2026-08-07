from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from zoneinfo import ZoneInfo
import re
from app.db import dispatch_background_storage, search_stored_articles_async, get_recent_articles_async

# ==========================================
# 1. Explicit JSON Schemas (Pydantic Models)
# ==========================================

class SearchInput(BaseModel):
    """Explicit JSON Schema for web search tool inputs."""
    query: str = Field(..., description="Search topic, keywords, or research query for news retrieval.")
    max_results: Optional[int] = Field(2, description="Maximum number of articles to retrieve.", ge=1, le=10)
    use_cross_session_memory: Optional[bool] = Field(True, description="Whether to query past stored cross-session memory.")


class ArticleMetadata(BaseModel):
    """Explicit JSON Schema for individual article metadata."""
    id: str = Field(..., description="Unique article identifier.")
    title: str = Field(..., description="Title of the fetched news article.")
    content: str = Field(..., description="Summary content snippet of the article.")
    word_count: int = Field(..., description="Total word count of the content.")
    timestamp: str = Field(..., description="UTC ISO timestamp of retrieval.")


class SearchResult(BaseModel):
    """Explicit JSON Schema for web search tool outputs."""
    status: str = Field(..., description="Execution status: 'success' or 'error'.")
    query: str = Field(..., description="The query that was executed.")
    fetched_articles: List[ArticleMetadata] = Field(default_factory=list, description="List of fetched and stored news articles.")
    memory_articles: List[ArticleMetadata] = Field(default_factory=list, description="Retrieved past articles from vector store / cross-session memory.")
    error: Optional[str] = Field(None, description="Error message if execution failed.")
    recovery_instructions: Optional[str] = Field(None, description="Guided recovery instructions in case of execution failure.")


class RedactionInput(BaseModel):
    """Explicit JSON Schema for PII redaction tool inputs."""
    text: str = Field(..., description="Raw input text to be sanitized for PII.")


class RedactionResult(BaseModel):
    """Explicit JSON Schema for PII redaction tool outputs."""
    sanitized_text: str = Field(..., description="Sanitized text with PII redacted.")
    pii_detected: bool = Field(..., description="Flag indicating whether PII was found and redacted.")
    error: Optional[str] = Field(None, description="Error message if redaction failed.")
    recovery_instructions: Optional[str] = Field(None, description="Guided recovery instructions in case of redaction failure.")


# ==========================================
# 2. Async Tools with Vector Memory & Background Task Persistence
# ==========================================

async def google_web_search(input_data: SearchInput | Dict[str, Any] | str) -> Dict[str, Any]:
    """Performs a web search using simulated retrieval, queries vector-backed cross-session memory asynchronously,
    and dispatches storage writes as non-blocking background tasks (`asyncio.create_task`).
    
    Includes explicit schema validation and guided error handling with recovery instructions.
    """
    try:
        if isinstance(input_data, str):
            validated_input = SearchInput(query=input_data)
        elif isinstance(input_data, dict):
            validated_input = SearchInput(**input_data)
        elif isinstance(input_data, SearchInput):
            validated_input = input_data
        else:
            raise ValueError(f"Invalid input type: {type(input_data)}")
    except (ValidationError, ValueError) as e:
        return SearchResult(
            status="error",
            query=str(input_data),
            fetched_articles=[],
            memory_articles=[],
            error=f"Input validation failed: {str(e)}",
            recovery_instructions="Please provide a valid search query as a non-empty string or dictionary matching SearchInput schema."
        ).model_dump()

    try:
        now = datetime.now(ZoneInfo("UTC")).isoformat()
        query = validated_input.query
        
        # 1. Retrieve vector/Vertex AI search cross-session memory asynchronously if enabled
        memory_articles = []
        if validated_input.use_cross_session_memory:
            past_records = await search_stored_articles_async(keyword=query, limit=3)
            memory_articles = [ArticleMetadata(**rec) for rec in past_records]

        # 2. Simulated web search retrieval
        search_results = [
            {
                "id": f"web-{int(datetime.now().timestamp())}-1",
                "title": f"Latest Developments in {query}: Agentic AI & Systems",
                "content": f"Recent industry reports on {query} highlight massive gains in multi-agent coordination, structured error recovery, and robust reasoning frameworks.",
                "timestamp": now,
            },
            {
                "id": f"web-{int(datetime.now().timestamp())}-2",
                "title": f"Production Scaling and Security for {query}",
                "content": f"Engineers deploying {query} report significant improvements when incorporating input sanitization, prompt injection guardrails, and persistent memory storage.",
                "timestamp": now,
            }
        ]

        stored_articles = []
        for art in search_results[:validated_input.max_results]:
            word_count = len(art["content"].split())
            article_data = {
                "id": art["id"],
                "title": art["title"],
                "content": art["content"],
                "word_count": word_count,
                "timestamp": art["timestamp"],
            }
            # Dispatch storage write as an asynchronous background task (non-blocking)
            try:
                dispatch_background_storage(article_data, query)
            except Exception as bg_err:
                print(f"[Warning] Failed to dispatch background storage task: {bg_err}")
            
            stored_articles.append(ArticleMetadata(**article_data))

        result = SearchResult(
            status="success",
            query=query,
            fetched_articles=stored_articles,
            memory_articles=memory_articles,
            error=None,
            recovery_instructions=None
        )
        return result.model_dump()

    except Exception as exc:
        error_result = SearchResult(
            status="error",
            query=getattr(validated_input, 'query', 'unknown'),
            fetched_articles=[],
            memory_articles=[],
            error=f"Web search execution failed: {str(exc)}",
            recovery_instructions="An unexpected error occurred during async search retrieval or background task dispatch. Please check database permissions."
        )
        return error_result.model_dump()


def redact_pii(input_data: RedactionInput | Dict[str, Any] | str) -> Dict[str, Any]:
    """Programmatically redacts personal identifiable information (PII) from text with explicit schema validation."""
    try:
        if isinstance(input_data, str):
            validated_input = RedactionInput(text=input_data)
        elif isinstance(input_data, dict):
            validated_input = RedactionInput(**input_data)
        elif isinstance(input_data, RedactionInput):
            validated_input = input_data
        else:
            raise ValueError(f"Invalid input type: {type(input_data)}")
    except (ValidationError, ValueError) as e:
        return RedactionResult(
            sanitized_text="",
            pii_detected=False,
            error=f"Redaction input validation failed: {str(e)}",
            recovery_instructions="Please provide a valid text string for PII redaction."
        ).model_dump()

    try:
        text = validated_input.text
        if not text:
            return RedactionResult(
                sanitized_text="",
                pii_detected=False,
                error=None,
                recovery_instructions=None
            ).model_dump()

        original_text = text
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]', text)
        text = re.sub(r'\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})\b', '[REDACTED_PHONE]', text)
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]', text)
        text = re.sub(r'\b(?:\d[ -]*?){13,16}\b', '[REDACTED_CREDIT_CARD]', text)

        pii_detected = (text != original_text)

        return RedactionResult(
            sanitized_text=text,
            pii_detected=pii_detected,
            error=None,
            recovery_instructions=None
        ).model_dump()

    except Exception as exc:
        return RedactionResult(
            sanitized_text=getattr(validated_input, 'text', ''),
            pii_detected=False,
            error=f"PII redaction execution failed: {str(exc)}",
            recovery_instructions="An unexpected error occurred during regex matching. Please ensure the input text is valid UTF-8 and retry."
        ).model_dump()
