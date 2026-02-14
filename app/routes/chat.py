import os

import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

chat_bp = Blueprint('chat', __name__)

GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
SYSTEM_PERSONA = (
    "You are Sensybull, a helpful AI assistant specializing in financial news "
    "and market insights. Provide concise, accurate, and helpful responses about "
    "stocks, companies, and market trends. Always base your responses on the "
    "article context when provided."
)


def _build_system_messages(article_context):
    messages = []

    if article_context:
        title = article_context.get('title', '')
        summary = article_context.get('summary', '')
        bullets = article_context.get('bullets', [])
        tickers = article_context.get('tickers', [])

        parts = [f"Article: {title}"]
        if summary:
            parts.append(f"Summary: {summary}")
        if bullets:
            parts.append("Key Points:\n" + "\n".join(f"- {b}" for b in bullets))
        if tickers:
            companies = ", ".join(
                f"{t['symbol']} ({t['name']})" for t in tickers
            )
            parts.append(f"Related Companies: {companies}")

        messages.append({"role": "system", "content": "\n\n".join(parts)})

    messages.append({"role": "system", "content": SYSTEM_PERSONA})
    return messages


@chat_bp.route('/', methods=['POST'])
@jwt_required()
def chat():
    data = request.get_json()
    if not data or not data.get('messages'):
        return jsonify({'error': 'messages is required'}), 400

    user_messages = data['messages']
    article_context = data.get('article_context')

    system_messages = _build_system_messages(article_context)
    all_messages = system_messages + user_messages

    groq_api_key = os.environ.get('GROQ_API_KEY')
    if not groq_api_key:
        return jsonify({'error': 'AI service not configured'}), 500

    try:
        resp = requests.post(
            GROQ_API_URL,
            headers={
                'Authorization': f'Bearer {groq_api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'llama-3.3-70b-versatile',
                'messages': all_messages,
                'temperature': 0.7,
                'max_tokens': 1024,
                'top_p': 0.9,
            },
            timeout=30,
        )
        resp.raise_for_status()
    except requests.RequestException:
        return jsonify({'error': 'AI service error'}), 502

    result = resp.json()
    reply = result['choices'][0]['message']['content']
    return jsonify({'response': reply})
