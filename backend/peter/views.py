from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
import requests
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

@csrf_exempt
def health_check(request):
    """
    Simple health check endpoint for Peter Rabbit API
    """
    return JsonResponse({
        'status': 'ok',
        'message': 'Peter Rabbit API is working!'
    })

@csrf_exempt
@require_http_methods(["POST"])
def check_question1_answer(request):
    """
    API endpoint to check Peter Rabbit Question 1 answer - Story Title
    """
    try:
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please enter an answer.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 2:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please provide a more complete answer.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization'
            })

        # AI-powered analysis for the Peter Rabbit title question
        return analyze_peter_title_answer(user_answer)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Error in check_peter_question1_answer: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def analyze_peter_title_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit title answer specifically
    """
    logger.debug(f"Starting AI analysis for answer: '{user_answer}'")
    
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.error("OpenRouter API key not found in environment variables")
        return JsonResponse({
            'error': 'API configuration error. Please contact support.'
        }, status=500)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Title Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified the story title. Your task is twofold:
1. Evaluate the correctness of the student's answer about the story "The Tale of Peter Rabbit".
2. Identify any misspelled English words in their answer.

The correct story title is: "The Tale of Peter Rabbit"

IMPORTANT: Your entire response MUST be a single, valid JSON object and nothing else.

The required JSON format is:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "incorrect",
    "show_answer": true/false,
    "correct_answer": "The Tale of Peter Rabbit",
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines for the TITLE question:
- If the answer is exactly correct or very close (like "the tale of peter rabbit", "Tale of Peter Rabbit"), mark as correct
- If they have "Peter Rabbit" but missing "The Tale of", mark as good but explain the full title
- If they just say "Peter Rabbit" without "Tale", it's still partially correct
- If they have some right elements but significant errors, give guidance
- If completely wrong, mark as incorrect
- Always be encouraging and specific in your feedback
- If isCorrect is false, set show_answer to true
- If isCorrect is true, set show_answer to false

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this title answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 200
    }

    try:
        logger.debug(f"Making request to OpenRouter API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                logger.debug(f"Successfully parsed AI response")
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.error(f"AI returned invalid JSON: {e}, Raw response: {result_raw}")
                return JsonResponse({
                    'error': 'AI service returned invalid response. Please try again.'
                }, status=500)
        elif response.status_code == 401:
            logger.error(f"OpenRouter API authentication failed: {response.text}")
            return JsonResponse({
                'error': 'API authentication failed. Please check your API key configuration.'
            }, status=500)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'AI service error ({response.status_code}). Please try again.'
            }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_title_answer: {e}")
        return JsonResponse({
            'error': 'Unable to connect to AI service. Please try again.'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in analyze_peter_title_answer: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Unexpected error occurred. Please try again.'
        }, status=500)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Title Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified the story title. Your task is twofold:
1. Evaluate the correctness of the student's answer about the story "The Tale of Peter Rabbit".
2. Identify any misspelled English words in their answer.

The correct story title is: "The Tale of Peter Rabbit"

IMPORTANT: Your entire response MUST be a single, valid JSON object and nothing else.

The required JSON format is:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "incorrect",
    "show_answer": true/false,
    "correct_answer": "The Tale of Peter Rabbit",
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines for the TITLE question:
- If the answer is exactly correct or very close (like "the tale of peter rabbit", "Tale of Peter Rabbit"), mark as correct
- If they have "Peter Rabbit" but missing "The Tale of", mark as good but explain the full title
- If they just say "Peter Rabbit" without "Tale", it's still partially correct
- If they have some right elements but significant errors, give guidance
- If completely wrong, mark as incorrect
- Always be encouraging and specific in your feedback
- If isCorrect is false, set show_answer to true
- If isCorrect is true, set show_answer to false

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this title answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 200
    }

    try:
        logger.debug(f"Making request to OpenRouter API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                logger.debug(f"Successfully parsed AI response")
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.warning(f"AI JSON decode error: {e}, using fallback")
                return create_peter_title_fallback_response(user_answer)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'AI service temporarily unavailable. Please try again.'
            }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_title_answer: {e}")
        return JsonResponse({
            'error': 'Unable to check answer right now. Please try again.'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in analyze_peter_title_answer: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Unable to check answer right now. Please try again.'
        }, status=500)

def create_peter_title_fallback_response(user_answer):
    """
    Create a fallback response if AI service fails for Peter Rabbit title
    """
    try:
        user_lower = user_answer.lower()
        correct_title = "The Tale of Peter Rabbit"
        
        # Simple keyword matching as fallback
        has_peter = 'peter' in user_lower
        has_rabbit = 'rabbit' in user_lower
        has_tale = 'tale' in user_lower or 'story' in user_lower
        
        if has_peter and has_rabbit and has_tale:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! You got the complete title right!',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': correct_title,
                'misspelled_words': []
            })
        elif has_peter and has_rabbit:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Great! You have the main characters. The full title also mentions it being a "Tale".',
                'feedback_type': 'good',
                'show_answer': False,
                'correct_answer': correct_title,
                'misspelled_words': []
            })
        elif has_peter:
            return JsonResponse({
                'isCorrect': False,
                'message': 'You got the main character! But the title also includes another important word about what kind of animal Peter is.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_title,
                'misspelled_words': []
            })
        elif has_rabbit:
            return JsonResponse({
                'isCorrect': False,
                'message': 'You identified the type of animal, but you are missing the main character\'s name.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_title,
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about the main character in this story - what is his name and what kind of animal is he?',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_title,
                'misspelled_words': []
            })
    except Exception as e:
        logger.error(f"Error in create_peter_title_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })
@csrf_exempt
@require_http_methods(["POST"])
def check_question2_answer(request):
    """
    API endpoint to check Peter Rabbit Question 2 answer - Story Author
    """
    try:
        logger.debug(f"Received request: {request.method} {request.path}")
        logger.debug(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        logger.debug(f"User answer: '{user_answer}'")
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please enter an answer.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 2:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please provide a more complete answer.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization'
            })

        # AI-powered analysis for the Peter Rabbit author question
        return analyze_peter_author_answer(user_answer)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in check_peter_question2_answer: {e}", exc_info=True)
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

def analyze_peter_author_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit author answer specifically
    """
    logger.debug(f"Starting AI analysis for author answer: '{user_answer}'")
    
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.error("OpenRouter API key not found in environment variables")
        return JsonResponse({
            'error': 'API configuration error. Please contact support.'
        }, status=500)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Author Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified the author of "The Tale of Peter Rabbit". Your task is twofold:
1. Evaluate the correctness of the student's answer about the story "The Tale of Peter Rabbit".
2. Identify any misspelled English words in their answer.

IMPORTANT CONTEXT: "The Tale of Peter Rabbit" was written by Beatrix Potter, a famous British author and illustrator who created many beloved children's stories featuring animal characters.

CORRECT ANSWERS include:
- "Beatrix Potter" (the exact correct answer)
- "Beatrix" or "Potter" (partial but recognizable)
- Close spellings like "Beatrice Potter" or "Beatrix Pottor" (should be marked as good but with spelling correction)

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "incorrect",
    "show_answer": true/false,
    "correct_answer": "Beatrix Potter",
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines for the AUTHOR question:
- If they mention "Beatrix Potter" correctly, mark as "excellent"
- If they mention "Beatrix" or "Potter" but not both, mark as "good" 
- If they have close spellings of the name, mark as "good" but mention the correct spelling
- If they give a completely wrong author (like "Dr. Seuss"), mark as "incorrect"
- If they say "I don't know" or similar, mark as "partial" and encourage them
- Always be encouraging and educational
- If isCorrect is false, set show_answer to true
- If isCorrect is true, set show_answer to false

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this author answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 250
    }

    try:
        logger.debug(f"Making request to OpenRouter API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                logger.debug(f"Successfully parsed AI response")
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.error(f"AI returned invalid JSON: {e}, Raw response: {result_raw}")
                return create_peter_author_fallback_response(user_answer)
        elif response.status_code == 401:
            logger.error(f"OpenRouter API authentication failed: {response.text}")
            return JsonResponse({
                'error': 'API authentication failed. Please check your API key configuration.'
            }, status=500)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'AI service error ({response.status_code}). Please try again.'
            }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_author_answer: {e}")
        return JsonResponse({
            'error': 'Unable to connect to AI service. Please try again.'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in analyze_peter_author_answer: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Unexpected error occurred. Please try again.'
        }, status=500)

def create_peter_author_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit author question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        correct_answer = "Beatrix Potter"
        
        # Keywords that indicate correct understanding
        has_beatrix = 'beatrix' in user_lower or 'beatrice' in user_lower
        has_potter = 'potter' in user_lower or 'pottor' in user_lower
        
        # Obviously wrong authors
        wrong_authors = ['dr. seuss', 'roald dahl', 'j.k. rowling', 'disney', 
                        'brothers grimm', 'hans christian andersen', 'unknown', 'anonymous']
        
        # Check if they understand it's Beatrix Potter
        has_wrong_author = any(wrong in user_lower for wrong in wrong_authors)
        
        if has_beatrix and has_potter:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! You correctly identified Beatrix Potter as the author of Peter Rabbit stories.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_beatrix or has_potter:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Good! You have part of the author\'s name. The full name is Beatrix Potter.',
                'feedback_type': 'good',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_wrong_author:
            return JsonResponse({
                'isCorrect': False,
                'message': 'That author didn\'t write Peter Rabbit. Think about a British author who wrote many animal stories.',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif 'don\'t know' in user_lower or 'not sure' in user_lower:
            return JsonResponse({
                'isCorrect': False,
                'message': 'That\'s okay! The author is a famous British writer who created many beloved animal characters.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about a British author known for writing charming animal stories with beautiful illustrations.',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
    except Exception as e:
        logger.error(f"Error in create_peter_author_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })
@csrf_exempt
@require_http_methods(["POST"])
def check_question3_answer(request):
    """
    API endpoint to check Peter Rabbit Question 3 answer - Story Genre
    """
    try:
        logger.debug(f"Received request: {request.method} {request.path}")
        logger.debug(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        logger.debug(f"User answer: '{user_answer}'")
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please enter an answer.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 2:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please provide a more complete answer.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization'
            })

        # AI-powered analysis for the Peter Rabbit genre question
        return analyze_peter_genre_answer(user_answer)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in check_peter_question3_answer: {e}", exc_info=True)
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

def analyze_peter_genre_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit genre answer specifically
    """
    logger.debug(f"Starting AI analysis for genre answer: '{user_answer}'")
    
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.error("OpenRouter API key not found in environment variables")
        return JsonResponse({
            'error': 'API configuration error. Please contact support.'
        }, status=500)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Genre Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified the genre of "The Tale of Peter Rabbit". Your task is twofold:
1. Evaluate the correctness of the student's answer about the story "The Tale of Peter Rabbit".
2. Identify any misspelled English words in their answer.

The correct broad genre is "Fiction". Other related correct answers include "children's fiction", "fairy tale", "animal story", "picture book", or "fantasy".

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "incorrect",
    "show_answer": true/false,
    "correct_answer": "Fiction",
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines for the GENRE question:
- If the answer is "Fiction" or a very close synonym (like "children's fiction", "fairy tale", "animal story", "fantasy"), mark as correct and explain WHY (it's a made-up story with talking animals).
- If the answer is "Non-Fiction", mark as incorrect and explain the difference.
- If the answer is a sub-genre like "Adventure", "Comedy", or "Drama", acknowledge their thinking but explain that the broader category is "Fiction". Mark as "good" but suggest the main genre.
- Always be encouraging and educational. If isCorrect is false, set show_answer to true.
- If isCorrect is true, set show_answer to false.

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this genre answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }

    try:
        logger.debug(f"Making request to OpenRouter API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                logger.debug(f"Successfully parsed AI response")
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.error(f"AI returned invalid JSON: {e}, Raw response: {result_raw}")
                return create_peter_genre_fallback_response(user_answer)
        elif response.status_code == 401:
            logger.error(f"OpenRouter API authentication failed: {response.text}")
            return JsonResponse({
                'error': 'API authentication failed. Please check your API key configuration.'
            }, status=500)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'AI service error ({response.status_code}). Please try again.'
            }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_genre_answer: {e}")
        return JsonResponse({
            'error': 'Unable to connect to AI service. Please try again.'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in analyze_peter_genre_answer: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Unexpected error occurred. Please try again.'
        }, status=500)

def create_peter_genre_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit genre question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        correct_answer = "Fiction"
        
        # Keywords that indicate correct understanding
        fiction_keywords = ['fiction', 'fairy tale', 'fantasy', 'children', 'animal story', 'picture book', 'story']
        nonfiction_keywords = ['non-fiction', 'nonfiction', 'biography', 'history', 'factual', 'real', 'true']
        subgenre_keywords = ['adventure', 'comedy', 'drama', 'mystery', 'romance']
        
        has_fiction = any(keyword in user_lower for keyword in fiction_keywords)
        has_nonfiction = any(keyword in user_lower for keyword in nonfiction_keywords)
        has_subgenre = any(keyword in user_lower for keyword in subgenre_keywords)
        
        if user_lower == 'fiction' or 'children\'s fiction' in user_lower or 'fairy tale' in user_lower:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! Fiction is exactly right because Peter Rabbit is an imaginary story with talking animals.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_fiction:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Great! You understand this is fiction - a made-up story with imaginary characters and talking animals.',
                'feedback_type': 'good',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_nonfiction:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Not quite! Peter Rabbit is actually fiction because it\'s an imaginary story with talking animals. Non-fiction would be true stories about real events.',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_subgenre:
            return JsonResponse({
                'isCorrect': False,
                'message': 'You\'re thinking about story types! But the main genre category is broader - think about whether this story is real or made-up.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about whether Peter Rabbit is a real story about real animals, or an imaginary story with talking animals.',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
    except Exception as e:
        logger.error(f"Error in create_peter_genre_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_question4_answer(request):
    """
    API endpoint to check Peter Rabbit Question 4 answer - Main Animal
    """
    try:
        logger.debug(f"Received request: {request.method} {request.path}")
        logger.debug(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        logger.debug(f"User answer: '{user_answer}'")
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please enter an answer.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 2:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please provide a more complete answer.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization'
            })

        # AI-powered analysis for the Peter Rabbit main animal question
        return analyze_peter_main_animal_answer(user_answer)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in check_peter_question4_answer: {e}", exc_info=True)
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

def analyze_peter_main_animal_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit main animal answer specifically
    """
    logger.debug(f"Starting AI analysis for main animal answer: '{user_answer}'")
    
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.error("OpenRouter API key not found in environment variables")
        return JsonResponse({
            'error': 'API configuration error. Please contact support.'
        }, status=500)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Main Animal Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified the main animal in "The Tale of Peter Rabbit". Your task is twofold:
1. Evaluate the correctness of the student's answer about the story "The Tale of Peter Rabbit".
2. Identify any misspelled English words in their answer.

The correct answer is "Rabbit" - Peter Rabbit is the main character and he is a rabbit.

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "incorrect",
    "show_answer": true/false,
    "correct_answer": "Rabbit",
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines for the MAIN ANIMAL question:
- If the answer is "Rabbit" or "Bunny", mark as "excellent"
- If they mention "Peter" along with "rabbit" (like "Peter is a rabbit"), mark as "excellent" 
- If they say just "Peter" without mentioning he's a rabbit, mark as "good" but explain what type of animal Peter is
- If they mention other animals from the story (like "cat" for the cat or birds), mark as "partial" and explain that Peter is the MAIN character
- If they give completely wrong animals (like "dog", "mouse", "bear"), mark as "incorrect"
- Always be encouraging and educational
- If isCorrect is false, set show_answer to true
- If isCorrect is true, set show_answer to false

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this main animal answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 250
    }

    try:
        logger.debug(f"Making request to OpenRouter API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                logger.debug(f"Successfully parsed AI response")
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.error(f"AI returned invalid JSON: {e}, Raw response: {result_raw}")
                return create_peter_main_animal_fallback_response(user_answer)
        elif response.status_code == 401:
            logger.error(f"OpenRouter API authentication failed: {response.text}")
            return JsonResponse({
                'error': 'API authentication failed. Please check your API key configuration.'
            }, status=500)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'AI service error ({response.status_code}). Please try again.'
            }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_main_animal_answer: {e}")
        return JsonResponse({
            'error': 'Unable to connect to AI service. Please try again.'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in analyze_peter_main_animal_answer: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Unexpected error occurred. Please try again.'
        }, status=500)

def create_peter_main_animal_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit main animal question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        correct_answer = "Rabbit"
        
        # Keywords that indicate correct understanding
        has_rabbit = 'rabbit' in user_lower or 'bunny' in user_lower
        has_peter = 'peter' in user_lower
        
        # Other animals that might appear in the story
        other_story_animals = ['cat', 'bird', 'sparrow', 'mouse']
        has_other_story_animal = any(animal in user_lower for animal in other_story_animals)
        
        # Wrong animals
        wrong_animals = ['dog', 'bear', 'wolf', 'fox', 'lion', 'tiger', 'elephant']
        has_wrong_animal = any(animal in user_lower for animal in wrong_animals)
        
        if has_rabbit and has_peter:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! You correctly identified that Peter is a rabbit, and he is the main character of the story.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_rabbit:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Perfect! Rabbit is exactly right. Peter Rabbit is the main character and he is a rabbit.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_peter and not has_rabbit:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Good! Peter is the main character. Can you tell me what type of animal Peter is?',
                'feedback_type': 'good',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_other_story_animal:
            return JsonResponse({
                'isCorrect': False,
                'message': 'There are other animals in the story, but think about the MAIN character. What type of animal is Peter?',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_wrong_animal:
            return JsonResponse({
                'isCorrect': False,
                'message': 'That animal isn\'t in this story. Think about the main character, Peter. What type of animal is he?',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about the main character of the story. His name is Peter, and he\'s a type of animal that hops and has long ears.',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
    except Exception as e:
        logger.error(f"Error in create_peter_main_animal_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_question5_answer(request):
    """
    API endpoint to check Peter Rabbit Question 5 answer - Personality
    """
    try:
        logger.debug(f"Received request: {request.method} {request.path}")
        logger.debug(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        logger.debug(f"User answer: '{user_answer}'")
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please enter an answer.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 3:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please provide more details about Peter\'s personality.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization'
            })

        # AI-powered analysis for the Peter Rabbit personality question
        return analyze_peter_personality_answer(user_answer)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in check_peter_question5_answer: {e}", exc_info=True)
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

def analyze_peter_personality_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit personality answer specifically
    """
    logger.debug(f"Starting AI analysis for personality answer: '{user_answer}'")
    
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.error("OpenRouter API key not found in environment variables")
        return JsonResponse({
            'error': 'API configuration error. Please contact support.'
        }, status=500)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Personality Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified Peter Rabbit's personality from "The Tale of Peter Rabbit". Your task is twofold:
1. Evaluate the correctness of the student's answer about Peter Rabbit's personality.
2. Identify any misspelled English words in their answer.

Peter Rabbit's main personality traits include:
- Curious and adventurous
- Mischievous and naughty
- Disobedient (he goes into Mr. McGregor's garden despite being told not to)
- Brave but sometimes reckless
- Young and playful
- Gets into trouble easily

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "needs_improvement",
    "show_answer": false,
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines for the PERSONALITY question:
- If they mention multiple accurate traits (curious, mischievous, adventurous, naughty, disobedient), mark as "excellent"
- If they mention 1-2 accurate traits, mark as "good"
- If they mention traits that are somewhat related but not quite accurate, mark as "partial"
- If they give completely wrong personality traits, mark as "needs_improvement"
- Accept various ways of expressing the same concepts (e.g., "naughty" = "mischievous", "curious" = "adventurous")
- Always be encouraging and help them understand Peter's character
- For personality questions, never show a "correct answer" since there can be multiple valid ways to describe personality
- Always set show_answer to false
- Focus on whether they understood that Peter gets into trouble and doesn't always follow rules

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this personality answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }

    try:
        logger.debug(f"Making request to OpenRouter API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                
                # Set isCorrect based on feedback_type for personality questions
                feedback_type = parsed_result.get('feedback_type', 'needs_improvement')
                parsed_result['isCorrect'] = feedback_type in ['excellent', 'good', 'partial']
                
                logger.debug(f"Successfully parsed AI response")
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.error(f"AI returned invalid JSON: {e}, Raw response: {result_raw}")
                return create_peter_personality_fallback_response(user_answer)
        elif response.status_code == 401:
            logger.error(f"OpenRouter API authentication failed: {response.text}")
            return JsonResponse({
                'error': 'API authentication failed. Please check your API key configuration.'
            }, status=500)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'AI service error ({response.status_code}). Please try again.'
            }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_personality_answer: {e}")
        return JsonResponse({
            'error': 'Unable to connect to AI service. Please try again.'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in analyze_peter_personality_answer: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Unexpected error occurred. Please try again.'
        }, status=500)

def create_peter_personality_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit personality question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        
        # Keywords that indicate correct personality understanding
        positive_traits = {
            'curious': any(word in user_lower for word in ['curious', 'inquisitive', 'interested', 'wondering']),
            'adventurous': any(word in user_lower for word in ['adventurous', 'explorer', 'brave', 'bold']),
            'mischievous': any(word in user_lower for word in ['mischievous', 'naughty', 'troublesome', 'cheeky']),
            'disobedient': any(word in user_lower for word in ['disobedient', 'doesn\'t listen', 'breaks rules', 'rebels']),
            'playful': any(word in user_lower for word in ['playful', 'fun', 'energetic', 'active']),
            'young': any(word in user_lower for word in ['young', 'little', 'small', 'child'])
        }
        
        # Negative traits that don't fit Peter
        negative_traits = ['mean', 'cruel', 'evil', 'scary', 'angry', 'sad', 'boring', 'lazy']
        has_negative = any(trait in user_lower for trait in negative_traits)
        
        # Count accurate personality traits mentioned
        accurate_traits = sum(positive_traits.values())
        
        # Check for reasoning/explanation words
        reasoning_words = ['because', 'since', 'when', 'he', 'goes', 'into', 'garden', 'mcgregor']
        has_reasoning = any(word in user_lower for word in reasoning_words)
        
        if accurate_traits >= 3 and has_reasoning:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! You understand Peter\'s personality very well. He is indeed curious, mischievous, and adventurous.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'misspelled_words': []
            })
        elif accurate_traits >= 2:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Good job! You identified important aspects of Peter\'s personality. He does get into trouble because of his curious nature.',
                'feedback_type': 'good',
                'show_answer': False,
                'misspelled_words': []
            })
        elif accurate_traits >= 1:
            return JsonResponse({
                'isCorrect': True,
                'message': 'You\'re on the right track! Peter does have that trait. Can you think of other ways to describe his personality?',
                'feedback_type': 'partial',
                'show_answer': False,
                'misspelled_words': []
            })
        elif has_negative:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Peter isn\'t really like that. Think about how he acts in the story - he\'s more playful and curious than mean.',
                'feedback_type': 'needs_improvement',
                'show_answer': False,
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about what Peter does in the story. Does he follow rules? Is he curious about things? How does he act?',
                'feedback_type': 'needs_improvement',
                'show_answer': False,
                'misspelled_words': []
            })
    except Exception as e:
        logger.error(f"Error in create_peter_personality_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_question6_answer(request):
    """
    API endpoint to check Peter Rabbit Question 6 answer - Second Main Animal
    """
    try:
        logger.debug(f"Received request: {request.method} {request.path}")
        logger.debug(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        logger.debug(f"User answer: '{user_answer}'")
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please enter an answer.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 2:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please provide a more complete answer.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization'
            })

        # AI-powered analysis for the Peter Rabbit second main animal question
        return analyze_peter_second_animal_answer(user_answer)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in check_peter_question6_answer: {e}", exc_info=True)
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

def analyze_peter_second_animal_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit second main animal answer specifically
    """
    logger.debug(f"Starting AI analysis for second animal answer: '{user_answer}'")
    
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.error("OpenRouter API key not found in environment variables")
        return JsonResponse({
            'error': 'API configuration error. Please contact support.'
        }, status=500)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Second Animal Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified the second main animal in "The Tale of Peter Rabbit". Your task is twofold:
1. Evaluate the correctness of the student's answer about the story "The Tale of Peter Rabbit".
2. Identify any misspelled English words in their answer.

In "The Tale of Peter Rabbit":
- The MAIN animal is Peter Rabbit (a rabbit)
- The SECOND main animal/character is typically Mr. McGregor's Cat or the Birds/Sparrows

CORRECT ANSWERS include:
- "Cat" (Mr. McGregor's cat appears in the story)
- "Bird" or "Birds" (the sparrows that help Peter)
- "Sparrow" or "Sparrows" 
- Other animals that actually appear in the story

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "incorrect",
    "show_answer": true/false,
    "correct_answer": "Cat or Birds",
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines for the SECOND MAIN ANIMAL question:
- If they mention "Cat", "Bird", or "Sparrow", mark as "excellent"
- If they mention other animals that actually appear in the story, mark as "good"
- If they mention animals that might be in similar stories but not this one, mark as "partial"
- If they give the main character (rabbit/Peter) again, gently redirect them to think about OTHER animals
- If they give completely wrong animals, mark as "incorrect"
- Always be encouraging and help them think about the story details
- If isCorrect is false, set show_answer to true
- If isCorrect is true, set show_answer to false

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this second animal answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 250
    }

    try:
        logger.debug(f"Making request to OpenRouter API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                logger.debug(f"Successfully parsed AI response")
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.error(f"AI returned invalid JSON: {e}, Raw response: {result_raw}")
                return create_peter_second_animal_fallback_response(user_answer)
        elif response.status_code == 401:
            logger.error(f"OpenRouter API authentication failed: {response.text}")
            return JsonResponse({
                'error': 'API authentication failed. Please check your API key configuration.'
            }, status=500)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'AI service error ({response.status_code}). Please try again.'
            }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_second_animal_answer: {e}")
        return JsonResponse({
            'error': 'Unable to connect to AI service. Please try again.'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in analyze_peter_second_animal_answer: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Unexpected error occurred. Please try again.'
        }, status=500)

def create_peter_second_animal_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit second animal question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        correct_answer = "Cat or Birds"
        
        # Keywords that indicate correct understanding
        has_cat = 'cat' in user_lower or 'kitten' in user_lower
        has_bird = any(word in user_lower for word in ['bird', 'sparrow', 'robin'])
        has_rabbit_again = 'rabbit' in user_lower or 'peter' in user_lower or 'bunny' in user_lower
        
        # Other story animals that might be mentioned
        other_story_animals = ['mouse', 'frog', 'butterfly']
        has_other_story_animal = any(animal in user_lower for animal in other_story_animals)
        
        # Wrong animals not in the story
        wrong_animals = ['dog', 'bear', 'wolf', 'fox', 'lion', 'tiger', 'elephant', 'cow', 'horse']
        has_wrong_animal = any(animal in user_lower for animal in wrong_animals)
        
        if has_cat:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! The cat is indeed another important animal in Peter Rabbit\'s story. Mr. McGregor\'s cat appears in the tale.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_bird:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Great! Birds do appear in the Peter Rabbit story. The sparrows are mentioned and interact with Peter.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_rabbit_again:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Peter Rabbit is the MAIN character! Think about OTHER animals that appear in the story besides Peter.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_other_story_animal:
            return JsonResponse({
                'isCorrect': True,
                'message': 'That animal might appear in the story! Good thinking about the different creatures in Peter\'s world.',
                'feedback_type': 'good',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_wrong_animal:
            return JsonResponse({
                'isCorrect': False,
                'message': 'That animal doesn\'t appear in Peter Rabbit\'s story. Think about animals that live in gardens or around houses.',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about what other animals Peter encounters in the story. What animals might live in or around Mr. McGregor\'s garden?',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
    except Exception as e:
        logger.error(f"Error in create_peter_second_animal_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_question7_answer(request):
    """
    API endpoint to check Peter Rabbit Question 7 answer - Second Animal Personality
    """
    try:
        logger.debug(f"Received request: {request.method} {request.path}")
        logger.debug(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        logger.debug(f"User answer: '{user_answer}'")
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please enter an answer.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 3:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please provide more details about the personality.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization'
            })

        # AI-powered analysis for the second animal personality question
        return analyze_peter_second_animal_personality_answer(user_answer)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in check_peter_question7_answer: {e}", exc_info=True)
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

def analyze_peter_second_animal_personality_answer(user_answer):
    """
    Use AI to analyze the second animal personality answer specifically
    """
    logger.debug(f"Starting AI analysis for second animal personality answer: '{user_answer}'")
    
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.error("OpenRouter API key not found in environment variables")
        return JsonResponse({
            'error': 'API configuration error. Please contact support.'
        }, status=500)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Second Animal Personality Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified the personality of the second main animal in "The Tale of Peter Rabbit". Your task is twofold:
1. Evaluate the correctness of the student's answer about the personality of secondary characters in the story.
2. Identify any misspelled English words in their answer.

In "The Tale of Peter Rabbit", the main secondary animals include:
- Mr. McGregor's Cat: Often portrayed as watchful, alert, predatory, or cautious
- Birds/Sparrows: Helpful, friendly, warning Peter about danger, protective

Since this is about personality traits of secondary characters, accept descriptions that fit common characteristics of these animals in the story context.

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "needs_improvement",
    "show_answer": false,
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines for the SECOND ANIMAL PERSONALITY question:
- If they describe traits that fit the cat (watchful, alert, predatory, cautious, hunting), mark as "excellent"
- If they describe traits that fit the birds (helpful, friendly, warning, protective, kind), mark as "excellent"
- If they describe general animal traits that could apply (smart, careful, quick), mark as "good"
- If they describe traits that don't really fit the story context, mark as "partial"
- If they describe completely inappropriate traits, mark as "needs_improvement"
- Accept various ways of expressing similar concepts
- Always be encouraging and help them think about how secondary characters behave in stories
- For personality questions, never show a "correct answer" since there can be multiple valid descriptions
- Always set show_answer to false
- If they seem confused about which animal, gently guide them to think about cats or birds

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this second animal personality answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }

    try:
        logger.debug(f"Making request to OpenRouter API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                
                # Set isCorrect based on feedback_type for personality questions
                feedback_type = parsed_result.get('feedback_type', 'needs_improvement')
                parsed_result['isCorrect'] = feedback_type in ['excellent', 'good', 'partial']
                
                logger.debug(f"Successfully parsed AI response")
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.error(f"AI returned invalid JSON: {e}, Raw response: {result_raw}")
                return create_peter_second_animal_personality_fallback_response(user_answer)
        elif response.status_code == 401:
            logger.error(f"OpenRouter API authentication failed: {response.text}")
            return JsonResponse({
                'error': 'API authentication failed. Please check your API key configuration.'
            }, status=500)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'AI service error ({response.status_code}). Please try again.'
            }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_second_animal_personality_answer: {e}")
        return JsonResponse({
            'error': 'Unable to connect to AI service. Please try again.'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in analyze_peter_second_animal_personality_answer: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Unexpected error occurred. Please try again.'
        }, status=500)

def create_peter_second_animal_personality_fallback_response(user_answer):
    """
    Create a fallback response for second animal personality question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        
        # Keywords for cat personality traits
        cat_traits = {
            'watchful': any(word in user_lower for word in ['watchful', 'watching', 'alert', 'observant']),
            'predatory': any(word in user_lower for word in ['hunting', 'predatory', 'stalking', 'dangerous']),
            'cautious': any(word in user_lower for word in ['cautious', 'careful', 'sneaky', 'quiet']),
            'smart': any(word in user_lower for word in ['smart', 'clever', 'intelligent'])
        }
        
        # Keywords for bird personality traits
        bird_traits = {
            'helpful': any(word in user_lower for word in ['helpful', 'helping', 'kind', 'nice']),
            'friendly': any(word in user_lower for word in ['friendly', 'friend', 'caring', 'good']),
            'warning': any(word in user_lower for word in ['warning', 'protective', 'looking out', 'alert']),
            'small': any(word in user_lower for word in ['small', 'little', 'tiny', 'quick'])
        }
        
        # General positive animal traits
        general_traits = ['loyal', 'brave', 'fast', 'strong', 'gentle']
        has_general = any(trait in user_lower for trait in general_traits)
        
        # Inappropriate traits
        negative_traits = ['mean', 'evil', 'scary', 'ugly', 'stupid']
        has_negative = any(trait in user_lower for trait in negative_traits)
        
        # Count trait categories
        cat_score = sum(cat_traits.values())
        bird_score = sum(bird_traits.values())
        
        if cat_score >= 2:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! Those are great personality traits for a cat character. Cats are often watchful and alert in stories.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'misspelled_words': []
            })
        elif bird_score >= 2:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Wonderful! Those traits fit well for bird characters. Birds in stories often help and warn other characters.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'misspelled_words': []
            })
        elif cat_score >= 1 or bird_score >= 1:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Good thinking! That\'s a nice personality trait for an animal character in the story.',
                'feedback_type': 'good',
                'show_answer': False,
                'misspelled_words': []
            })
        elif has_general:
            return JsonResponse({
                'isCorrect': True,
                'message': 'That could work for an animal character! Can you think of more specific traits that fit cats or birds?',
                'feedback_type': 'partial',
                'show_answer': False,
                'misspelled_words': []
            })
        elif has_negative:
            return JsonResponse({
                'isCorrect': False,
                'message': 'The animals in Peter Rabbit aren\'t really like that. Think about more positive traits like how cats watch carefully or birds help others.',
                'feedback_type': 'needs_improvement',
                'show_answer': False,
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about the personality of animals like cats or birds. How do they behave? Are they helpful, watchful, or careful?',
                'feedback_type': 'needs_improvement',
                'show_answer': False,
                'misspelled_words': []
            })
    except Exception as e:
        logger.error(f"Error in create_peter_second_animal_personality_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_question8_answer(request):
    """
    API endpoint to check Peter Rabbit Question 8 answer - Story Setting
    """
    try:
        logger.debug(f"Received request: {request.method} {request.path}")
        logger.debug(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        logger.debug(f"User answer: '{user_answer}'")
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please enter an answer.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 3:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please provide more details about where the story takes place.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization'
            })

        # AI-powered analysis for the Peter Rabbit setting question
        return analyze_peter_setting_answer(user_answer)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in check_peter_question8_answer: {e}", exc_info=True)
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

def analyze_peter_setting_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit setting answer specifically
    """
    logger.debug(f"Starting AI analysis for setting answer: '{user_answer}'")
    
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.error("OpenRouter API key not found in environment variables")
        return JsonResponse({
            'error': 'API configuration error. Please contact support.'
        }, status=500)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Setting Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified where "The Tale of Peter Rabbit" takes place. Your task is twofold:
1. Evaluate the correctness of the student's answer about the story setting.
2. Identify any misspelled English words in their answer.

The main settings in "The Tale of Peter Rabbit" are:
1. Mr. McGregor's garden (where Peter gets into trouble)
2. The woods/countryside (where Peter and his family live)
3. The rabbit burrow/home (under the fir tree)
4. The countryside/rural area in general

CORRECT ANSWERS include any combination of:
- "Mr. McGregor's garden" or "McGregor's garden" or "garden"
- "Woods" / "Forest" / "Countryside" 
- "Under a fir tree" / "rabbit burrow" / "rabbit hole"
- "In the country" / "rural area"
- Any combination of these locations

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "incorrect",
    "show_answer": true/false,
    "correct_answer": "Mr. McGregor's garden and the countryside",
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines for the SETTING question:
- If they mention BOTH the garden AND the woods/countryside, mark as "excellent"
- If they mention ONLY the garden OR ONLY the woods/countryside, mark as "good"
- If they mention related locations (farm, outside, nature), mark as "partial"
- If they give completely wrong locations (city, school, castle), mark as "incorrect"
- Be encouraging and explain the different places where the story happens
- If isCorrect is false, set show_answer to true
- If isCorrect is true, set show_answer to false

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this setting answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }

    try:
        logger.debug(f"Making request to OpenRouter API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                logger.debug(f"Successfully parsed AI response")
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.error(f"AI returned invalid JSON: {e}, Raw response: {result_raw}")
                return create_peter_setting_fallback_response(user_answer)
        elif response.status_code == 401:
            logger.error(f"OpenRouter API authentication failed: {response.text}")
            return JsonResponse({
                'error': 'API authentication failed. Please check your API key configuration.'
            }, status=500)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'AI service error ({response.status_code}). Please try again.'
            }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_setting_answer: {e}")
        return JsonResponse({
            'error': 'Unable to connect to AI service. Please try again.'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in analyze_peter_setting_answer: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Unexpected error occurred. Please try again.'
        }, status=500)

def create_peter_setting_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit setting question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        correct_answer = "Mr. McGregor's garden and the countryside"
        
        # Check for setting mentions
        has_garden = any(word in user_lower for word in ['garden', 'mcgregor', 'vegetable'])
        has_woods = any(word in user_lower for word in ['woods', 'forest', 'countryside', 'country'])
        has_burrow = any(word in user_lower for word in ['burrow', 'hole', 'under', 'fir tree', 'tree'])
        has_outside = any(word in user_lower for word in ['outside', 'outdoors', 'nature'])
        
        # Wrong settings
        wrong_settings = ['city', 'school', 'castle', 'ocean', 'space', 'house', 'indoors']
        has_wrong_setting = any(setting in user_lower for setting in wrong_settings)
        
        if (has_garden and has_woods) or (has_garden and has_burrow):
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! You identified multiple important settings in Peter Rabbit - both the garden where he gets into trouble and his home area.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_garden:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Great! Mr. McGregor\'s garden is definitely where the main action happens. The story also takes place in other outdoor areas.',
                'feedback_type': 'good',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_woods or has_burrow:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Good! Peter does live in the countryside/woods area. The story also takes place in a special garden where he gets into trouble.',
                'feedback_type': 'good',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_outside:
            return JsonResponse({
                'isCorrect': False,
                'message': 'You\'re right that it\'s outside! Can you be more specific about what kind of outdoor places Peter visits?',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_wrong_setting:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Peter Rabbit takes place in outdoor, natural settings. Think about where a rabbit would live and what kind of places he might explore.',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about where Peter lives and where he goes to get into trouble. What outdoor places does he visit?',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
    except Exception as e:
        logger.error(f"Error in create_peter_setting_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_question9_answer(request):
    """
    API endpoint to check Peter Rabbit Question 9 answer - Main Problem
    """
    try:
        logger.debug(f"Received request: {request.method} {request.path}")
        logger.debug(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        logger.debug(f"User answer: '{user_answer}'")
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please enter an answer.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 3:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please provide more details about the main problem in the story.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization'
            })

        # AI-powered analysis for the Peter Rabbit main problem question
        return analyze_peter_main_problem_answer(user_answer)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in check_peter_question9_answer: {e}", exc_info=True)
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

def analyze_peter_main_problem_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit main problem answer specifically
    """
    logger.debug(f"Starting AI analysis for main problem answer: '{user_answer}'")
    
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.error("OpenRouter API key not found in environment variables")
        return JsonResponse({
            'error': 'API configuration error. Please contact support.'
        }, status=500)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Main Problem Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified the main problem in "The Tale of Peter Rabbit". Your task is twofold:
1. Evaluate the correctness of the student's answer about the story's main conflict/problem.
2. Identify any misspelled English words in their answer.

The main problem/conflict in "The Tale of Peter Rabbit" is:
Peter disobeys his mother and goes into Mr. McGregor's garden, where he gets into trouble and is chased by Mr. McGregor.

CORRECT ANSWERS include variations of:
- "Peter goes into Mr. McGregor's garden" / "Peter enters the forbidden garden"
- "Peter disobeys his mother" / "Peter doesn't listen to his mother"
- "Peter gets chased by Mr. McGregor" / "Mr. McGregor chases Peter"
- "Peter gets stuck/trapped in the garden" / "Peter can't escape"
- "Peter eats the vegetables" / "Peter steals from the garden"
- Any combination that shows understanding of the conflict

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "incorrect",
    "show_answer": true/false,
    "correct_answer": "Peter disobeys his mother and gets into trouble in Mr. McGregor's garden",
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines for the MAIN PROBLEM question:
- If they identify the core conflict (Peter's disobedience leading to trouble in the garden), mark as "excellent"
- If they mention key elements but miss some details (like just "Peter gets in trouble"), mark as "good"
- If they identify related problems but not the main one (like "Peter is scared"), mark as "partial"
- If they give unrelated problems or miss the point entirely, mark as "incorrect"
- Always connect the problem to the story's lesson about obedience and consequences
- If isCorrect is false, set show_answer to true
- If isCorrect is true, set show_answer to false

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this main problem answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }

    try:
        logger.debug(f"Making request to OpenRouter API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                logger.debug(f"Successfully parsed AI response")
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.error(f"AI returned invalid JSON: {e}, Raw response: {result_raw}")
                return create_peter_main_problem_fallback_response(user_answer)
        elif response.status_code == 401:
            logger.error(f"OpenRouter API authentication failed: {response.text}")
            return JsonResponse({
                'error': 'API authentication failed. Please check your API key configuration.'
            }, status=500)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'AI service error ({response.status_code}). Please try again.'
            }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_main_problem_answer: {e}")
        return JsonResponse({
            'error': 'Unable to connect to AI service. Please try again.'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in analyze_peter_main_problem_answer: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Unexpected error occurred. Please try again.'
        }, status=500)

def create_peter_main_problem_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit main problem question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        correct_answer = "Peter disobeys his mother and gets into trouble in Mr. McGregor's garden"
        
        # Keywords for different aspects of the main problem
        problem_aspects = {
            'disobedience': any(word in user_lower for word in ['disobey', 'doesn\'t listen', 'broke rule', 'ignored']),
            'garden': any(word in user_lower for word in ['garden', 'mcgregor', 'forbidden', 'shouldn\'t go']),
            'trouble': any(word in user_lower for word in ['trouble', 'problem', 'stuck', 'trapped', 'chased']),
            'eating': any(word in user_lower for word in ['ate', 'eating', 'vegetables', 'food', 'stealing']),
            'mother': any(word in user_lower for word in ['mother', 'mom', 'warned', 'told not to'])
        }
        
        # Secondary problems (not the main conflict)
        secondary_problems = ['scared', 'lost', 'tired', 'hungry', 'sick']
        has_secondary = any(problem in user_lower for problem in secondary_problems)
        
        # Completely wrong problems
        wrong_problems = ['fighting', 'school', 'homework', 'friends', 'weather']
        has_wrong = any(problem in user_lower for problem in wrong_problems)
        
        # Count how many aspects they identified
        problem_score = sum(problem_aspects.values())
        
        if problem_score >= 3:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! You understand the main conflict - Peter\'s disobedience leads to big trouble in the garden.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif problem_score >= 2:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Good job! You identified key parts of the main problem. Peter gets in trouble because he doesn\'t obey his mother.',
                'feedback_type': 'good',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif problem_score >= 1:
            return JsonResponse({
                'isCorrect': False,
                'message': 'You\'re on the right track! Think about WHY Peter gets into this situation. What did he do wrong?',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_secondary:
            return JsonResponse({
                'isCorrect': False,
                'message': 'That happens in the story, but think about the MAIN problem. What causes all the trouble to begin with?',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_wrong:
            return JsonResponse({
                'isCorrect': False,
                'message': 'That\'s not what happens in Peter Rabbit. Think about what Peter does that gets him into trouble.',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about what Peter does wrong and where he goes that he shouldn\'t. What gets him into trouble?',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
    except Exception as e:
        logger.error(f"Error in create_peter_main_problem_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_question10_answer(request):
    """
    API endpoint to check Peter Rabbit Question 10 answer - Story Solution
    """
    try:
        logger.debug(f"Received request: {request.method} {request.path}")
        logger.debug(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        logger.debug(f"User answer: '{user_answer}'")
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please enter an answer.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 3:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please provide more details about how the problem was solved.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization'
            })

        # AI-powered analysis for the Peter Rabbit solution question
        return analyze_peter_solution_answer(user_answer)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in check_peter_question10_answer: {e}", exc_info=True)
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

def analyze_peter_solution_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit solution answer specifically
    """
    logger.debug(f"Starting AI analysis for solution answer: '{user_answer}'")
    
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.error("OpenRouter API key not found in environment variables")
        return JsonResponse({
            'error': 'API configuration error. Please contact support.'
        }, status=500)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Solution Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified how the problem was solved in "The Tale of Peter Rabbit". Your task is twofold:
1. Evaluate the correctness of the student's answer about how Peter's problem was resolved.
2. Identify any misspelled English words in their answer.

The main solution/resolution in "The Tale of Peter Rabbit" includes:
1. Peter escapes from Mr. McGregor's garden (sometimes helped by the sparrows who warn him)
2. He runs away and hides
3. He eventually finds his way home to his mother
4. His mother takes care of him when he gets home sick from his adventure
5. Peter learns his lesson about disobedience (though this may be implied)

CORRECT ANSWERS include variations of:
- "Peter escapes from the garden" / "Peter runs away"
- "Peter gets home safely" / "Peter returns to his mother"
- "His mother takes care of him" / "Mother helps Peter feel better"
- "Peter hides from Mr. McGregor" / "Peter finds a way out"
- "The sparrows help Peter" / "Birds warn Peter"
- "Peter learns his lesson" / "Peter realizes he shouldn't have disobeyed"
- Any combination that shows understanding of how the conflict was resolved

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "incorrect",
    "show_answer": true/false,
    "correct_answer": "Peter escapes from the garden and returns home safely to his mother",
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines for the SOLUTION question:
- If they identify multiple aspects of the resolution (escape + returning home + mother's care), mark as "excellent"
- If they mention the key resolution (Peter escapes/gets home), mark as "good"
- If they mention partial solutions or related events, mark as "partial"
- If they give unrelated or incorrect solutions, mark as "incorrect"
- Always connect the solution to how it resolves the main problem (Peter's disobedience and getting trapped)
- If isCorrect is false, set show_answer to true
- If isCorrect is true, set show_answer to false

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this solution answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }

    try:
        logger.debug(f"Making request to OpenRouter API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                logger.debug(f"Successfully parsed AI response")
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.error(f"AI returned invalid JSON: {e}, Raw response: {result_raw}")
                return create_peter_solution_fallback_response(user_answer)
        elif response.status_code == 401:
            logger.error(f"OpenRouter API authentication failed: {response.text}")
            return JsonResponse({
                'error': 'API authentication failed. Please check your API key configuration.'
            }, status=500)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'AI service error ({response.status_code}). Please try again.'
            }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_solution_answer: {e}")
        return JsonResponse({
            'error': 'Unable to connect to AI service. Please try again.'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in analyze_peter_solution_answer: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Unexpected error occurred. Please try again.'
        }, status=500)

def create_peter_solution_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit solution question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        correct_answer = "Peter escapes from the garden and returns home safely to his mother"
        
        # Keywords for different aspects of the solution
        solution_aspects = {
            'escape': any(word in user_lower for word in ['escape', 'escapes', 'runs away', 'gets away', 'flees']),
            'home': any(word in user_lower for word in ['home', 'returns', 'goes back', 'gets back']),
            'mother': any(word in user_lower for word in ['mother', 'mom', 'mama', 'takes care']),
            'hide': any(word in user_lower for word in ['hide', 'hides', 'hiding', 'hidden']),
            'help': any(word in user_lower for word in ['help', 'helped', 'sparrow', 'bird', 'warn']),
            'safe': any(word in user_lower for word in ['safe', 'safely', 'okay', 'alright']),
            'learn': any(word in user_lower for word in ['learn', 'lesson', 'realizes', 'understands'])
        }
        
        # Wrong solutions
        wrong_solutions = ['fights', 'calls police', 'magic', 'flies away', 'becomes friends']
        has_wrong_solution = any(solution in user_lower for solution in wrong_solutions)
        
        # Count how many solution aspects they identified
        solution_score = sum(solution_aspects.values())
        
        if solution_score >= 3:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! You understand how Peter\'s problem was resolved - he escaped the garden and got home safely where his mother could take care of him.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif solution_score >= 2:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Good job! You identified important parts of how the problem was solved. Peter did manage to resolve his dangerous situation.',
                'feedback_type': 'good',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif solution_score >= 1:
            return JsonResponse({
                'isCorrect': False,
                'message': 'You\'re on the right track! Think about what Peter had to do to get out of his dangerous situation and where he ended up.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_wrong_solution:
            return JsonResponse({
                'isCorrect': False,
                'message': 'That\'s not how the problem was solved in Peter Rabbit. Think about realistic ways Peter could escape from the garden.',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about how Peter got out of the dangerous situation in Mr. McGregor\'s garden and where he went afterwards.',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
    except Exception as e:
        logger.error(f"Error in create_peter_solution_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_question11_answer(request):
    """
    API endpoint to check Peter Rabbit Question 11 answer - Lesson Learned
    """
    try:
        logger.debug(f"Received request: {request.method} {request.path}")
        logger.debug(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        logger.debug(f"User answer: '{user_answer}'")
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please enter an answer.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 3:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please provide more details about what lesson was learned.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization'
            })

        # AI-powered analysis for the Peter Rabbit lesson learned question
        return analyze_peter_lesson_answer(user_answer)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in check_peter_question11_answer: {e}", exc_info=True)
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

def analyze_peter_lesson_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit lesson learned answer specifically
    """
    logger.debug(f"Starting AI analysis for lesson answer: '{user_answer}'")
    
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.error("OpenRouter API key not found in environment variables")
        return JsonResponse({
            'error': 'API configuration error. Please contact support.'
        }, status=500)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Lesson Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified the lesson learned in "The Tale of Peter Rabbit". Your task is twofold:
1. Evaluate the correctness of the student's answer about what lesson Peter (or readers) learned from the story.
2. Identify any misspelled English words in their answer.

The main lessons/morals in "The Tale of Peter Rabbit" include:
1. Listen to your parents/mother (Peter should have listened to his mother's warning)
2. Obey rules and instructions (Peter broke the rule about not going to Mr. McGregor's garden)
3. Disobedience has consequences (Peter got sick and in trouble because he disobeyed)
4. Don't go where you're not supposed to go (the garden was forbidden)
5. Actions have consequences (Peter's adventure led to danger and illness)
6. It's important to follow safety rules (his mother's warning was for his protection)

CORRECT ANSWERS include variations of:
- "Listen to your parents" / "Obey your mother"
- "Don't disobey rules" / "Follow instructions"
- "Actions have consequences" / "Bad choices lead to problems"
- "Don't go where you're not supposed to" / "Stay away from dangerous places"
- "Obedience keeps you safe" / "Rules are there to protect you"
- Any combination that shows understanding of the moral about obedience and consequences

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "incorrect",
    "show_answer": true/false,
    "correct_answer": "Listen to your parents and obey rules, because disobedience has consequences",
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines for the LESSON LEARNED question:
- If they identify the core moral about obedience and consequences, mark as "excellent"
- If they mention key aspects like listening to parents or following rules, mark as "good"
- If they mention related lessons but miss the main point, mark as "partial"
- If they give unrelated or incorrect lessons, mark as "incorrect"
- Always connect the lesson to Peter's specific experience in the story
- Be encouraging and help them understand the moral value of the story
- If isCorrect is false, set show_answer to true
- If isCorrect is true, set show_answer to false

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this lesson answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }

    try:
        logger.debug(f"Making request to OpenRouter API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                logger.debug(f"Successfully parsed AI response")
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.error(f"AI returned invalid JSON: {e}, Raw response: {result_raw}")
                return create_peter_lesson_fallback_response(user_answer)
        elif response.status_code == 401:
            logger.error(f"OpenRouter API authentication failed: {response.text}")
            return JsonResponse({
                'error': 'API authentication failed. Please check your API key configuration.'
            }, status=500)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'AI service error ({response.status_code}). Please try again.'
            }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_lesson_answer: {e}")
        return JsonResponse({
            'error': 'Unable to connect to AI service. Please try again.'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in analyze_peter_lesson_answer: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Unexpected error occurred. Please try again.'
        }, status=500)

def create_peter_lesson_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit lesson learned question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        correct_answer = "Listen to your parents and obey rules, because disobedience has consequences"
        
        # Keywords for different aspects of the lesson
        lesson_aspects = {
            'obedience': any(word in user_lower for word in ['obey', 'listen', 'follow', 'do what', 'told']),
            'parents': any(word in user_lower for word in ['parent', 'mother', 'mom', 'mama']),
            'rules': any(word in user_lower for word in ['rule', 'instruction', 'warning', 'command']),
            'consequences': any(word in user_lower for word in ['consequence', 'trouble', 'danger', 'punishment', 'problem']),
            'disobedience': any(word in user_lower for word in ['disobey', 'don\'t listen', 'ignore', 'break rule']),
            'safety': any(word in user_lower for word in ['safe', 'protect', 'danger', 'careful', 'harm']),
            'bad_choices': any(word in user_lower for word in ['bad choice', 'wrong', 'mistake', 'shouldn\'t'])
        }
        
        # General positive lessons (related but not specific)
        general_lessons = ['be good', 'be nice', 'help others', 'share', 'be kind']
        has_general_lesson = any(lesson in user_lower for lesson in general_lessons)
        
        # Unrelated lessons
        wrong_lessons = ['brush teeth', 'do homework', 'exercise', 'eat vegetables']
        has_wrong_lesson = any(lesson in user_lower for lesson in wrong_lessons)
        
        # Count how many lesson aspects they identified
        lesson_score = sum(lesson_aspects.values())
        
        if lesson_score >= 3:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! You understand the main lesson - Peter learned that disobeying his mother led to serious consequences and danger.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif lesson_score >= 2:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Good job! You identified important parts of the lesson Peter learned about obedience and consequences.',
                'feedback_type': 'good',
                'show_answer': False,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif lesson_score >= 1:
            return JsonResponse({
                'isCorrect': False,
                'message': 'You\'re on the right track! Think about what Peter should have done differently and why his mother gave him that warning.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_general_lesson:
            return JsonResponse({
                'isCorrect': False,
                'message': 'That\'s a good lesson in general, but think specifically about what Peter learned from his adventure in the garden.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        elif has_wrong_lesson:
            return JsonResponse({
                'isCorrect': False,
                'message': 'That lesson isn\'t from Peter Rabbit\'s story. Think about what happened when Peter didn\'t listen to his mother.',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about what Peter should have learned from his dangerous experience. What did his mother warn him about?',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer,
                'misspelled_words': []
            })
    except Exception as e:
        logger.error(f"Error in create_peter_lesson_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_question12_answer(request):
    """
    API endpoint to check Peter Rabbit Question 12 answer - Favourite Character
    """
    try:
        logger.debug(f"Received request: {request.method} {request.path}")
        logger.debug(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        logger.debug(f"User answer: '{user_answer}'")
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please enter an answer.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 5:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please tell us more about your favourite character and explain why you like them.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization'
            })

        # AI-powered analysis for the Peter Rabbit favourite character question
        return analyze_peter_favourite_character_answer(user_answer)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in check_peter_question12_answer: {e}", exc_info=True)
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

def analyze_peter_favourite_character_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit favourite character answer specifically
    """
    logger.debug(f"Starting AI analysis for favourite character answer: '{user_answer}'")
    
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.error("OpenRouter API key not found in environment variables")
        return JsonResponse({
            'error': 'API configuration error. Please contact support.'
        }, status=500)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Favourite Character Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student provided a thoughtful answer about their favourite character in "The Tale of Peter Rabbit". Your task is twofold:
1. Evaluate whether the student identified a character from the story and provided reasoning for their choice.
2. Identify any misspelled English words in their answer.

Characters in "The Tale of Peter Rabbit" include:
- Peter Rabbit (the main character)
- Mother Rabbit (Peter's mother)
- Mr. McGregor (the farmer/gardener)
- Flopsy, Mopsy, and Cotton-tail (Peter's sisters)
- The Cat (Mr. McGregor's cat)
- The Sparrows/Birds (who help Peter)

This is a PERSONAL OPINION question - there is no "wrong" character choice. The key is that students should:
1. Name a character that actually appears in the story
2. Provide some reasoning for why they like that character
3. Show understanding of the character's role or personality

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "needs_improvement",
    "show_answer": false,
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines for the FAVOURITE CHARACTER question:
- If they name a story character AND give good reasoning, mark as "excellent"
- If they name a story character with basic reasoning, mark as "good"
- If they name a story character but with unclear reasoning, mark as "partial"
- If they name a character not in the story or give no reasoning, mark as "needs_improvement"
- Always be encouraging about their personal choice while checking story accuracy
- For opinion questions, never show a "correct answer" since all character preferences are valid
- Always set show_answer to false
- Focus on whether they understand the characters and can express their thoughts

Examples of good reasoning:
- Character traits (brave, curious, caring, etc.)
- Actions in the story (helps others, learns lessons, etc.)
- Relatability (reminds them of themselves, etc.)
- Story role (main character, protector, etc.)

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this favourite character answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }

    try:
        logger.debug(f"Making request to OpenRouter API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                
                # Set isCorrect based on feedback_type for opinion questions
                feedback_type = parsed_result.get('feedback_type', 'needs_improvement')
                parsed_result['isCorrect'] = feedback_type in ['excellent', 'good', 'partial']
                
                logger.debug(f"Successfully parsed AI response")
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.error(f"AI returned invalid JSON: {e}, Raw response: {result_raw}")
                return create_peter_favourite_character_fallback_response(user_answer)
        elif response.status_code == 401:
            logger.error(f"OpenRouter API authentication failed: {response.text}")
            return JsonResponse({
                'error': 'API authentication failed. Please check your API key configuration.'
            }, status=500)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'AI service error ({response.status_code}). Please try again.'
            }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_favourite_character_answer: {e}")
        return JsonResponse({
            'error': 'Unable to connect to AI service. Please try again.'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in analyze_peter_favourite_character_answer: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Unexpected error occurred. Please try again.'
        }, status=500)

def create_peter_favourite_character_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit favourite character question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        
        # Story characters
        story_characters = {
            'peter': any(word in user_lower for word in ['peter', 'peter rabbit']),
            'mother': any(word in user_lower for word in ['mother', 'mom', 'mama', 'mother rabbit']),
            'mcgregor': any(word in user_lower for word in ['mcgregor', 'mr mcgregor', 'farmer', 'gardener']),
            'sisters': any(word in user_lower for word in ['flopsy', 'mopsy', 'cotton-tail', 'cotton tail', 'sister']),
            'cat': any(word in user_lower for word in ['cat', 'kitten']),
            'birds': any(word in user_lower for word in ['bird', 'sparrow', 'robin'])
        }
        
        # Reasoning indicators
        reasoning_indicators = {
            'traits': any(word in user_lower for word in ['brave', 'curious', 'adventurous', 'kind', 'caring', 'funny', 'clever', 'smart']),
            'actions': any(word in user_lower for word in ['helps', 'saves', 'protects', 'learns', 'tries', 'escapes']),
            'relatability': any(word in user_lower for word in ['like me', 'reminds me', 'similar', 'relate']),
            'because': 'because' in user_lower or 'why' in user_lower or 'reason' in user_lower
        }
        
        # Characters not in the story
        wrong_characters = ['harry potter', 'elsa', 'spiderman', 'batman', 'cinderella']
        has_wrong_character = any(char in user_lower for char in wrong_characters)
        
        # Count story characters mentioned and reasoning provided
        character_mentioned = sum(story_characters.values())
        reasoning_provided = sum(reasoning_indicators.values())
        
        if character_mentioned >= 1 and reasoning_provided >= 2:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! You chose a character from the story and gave thoughtful reasons for your choice. Great personal reflection!',
                'feedback_type': 'excellent',
                'show_answer': False,
                'misspelled_words': []
            })
        elif character_mentioned >= 1 and reasoning_provided >= 1:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Good choice! You picked a character from Peter Rabbit and explained why you like them. Nice thinking!',
                'feedback_type': 'good',
                'show_answer': False,
                'misspelled_words': []
            })
        elif character_mentioned >= 1:
            return JsonResponse({
                'isCorrect': True,
                'message': 'You chose a character from the story! Can you tell us more about WHY you like this character?',
                'feedback_type': 'partial',
                'show_answer': False,
                'misspelled_words': []
            })
        elif has_wrong_character:
            return JsonResponse({
                'isCorrect': False,
                'message': 'That character isn\'t in Peter Rabbit\'s story. Choose someone from the Peter Rabbit tale and tell us why you like them.',
                'feedback_type': 'needs_improvement',
                'show_answer': False,
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please choose a character from the Peter Rabbit story and explain why they are your favourite.',
                'feedback_type': 'needs_improvement',
                'show_answer': False,
                'misspelled_words': []
            })
    except Exception as e:
        logger.error(f"Error in create_peter_favourite_character_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_question13_answer(request):
    """
    API endpoint to check Peter Rabbit Question 13 answer - Reading Feelings
    """
    try:
        logger.debug(f"Received request: {request.method} {request.path}")
        logger.debug(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        logger.debug(f"User answer: '{user_answer}'")
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please enter an answer.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 3:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please tell us more about how you felt while reading the story.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization'
            })

        # AI-powered analysis for the Peter Rabbit reading feelings question
        return analyze_peter_reading_feelings_answer(user_answer)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in check_peter_question13_answer: {e}", exc_info=True)
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

def analyze_peter_reading_feelings_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit reading feelings answer specifically
    """
    logger.debug(f"Starting AI analysis for reading feelings answer: '{user_answer}'")
    
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.error("OpenRouter API key not found in environment variables")
        return JsonResponse({
            'error': 'API configuration error. Please contact support.'
        }, status=500)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Reading Feelings Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student shared their feelings about reading "The Tale of Peter Rabbit". Your task is twofold:
1. Evaluate whether the student expressed genuine feelings/emotions about their reading experience.
2. Identify any misspelled English words in their answer.

This is a PERSONAL REFLECTION question about emotions and feelings. Common feelings while reading Peter Rabbit might include:

POSITIVE FEELINGS:
- Excited, thrilled, entertained
- Happy, joyful, amused
- Curious, interested, engaged
- Surprised, amazed
- Relieved (when Peter escapes)

CONCERNED/TENSE FEELINGS:
- Worried, nervous, anxious (about Peter's safety)
- Scared, frightened (during dangerous parts)
- Tense, suspenseful (wondering what happens next)
- Concerned (for Peter's wellbeing)

MIXED/COMPLEX FEELINGS:
- Proud of Peter but worried about his choices
- Entertained but nervous
- Happy and relieved

There are NO wrong emotional responses - this is about personal reflection and emotional literacy.

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "needs_improvement",
    "show_answer": false,
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines for the READING FEELINGS question:
- If they express clear, specific emotions with some explanation, mark as "excellent"
- If they mention emotions but with basic description, mark as "good"
- If they mention feelings but unclear or vague, mark as "partial"
- If they don't mention emotions or give non-emotional responses, mark as "needs_improvement"
- Always validate their emotional experience while encouraging reflection
- For feelings questions, never show a "correct answer" since all emotions are valid
- Always set show_answer to false
- Focus on emotional expression and personal connection to the story

Examples of good responses:
- "I felt excited when Peter was exploring"
- "I was worried he would get caught"
- "Happy and scared at the same time"
- "Nervous but couldn't stop reading"

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this reading feelings answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }

    try:
        logger.debug(f"Making request to OpenRouter API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                
                # Set isCorrect based on feedback_type for feelings questions
                feedback_type = parsed_result.get('feedback_type', 'needs_improvement')
                parsed_result['isCorrect'] = feedback_type in ['excellent', 'good', 'partial']
                
                logger.debug(f"Successfully parsed AI response")
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.error(f"AI returned invalid JSON: {e}, Raw response: {result_raw}")
                return create_peter_reading_feelings_fallback_response(user_answer)
        elif response.status_code == 401:
            logger.error(f"OpenRouter API authentication failed: {response.text}")
            return JsonResponse({
                'error': 'API authentication failed. Please check your API key configuration.'
            }, status=500)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'AI service error ({response.status_code}). Please try again.'
            }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_reading_feelings_answer: {e}")
        return JsonResponse({
            'error': 'Unable to connect to AI service. Please try again.'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in analyze_peter_reading_feelings_answer: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Unexpected error occurred. Please try again.'
        }, status=500)

def create_peter_reading_feelings_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit reading feelings question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        
        # Emotion words - positive
        positive_emotions = {
            'happy': any(word in user_lower for word in ['happy', 'joyful', 'cheerful', 'glad', 'delighted']),
            'excited': any(word in user_lower for word in ['excited', 'thrilled', 'amazed', 'enthusiastic']),
            'entertained': any(word in user_lower for word in ['entertained', 'amused', 'fun', 'funny', 'enjoyed']),
            'curious': any(word in user_lower for word in ['curious', 'interested', 'wonder', 'wanted to know'])
        }
        
        # Emotion words - concerned/tense
        concerned_emotions = {
            'worried': any(word in user_lower for word in ['worried', 'concerned', 'anxious', 'nervous']),
            'scared': any(word in user_lower for word in ['scared', 'frightened', 'afraid', 'fearful']),
            'tense': any(word in user_lower for word in ['tense', 'suspense', 'edge', 'nervous', 'anxious'])
        }
        
        # Mixed emotions
        mixed_emotions = {
            'mixed': any(word in user_lower for word in ['both', 'mixed', 'confused', 'complicated']),
            'relieved': any(word in user_lower for word in ['relieved', 'glad when', 'better when'])
        }
        
        # Explanation indicators
        explanation_indicators = {
            'because': 'because' in user_lower,
            'when': any(word in user_lower for word in ['when', 'during', 'while']),
            'story_events': any(word in user_lower for word in ['peter', 'garden', 'chase', 'escape', 'danger'])
        }
        
        # Non-emotional responses
        non_emotional = ['it was good', 'it was okay', 'fine', 'boring', 'don\'t know']
        has_non_emotional = any(phrase in user_lower for phrase in non_emotional)
        
        # Count emotional expressions and explanations
        positive_score = sum(positive_emotions.values())
        concerned_score = sum(concerned_emotions.values())
        mixed_score = sum(mixed_emotions.values())
        total_emotions = positive_score + concerned_score + mixed_score
        explanation_score = sum(explanation_indicators.values())
        
        if total_emotions >= 2 and explanation_score >= 2:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Wonderful! You shared detailed feelings about your reading experience. It\'s great that you connected emotionally with Peter\'s adventure!',
                'feedback_type': 'excellent',
                'show_answer': False,
                'misspelled_words': []
            })
        elif total_emotions >= 1 and explanation_score >= 1:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Great job sharing your feelings! You made a personal connection to the story and Peter\'s experiences.',
                'feedback_type': 'good',
                'show_answer': False,
                'misspelled_words': []
            })
        elif total_emotions >= 1:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Good! You expressed how you felt. Can you tell us more about WHEN you felt that way during the story?',
                'feedback_type': 'partial',
                'show_answer': False,
                'misspelled_words': []
            })
        elif has_non_emotional:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Try to think about your FEELINGS and emotions while reading. Were you excited, worried, happy, nervous? How did Peter\'s adventure make you feel?',
                'feedback_type': 'needs_improvement',
                'show_answer': False,
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please share your emotions and feelings while reading Peter\'s story. For example, were you excited, worried, happy, or scared during different parts?',
                'feedback_type': 'needs_improvement',
                'show_answer': False,
                'misspelled_words': []
            })
    except Exception as e:
        logger.error(f"Error in create_peter_reading_feelings_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_question14_answer(request):
    """
    API endpoint to check Peter Rabbit Question 14 answer - Story Part Analysis
    """
    try:
        logger.debug(f"Received request: {request.method} {request.path}")
        logger.debug(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        logger.debug(f"User answer: '{user_answer}'")
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please enter an answer.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 5:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please tell us more about which specific part of the story made you feel that way.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization'
            })

        # AI-powered analysis for the Peter Rabbit story part analysis question
        return analyze_peter_story_part_answer(user_answer)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in check_peter_question14_answer: {e}", exc_info=True)
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

def analyze_peter_story_part_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit story part answer specifically
    """
    logger.debug(f"Starting AI analysis for story part answer: '{user_answer}'")
    
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.error("OpenRouter API key not found in environment variables")
        return JsonResponse({
            'error': 'API configuration error. Please contact support.'
        }, status=500)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Story Part Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student identified a specific part of "The Tale of Peter Rabbit" that made them feel a certain way. Your task is twofold:
1. Evaluate whether the student referenced a specific story event, scene, or moment from Peter Rabbit.
2. Identify any misspelled English words in their answer.

This question follows up on emotional reflection by asking students to connect their feelings to specific story parts. 

Key story events/parts in "The Tale of Peter Rabbit":
- Beginning: Mother warning Peter not to go to Mr. McGregor's garden
- Peter entering the forbidden garden
- Peter eating vegetables in the garden
- Mr. McGregor discovering Peter
- The chase scene through the garden
- Peter getting stuck in the gooseberry net
- Peter hiding and trying to escape
- The sparrows helping or warning Peter
- Peter losing his jacket and shoes
- Peter finally escaping the garden
- Peter returning home sick and tired
- Mother putting Peter to bed with medicine
- The contrast with his good sisters getting treats

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "needs_improvement",
    "show_answer": false,
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines for the STORY PART question:
- If they identify a specific story event AND connect it to emotion, mark as "excellent"
- If they mention a story part but with less specific connection, mark as "good"
- If they reference the story generally but not a specific part, mark as "partial"
- If they don't reference the story or give unrelated answers, mark as "needs_improvement"
- Always validate their emotional connection while checking story accuracy
- For reflection questions, never show a "correct answer" since personal connections vary
- Always set show_answer to false
- Focus on whether they can connect emotions to specific narrative moments

Examples of good responses:
- "When Peter was being chased by Mr. McGregor"
- "The part where Peter got stuck in the net"
- "When Peter first entered the garden"
- "When Peter made it home safely to his mother"

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this story part answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }

    try:
        logger.debug(f"Making request to OpenRouter API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                
                # Set isCorrect based on feedback_type for story analysis questions
                feedback_type = parsed_result.get('feedback_type', 'needs_improvement')
                parsed_result['isCorrect'] = feedback_type in ['excellent', 'good', 'partial']
                
                logger.debug(f"Successfully parsed AI response")
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.error(f"AI returned invalid JSON: {e}, Raw response: {result_raw}")
                return create_peter_story_part_fallback_response(user_answer)
        elif response.status_code == 401:
            logger.error(f"OpenRouter API authentication failed: {response.text}")
            return JsonResponse({
                'error': 'API authentication failed. Please check your API key configuration.'
            }, status=500)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'AI service error ({response.status_code}). Please try again.'
            }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_story_part_answer: {e}")
        return JsonResponse({
            'error': 'Unable to connect to AI service. Please try again.'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in analyze_peter_story_part_answer: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Unexpected error occurred. Please try again.'
        }, status=500)

def create_peter_story_part_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit story part question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        
        # Specific story events and scenes
        story_events = {
            'garden_entry': any(word in user_lower for word in ['entered garden', 'went into garden', 'going to garden', 'in the garden']),
            'chase_scene': any(word in user_lower for word in ['chase', 'chased', 'running', 'mcgregor chasing', 'being chased']),
            'getting_caught': any(word in user_lower for word in ['stuck', 'trapped', 'caught', 'net', 'gooseberry']),
            'eating': any(word in user_lower for word in ['eating', 'ate', 'vegetables', 'lettuces', 'radishes']),
            'hiding': any(word in user_lower for word in ['hiding', 'hid', 'shed', 'watering can']),
            'escape': any(word in user_lower for word in ['escape', 'escaped', 'getting away', 'got away']),
            'returning_home': any(word in user_lower for word in ['home', 'mother', 'came back', 'returned']),
            'warning': any(word in user_lower for word in ['mother warned', 'warning', 'told not to']),
            'ending': any(word in user_lower for word in ['end', 'ending', 'medicine', 'bed', 'sick'])
        }
        
        # Characters and specific references
        story_references = {
            'peter': 'peter' in user_lower,
            'mcgregor': any(word in user_lower for word in ['mcgregor', 'mr mcgregor', 'farmer']),
            'mother': any(word in user_lower for word in ['mother', 'mom']),
            'birds': any(word in user_lower for word in ['bird', 'sparrow'])
        }
        
        # Emotional connection indicators
        emotional_connection = {
            'when': 'when' in user_lower,
            'part': any(word in user_lower for word in ['part', 'scene', 'moment', 'time']),
            'because': 'because' in user_lower
        }
        
        # Non-specific or unrelated responses
        non_specific = ['whole story', 'everything', 'all of it', 'don\'t know']
        has_non_specific = any(phrase in user_lower for phrase in non_specific)
        
        # Count story elements and connections
        events_mentioned = sum(story_events.values())
        references_made = sum(story_references.values())
        connections_made = sum(emotional_connection.values())
        
        if events_mentioned >= 1 and connections_made >= 1:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent connection! You identified a specific part of Peter\'s story and linked it to your feelings. That\'s exactly how good readers connect with stories!',
                'feedback_type': 'excellent',
                'show_answer': False,
                'misspelled_words': []
            })
        elif events_mentioned >= 1 or references_made >= 1:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Good job mentioning a part of Peter\'s story! You\'re making connections between the story and your feelings.',
                'feedback_type': 'good',
                'show_answer': False,
                'misspelled_words': []
            })
        elif 'peter' in user_lower or 'story' in user_lower:
            return JsonResponse({
                'isCorrect': True,
                'message': 'You\'re thinking about Peter\'s story! Can you be more specific about which exact part or scene made you feel that way?',
                'feedback_type': 'partial',
                'show_answer': False,
                'misspelled_words': []
            })
        elif has_non_specific:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Try to think of one specific scene or moment in Peter\'s adventure. Was it when he entered the garden, when he was chased, or when he got home?',
                'feedback_type': 'needs_improvement',
                'show_answer': False,
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please tell us about a specific part of Peter Rabbit\'s story that made you feel a certain way. Think about particular scenes or moments.',
                'feedback_type': 'needs_improvement',
                'show_answer': False,
                'misspelled_words': []
            })
    except Exception as e:
        logger.error(f"Error in create_peter_story_part_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })