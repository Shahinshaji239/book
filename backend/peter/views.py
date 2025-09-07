import json
import os
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

@csrf_exempt
def health_check(request):
    """
    Simple health check endpoint
    """
    return JsonResponse({
        'status': 'ok',
        'message': 'Peter Rabbit API is working!'
    })

@csrf_exempt
@require_http_methods(["POST"])
def check_peter_question1_answer(request):
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
    api_key = os.getenv('OPENROUTER_API_KEY2')
    if not api_key:
        return create_peter_title_fallback_response(user_answer)

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
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                return JsonResponse(parsed_result)
            except json.JSONDecodeError:
                return create_peter_title_fallback_response(user_answer)
        
        return JsonResponse({
            'error': f'AI service temporarily unavailable. Please try again.'
        }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_title_answer: {e}")
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
                'correct_answer': correct_title
            })
        elif has_peter and has_rabbit:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Great! You have the main characters. The full title also mentions it being a "Tale".',
                'feedback_type': 'good',
                'show_answer': False,
                'correct_answer': correct_title
            })
        elif has_peter:
            return JsonResponse({
                'isCorrect': False,
                'message': 'You got the main character! But the title also includes another important word about what kind of animal Peter is.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_title
            })
        elif has_rabbit:
            return JsonResponse({
                'isCorrect': False,
                'message': 'You identified the type of animal, but you are missing the main character\'s name.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_title
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about the main character in this story - what is his name and what kind of animal is he?',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_title
            })
    except Exception as e:
        logger.error(f"Error in create_peter_title_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_peter_question2_answer(request):
    """
    API endpoint to check Peter Rabbit Question 2 answer - Story Author
    """
    try:
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        logger.debug(f"Peter Rabbit Question 2 - Received answer: {user_answer}")
        
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
        logger.error(f"Unexpected error in check_peter_question2_answer: {e}")
        return JsonResponse({'error': 'Internal server error.'}, status=500)


def analyze_peter_author_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit author answer specifically
    """
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.warning("OpenRouter API key not found, using fallback")
        return create_peter_author_fallback_response(user_answer)

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

IMPORTANT CONTEXT: "The Tale of Peter Rabbit" was written by Beatrix Potter. She was a British author who created the beloved Peter Rabbit stories in the early 1900s.

CORRECT ANSWERS include:
- "Beatrix Potter"
- "Beatrice Potter" (alternative spelling)
- Any reasonable variation of the name

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
- If they mention "Beatrix Potter" or close variations, mark as correct
- If they give a completely wrong author (like "Dr. Seuss"), mark as incorrect
- If they show some understanding but get the name wrong, mark as partial
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
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                # Try to parse JSON response
                parsed_result = json.loads(result_raw)
                # Ensure the response has the correct format
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.warning(f"AI JSON decode error: {e}, using fallback")
                # Fallback if AI doesn't return proper JSON
                return create_peter_author_fallback_response(user_answer)
        
        logger.error(f"OpenRouter API error: {response.status_code}")
        return JsonResponse({
            'error': f'AI service temporarily unavailable. Please try again.'
        }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception: {e}")
        return JsonResponse({
            'error': 'Unable to check answer right now. Please try again.'
        }, status=500)


def create_peter_author_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit author question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        correct_answer = "Beatrix Potter"
        
        # Keywords that indicate correct understanding
        correct_keywords = ['beatrix', 'potter', 'beatrice']
        
        # Obviously wrong authors
        wrong_authors = ['dr. seuss', 'roald dahl', 'j.k. rowling', 'disney', 
                        'brothers grimm', 'hans christian andersen']
        
        # Check if they understand it's Beatrix Potter
        has_correct_author = any(keyword in user_lower for keyword in correct_keywords)
        has_wrong_author = any(wrong in user_lower for wrong in wrong_authors)
        
        if has_correct_author:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! Beatrix Potter is the correct author of The Tale of Peter Rabbit.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': correct_answer
            })
        elif has_wrong_author:
            return JsonResponse({
                'isCorrect': False,
                'message': 'That author didn\'t write this story. Peter Rabbit was created by a British author in the early 1900s.',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about the British author who created the Peter Rabbit stories in the early 1900s.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_answer
            })
    except Exception as e:
        logger.error(f"Peter author fallback error: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False
        })

def check_peter_question1_answer(request):
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
    api_key = os.getenv('OPENROUTER_API_KEY2')
    if not api_key:
        return create_peter_title_fallback_response(user_answer)

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
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                return JsonResponse(parsed_result)
            except json.JSONDecodeError:
                return create_peter_title_fallback_response(user_answer)
        
        return JsonResponse({
            'error': f'AI service temporarily unavailable. Please try again.'
        }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_title_answer: {e}")
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
                'correct_answer': correct_title
            })
        elif has_peter and has_rabbit:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Great! You have the main characters. The full title also mentions it being a "Tale".',
                'feedback_type': 'good',
                'show_answer': False,
                'correct_answer': correct_title
            })
        elif has_peter:
            return JsonResponse({
                'isCorrect': False,
                'message': 'You got the main character! But the title also includes another important word about what kind of animal Peter is.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_title
            })
        elif has_rabbit:
            return JsonResponse({
                'isCorrect': False,
                'message': 'You identified the type of animal, but you are missing the main character\'s name.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_title
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about the main character in this story - what is his name and what kind of animal is he?',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_title
            })
    except Exception as e:
        logger.error(f"Error in create_peter_title_fallback_response: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False
        })

# ========== QUESTION 2: STORY AUTHOR ==========

@csrf_exempt
@require_http_methods(["POST"])
def check_peter_question2_answer(request):
    """
    API endpoint to check Peter Rabbit Question 2 answer - Story Author
    """
    try:
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        logger.debug(f"Peter Question 2 - Received answer: {user_answer}")
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please enter an answer.'
            }, status=400)

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

        return analyze_peter_author_answer(user_answer)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in check_peter_question2_answer: {e}")
        return JsonResponse({'error': 'Internal server error.'}, status=500)


def analyze_peter_author_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit author answer specifically
    """
    api_key = os.getenv('OPENROUTER_API_KEY2')
    logger.debug(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.warning("OpenRouter API key not found, using fallback")
        return create_peter_author_fallback_response(user_answer)

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

IMPORTANT CONTEXT: "The Tale of Peter Rabbit" was written by Beatrix Potter, a famous British author and illustrator who wrote and illustrated many beloved children's books featuring animals.

CORRECT ANSWERS include:
- "Beatrix Potter"
- "Beatrix Helen Potter" (her full name)
- Any reasonable variation of her name

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

Guidelines:
- If they mention "Beatrix Potter" in any reasonable form, mark as correct
- If they give a completely wrong author name, mark as incorrect
- If they show partial understanding but wrong name, provide gentle correction
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
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.debug(f"OpenRouter response status: {response.status_code}")
        
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            logger.debug(f"OpenRouter raw response: {result_raw}")
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                return JsonResponse(parsed_result)
            except json.JSONDecodeError as e:
                logger.warning(f"AI JSON decode error: {e}, using fallback")
                return create_peter_author_fallback_response(user_answer)
        
        logger.error(f"OpenRouter API error: {response.status_code}")
        return create_peter_author_fallback_response(user_answer)

    except requests.RequestException as e:
        logger.error(f"Request exception: {e}")
        return create_peter_author_fallback_response(user_answer)


def create_peter_author_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit author question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        correct_answer = "Beatrix Potter"
        
        # Check for Beatrix Potter variations
        if 'beatrix' in user_lower and 'potter' in user_lower:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! Beatrix Potter is indeed the author of The Tale of Peter Rabbit.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': correct_answer
            })
        elif 'beatrix' in user_lower:
            return JsonResponse({
                'isCorrect': False,
                'message': 'You got the first name right! What is Beatrix\'s last name?',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_answer
            })
        elif 'potter' in user_lower:
            return JsonResponse({
                'isCorrect': False,
                'message': 'You got the last name right! What is the author\'s first name?',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_answer
            })
        else:
            # Check for obviously wrong authors
            wrong_authors = ['dr. seuss', 'roald dahl', 'j.k. rowling', 'disney', 'brothers grimm']
            has_wrong_author = any(wrong in user_lower for wrong in wrong_authors)
            
            if has_wrong_author:
                return JsonResponse({
                    'isCorrect': False,
                    'message': 'That author didn\'t write this story. The Tale of Peter Rabbit was written by a famous British author who also illustrated her books.',
                    'feedback_type': 'incorrect',
                    'show_answer': True,
                    'correct_answer': correct_answer
                })
            else:
                return JsonResponse({
                    'isCorrect': False,
                    'message': 'Think about the British author who wrote and illustrated this classic children\'s story in the early 1900s.',
                    'feedback_type': 'incorrect',
                    'show_answer': True,
                    'correct_answer': correct_answer
                })
    except Exception as e:
        logger.error(f"Peter author fallback error: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False
        })

# Health check endpoint
@csrf_exempt
def peter_health_check(request):
    """
    Simple health check endpoint for Peter Rabbit activities
    """
    return JsonResponse({
        'status': 'ok',
        'message': 'Peter Rabbit API is working!',
        'available_endpoints': [
            '/api/check-peter-question1/',
            '/api/check-peter-question2/',
            # Add more as they are created
        ]
    })

@csrf_exempt
@require_http_methods(["POST"])
def check_peter_question3_answer(request):
    """
    API endpoint to check Peter Rabbit Question 3 answer - Story Genre
    """
    try:
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        if not user_answer:
            return JsonResponse({'error': 'Please select an answer.'}, status=400)

        # AI-powered analysis for the genre question
        return analyze_peter_genre_answer(user_answer)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def analyze_peter_genre_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit genre answer specifically
    """
    api_key = os.getenv('OPENROUTER_API_KEY2')
    if not api_key:
        return check_peter_genre_manually(user_answer)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified the genre of "The Tale of Peter Rabbit". Your task is twofold:
1. Evaluate the correctness of the student's answer about the story "The Tale of Peter Rabbit".
2. Identify any misspelled English words in their answer.

The correct broad genre is "Fiction". Other related correct answers include "fairy tale", "folk tale", "children's story", or "made-up story".

IMPORTANT: The entire response must be a single, valid JSON object. Do not include any text outside of the JSON structure.
Example valid response:
{{
    "isCorrect": true,
    "message": "Excellent! 'Fiction' is the perfect genre because the story is imaginary and features talking animals.",
    "feedback_type": "excellent",
    "show_answer": false,
    "correct_answer": "Fiction",
    "misspelled_words": []
}}

Guidelines for the GENRE question:
- If the answer is "Fiction" or a very close synonym (like "fairy tale", "children's story", "imaginary"), mark as correct and explain WHY (it's a made-up story with talking animals).
- If the answer is "Non-Fiction", mark as incorrect and explain the difference.
- If the answer is a sub-genre like "Comedy", "Adventure", or "Drama", acknowledge their good thinking but explain that the broader category is "Fiction". Mark as "partial" or "good" but not fully correct.
- Always be encouraging and educational. If isCorrect is false, set show_answer to true.

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "system", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 300,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            # Get the JSON string from the AI's response and parse it
            ai_response_string = response.json()['choices'][0]['message']['content']
            data = json.loads(ai_response_string)
            return JsonResponse(data)
            
        return check_peter_genre_manually(user_answer)
    except requests.RequestException:
        return check_peter_genre_manually(user_answer)


def check_peter_genre_manually(user_answer):
    """
    Simple manual checking for Peter Rabbit genre question
    """
    if user_answer == 'Fiction':
        return JsonResponse({
            'isCorrect': True,
            'message': 'Excellent! You\'re absolutely right. The Tale of Peter Rabbit is fiction because it features imaginary characters and talking animals. Fiction stories are made-up tales like fairy tales, novels, and fantasy stories.',
            'feedback_type': 'excellent',
            'show_answer': False,
            'correct_answer': 'Fiction'
        })
    
    elif user_answer == 'Non-Fiction':
        return JsonResponse({
            'isCorrect': False,
            'message': 'Not quite! The Tale of Peter Rabbit is actually fiction because it\'s an imaginary story with made-up characters and talking animals. Non-fiction would be true stories about real people, historical events, biographies, or factual information.',
            'feedback_type': 'incorrect',
            'show_answer': True,
            'correct_answer': 'Fiction'
        })
    
    else:
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please select either Fiction or Non-Fiction.',
            'feedback_type': 'guidance',
            'show_answer': False,
            'correct_answer': 'Fiction'
        })

    
@csrf_exempt
@require_http_methods(["POST"])
def check_peter_question4_answer(request):
    """
    API endpoint to check Peter Rabbit Question 4 answer - Main Animal 1
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

        # AI-powered analysis for the Peter Rabbit main animal question
        return analyze_peter_main_animal_answer(user_answer)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Error in check_peter_question4_answer: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def analyze_peter_main_animal_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit main animal answer specifically
    """
    api_key = os.getenv('OPENROUTER_API_KEY2')
    if not api_key:
        return create_peter_main_animal_fallback_response(user_answer)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Main Animal Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified the main animal in "The Tale of Peter Rabbit".

IMPORTANT CONTEXT: "The Tale of Peter Rabbit" features Peter Rabbit as the main character. Peter is a rabbit (bunny). The story also features other animals like:
- Other rabbits (Flopsy, Mopsy, Cotton-tail - Peter's sisters)
- Mother Rabbit (Mrs. Rabbit)
- Mr. McGregor (human, not an animal)
- Sparrows (who help Peter)
- A cat and mouse (minor characters)

CORRECT ANSWERS for "Main Animal 1" include:
- "Rabbit"
- "Bunny" 
- "Peter Rabbit" (though just the animal type is preferred)
- "Rabbits"

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "incorrect",
    "show_answer": true/false,
    "correct_answer": "Rabbit"
}}

Guidelines:
- If they say "Rabbit" or "Bunny", mark as correct
- If they say "Peter" or "Peter Rabbit", it's partially correct but guide them to the animal type
- If they mention other animals from the story (sparrows, cat, mouse), explain these are minor characters
- If they say "Human" or "Mr. McGregor", explain he's not the main animal
- Always be encouraging and specific in your feedback
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
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                return JsonResponse(parsed_result)
            except json.JSONDecodeError:
                return create_peter_main_animal_fallback_response(user_answer)
        
        return create_peter_main_animal_fallback_response(user_answer)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_main_animal_answer: {e}")
        return create_peter_main_animal_fallback_response(user_answer)


def create_peter_main_animal_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit main animal question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        correct_answer = "Rabbit"
        
        # Check for correct main animal mentions
        rabbit_words = ['rabbit', 'bunny', 'bunnies']
        peter_words = ['peter']
        other_animals = ['sparrow', 'bird', 'cat', 'mouse', 'human', 'man', 'mcgregor']
        
        has_rabbit = any(word in user_lower for word in rabbit_words)
        has_peter = 'peter' in user_lower and not has_rabbit
        has_other_animal = any(word in user_lower for word in other_animals)
        
        if has_rabbit:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Perfect! Rabbit is indeed the main animal in this story. Peter is a rabbit who gets into trouble in Mr. McGregor\'s garden.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': correct_answer
            })
        elif has_peter:
            return JsonResponse({
                'isCorrect': True,
                'message': 'You\'re thinking of the right character! Peter is the main character, but what type of animal is he?',
                'feedback_type': 'good',
                'show_answer': False,
                'correct_answer': correct_answer
            })
        elif 'sparrow' in user_lower or 'bird' in user_lower:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Sparrows do appear in the story to help Peter, but they are not the main animal. Think about what type of animal Peter is.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_answer
            })
        elif 'cat' in user_lower:
            return JsonResponse({
                'isCorrect': False,
                'message': 'There is a cat in the story, but it\'s a minor character. The main character Peter is a different type of animal.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': correct_answer
            })
        elif 'mcgregor' in user_lower or 'human' in user_lower or 'man' in user_lower:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Mr. McGregor is a human character in the story, but we\'re looking for the main animal character. What type of animal is Peter?',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': correct_answer
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about the main character Peter. What type of animal is he? He has long ears and a fluffy tail.',
                'feedback_type': 'needs_improvement',
                'show_answer': True,
                'correct_answer': correct_answer
            })
    except Exception as e:
        logger.error(f"Peter main animal fallback error: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_peter_question5_answer(request):
    """
    API endpoint to check Peter Rabbit Question 5 answer - Personality
    """
    try:
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
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
        ai_result = analyze_peter_personality_answer(user_answer)
        
        if ai_result:
            return JsonResponse(ai_result)
        else:
            # Fallback to rule-based response if AI analysis fails
            fallback_result = create_peter_personality_fallback_response(user_answer)
            return JsonResponse(fallback_result)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Error in check_peter_question5_answer: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def analyze_peter_personality_answer(user_answer):
    """
    Analyze Peter Rabbit personality answer using AI
    Returns a dictionary (not JsonResponse) for the main function to wrap
    """
    try:
        api_key = os.getenv('OPENROUTER_API_KEY2')
        if not api_key:
            logger.warning("OpenRouter API key not found, using fallback")
            return None

        prompt = f"""
        Analyze this answer about Peter Rabbit's personality from "The Tale of Peter Rabbit":
        
        User Answer: "{user_answer}"
        
        Expected traits include: curious, adventurous, mischievous, disobedient, brave, determined, clever, naughty, playful, energetic, etc.
        
        Evaluate if the answer correctly identifies Peter Rabbit's personality traits. Consider:
        1. Does it mention relevant personality characteristics?
        2. Are the traits accurate to Peter Rabbit's character in the story?
        3. Is the answer specific and descriptive?
        
        Respond with JSON only:
        {{
            "isCorrect": true/false,
            "message": "Detailed feedback explaining why the answer is correct or incorrect",
            "correct_answer": "curious, adventurous, mischievous, disobedient",
            "show_answer": true/false,
            "feedback_type": "encouragement/guidance"
        }}
        """

        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'http://localhost:3000',
                'X-Title': 'Peter Rabbit Quiz'
            },
            json={
                'model': 'openai/gpt-4o-mini',
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.3,
                'max_tokens': 500
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                ai_result = json.loads(json_match.group())
                return ai_result
            else:
                logger.error("No JSON found in AI response")
                return None
        else:
            logger.error(f"OpenRouter API error: {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"Error in analyze_peter_personality_answer: {e}")
        return None

def create_peter_personality_fallback_response(user_answer):
    """
    Create fallback response for Peter Rabbit personality question
    Returns a dictionary (not JsonResponse) for the main function to wrap
    """
    try:
        user_answer_lower = user_answer.lower()
        
        # Keywords that indicate correct personality traits
        correct_keywords = [
            'curious', 'adventurous', 'mischievous', 'disobedient', 'brave', 
            'determined', 'clever', 'naughty', 'playful', 'energetic', 
            'bold', 'daring', 'rebellious', 'explorer', 'risk-taker'
        ]
        
        # Check if answer contains relevant personality traits
        found_traits = [word for word in correct_keywords if word in user_answer_lower]
        
        if found_traits:
            return {
                'isCorrect': True,
                'message': f"Excellent! You correctly identified Peter Rabbit's personality traits: {', '.join(found_traits)}. Peter is indeed {', '.join(found_traits)} in the story.",
                'correct_answer': 'curious, adventurous, mischievous, disobedient',
                'show_answer': False,
                'feedback_type': 'encouragement'
            }
        else:
            return {
                'isCorrect': False,
                'message': f"It looks like your answer '{user_answer}' doesn't mention the key personality traits of Peter Rabbit. Remember to focus on describing his character, such as being curious, adventurous, mischievous, or disobedient. Keep trying!",
                'correct_answer': 'curious, adventurous, mischievous, disobedient',
                'show_answer': True,
                'feedback_type': 'guidance'
            }
    except Exception as e:
        logger.error(f"Error in create_peter_personality_fallback_response: {e}")
        return {
            'isCorrect': False,
            'message': 'An error occurred while checking your answer. Please try again.',
            'correct_answer': 'curious, adventurous, mischievous, disobedient',
            'show_answer': True,
            'feedback_type': 'guidance'
        }


@csrf_exempt
@require_http_methods(["POST"])
def check_peter_question6_answer(request):
    """
    API endpoint to check Peter Rabbit Question 6 answer - Main Animal 2
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

        # AI-powered analysis for the Peter Rabbit main animal 2 question
        return analyze_peter_animal2_answer(user_answer)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Error in check_peter_question6_answer: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def analyze_peter_animal2_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit main animal 2 answer specifically
    """
    api_key = os.getenv('OPENROUTER_API_KEY2')
    if not api_key:
        return create_peter_animal2_fallback_response(user_answer)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Animal 2 Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified the second main animal in "The Tale of Peter Rabbit".

IMPORTANT CONTEXT: In "The Tale of Peter Rabbit", the second main animal character is Mr. McGregor, who is a human farmer, but the question is asking about animals. The main animals in the story are:
- Peter Rabbit (the main character)
- Flopsy, Mopsy, and Cotton-tail (Peter's sisters)
- Mrs. Rabbit (Peter's mother)

CORRECT ANSWERS for "Main Animal 2" include:
- "Rabbit" (referring to Peter's sisters or mother)
- "Rabbits" (plural form)
- "Sister rabbits"
- "Flopsy, Mopsy, and Cotton-tail"
- "Mrs. Rabbit"
- "Mother rabbit"

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "incorrect",
    "show_answer": true/false,
    "correct_answer": "Rabbit (Flopsy, Mopsy, and Cotton-tail)"
}}

Guidelines:
- If they mention "Rabbit" or "Rabbits", mark as correct
- If they mention the sister rabbits by name, mark as correct
- If they mention "Mrs. Rabbit" or "Mother rabbit", mark as correct
- If they say "Mr. McGregor" (human), gently correct them
- If they mention other animals not in the story, mark as incorrect
- Always be encouraging and educational about the story characters

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this animal answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 200
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                if 'is_correct' in parsed_result and 'isCorrect' not in parsed_result:
                    parsed_result['isCorrect'] = parsed_result['is_correct']
                return JsonResponse(parsed_result)
            except json.JSONDecodeError:
                return create_peter_animal2_fallback_response(user_answer)
        
        return create_peter_animal2_fallback_response(user_answer)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_animal2_answer: {e}")
        return create_peter_animal2_fallback_response(user_answer)


def create_peter_animal2_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit animal 2 question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        
        # Check for correct animal answers
        correct_answers = [
            'rabbit', 'rabbits', 'flopsy', 'mopsy', 'cotton-tail', 'cotton tail',
            'sister', 'sisters', 'mother', 'mom', 'mum'
        ]
        
        # Check for incorrect answers
        incorrect_answers = [
            'mcgregor', 'farmer', 'human', 'man', 'person', 'cat', 'dog', 'bird',
            'mouse', 'squirrel', 'fox', 'bear', 'wolf'
        ]
        
        has_correct = any(answer in user_lower for answer in correct_answers)
        has_incorrect = any(answer in user_lower for answer in incorrect_answers)
        
        if has_correct and not has_incorrect:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! You correctly identified another rabbit character from the story. The other main animals are Peter\'s sisters (Flopsy, Mopsy, and Cotton-tail) and his mother.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': 'Rabbit (Flopsy, Mopsy, and Cotton-tail)'
            })
        elif has_incorrect:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about the other characters in the story. Who are the other animals that live with Peter? They are also rabbits like Peter.',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': 'Rabbit (Flopsy, Mopsy, and Cotton-tail)'
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about Peter\'s family in the story. Who are the other animals that appear with him? They are the same type of animal as Peter.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': 'Rabbit (Flopsy, Mopsy, and Cotton-tail)'
            })
    except Exception as e:
        logger.error(f"Peter animal 2 fallback error: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False
        })

# Django Views for PetAct7 - Peter Rabbit Personality Question
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
@require_http_methods(["POST"])
def check_peter_question7_answer(request):
    """
    API endpoint to check Peter Rabbit Question 7 answer - Personality
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
                'show_answer': False,
                'misspelled_words': []
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization',
                'misspelled_words': []
            })

        # AI-powered analysis for the Peter Rabbit personality question
        return analyze_peter_personality_answer(user_answer)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Error in check_peter_question7_answer: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def analyze_peter_personality_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit personality answer specifically
    """
    api_key = os.getenv('OPENROUTER_API_KEY2')
    if not api_key:
        return create_peter_personality_fallback_response(user_answer)

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

IMPORTANT CONTEXT: Peter Rabbit is the main character in Beatrix Potter's "The Tale of Peter Rabbit". His key personality traits include:
- Curious/inquisitive 
- Mischievous/naughty
- Disobedient/rebellious
- Adventurous/brave
- Playful
- Sometimes reckless or impulsive

CORRECT ANSWERS for Peter Rabbit's personality include any of these traits:
- "Curious" / "Inquisitive" 
- "Mischievous" / "Naughty"
- "Disobedient" / "Rebellious"
- "Adventurous" / "Brave"
- "Playful" / "Fun-loving"
- "Reckless" / "Impulsive"
- Combinations like "curious and mischievous"

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "incorrect",
    "show_answer": true/false,
    "correct_answer": "Curious and mischievous",
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines:
- If they mention any correct personality trait, mark as correct
- If they mention multiple correct traits, mark as excellent
- If they give vague but related answers (like "bad" or "good"), mark as partial
- If they mention completely wrong traits or characters, mark as incorrect
- Always be encouraging and educational about Peter Rabbit's character
- If isCorrect is false, set show_answer to true
- If isCorrect is true, set show_answer to false

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
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            
            try:
                parsed_result = json.loads(result_raw)
                # Handle different possible key names from AI response
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                if 'is_correct' in parsed_result and 'isCorrect' not in parsed_result:
                    parsed_result['isCorrect'] = parsed_result['is_correct']
                
                # Ensure misspelled_words is always included
                if 'misspelled_words' not in parsed_result:
                    parsed_result['misspelled_words'] = []
                    
                return JsonResponse(parsed_result)
            except json.JSONDecodeError:
                return create_peter_personality_fallback_response(user_answer)
        
        return create_peter_personality_fallback_response(user_answer)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_personality_answer: {e}")
        return create_peter_personality_fallback_response(user_answer)


def create_peter_personality_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit personality question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        
        # Check for correct personality traits
        correct_traits = {
            'curious': ['curious', 'inquisitive', 'wondering'],
            'mischievous': ['mischievous', 'naughty', 'troublesome', 'cheeky'],
            'disobedient': ['disobedient', 'rebellious', 'defiant', 'stubborn'],
            'adventurous': ['adventurous', 'brave', 'bold', 'daring'],
            'playful': ['playful', 'fun', 'energetic', 'lively'],
            'reckless': ['reckless', 'impulsive', 'careless', 'risky']
        }
        
        # Check for incorrect traits
        wrong_traits = ['lazy', 'mean', 'scary', 'evil', 'sad', 'boring', 'quiet', 'shy', 'obedient', 'careful']
        
        # Count matching traits
        trait_matches = 0
        matched_categories = []
        
        for category, words in correct_traits.items():
            if any(word in user_lower for word in words):
                trait_matches += 1
                matched_categories.append(category)
        
        has_wrong_traits = any(trait in user_lower for trait in wrong_traits)
        
        if trait_matches >= 2 and not has_wrong_traits:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! You identified multiple aspects of Peter Rabbit\'s personality. He is indeed curious, mischievous, and adventurous.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': 'Curious and mischievous',
                'misspelled_words': []
            })
        elif trait_matches >= 1 and not has_wrong_traits:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Good! You identified an important part of Peter Rabbit\'s personality. He has several key traits that make him an interesting character.',
                'feedback_type': 'good',
                'show_answer': False,
                'correct_answer': 'Curious and mischievous',
                'misspelled_words': []
            })
        elif has_wrong_traits:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about how Peter Rabbit behaves in the story. Does he follow rules or break them? Is he cautious or does he take risks?',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': 'Curious and mischievous',
                'misspelled_words': []
            })
        elif any(word in user_lower for word in ['good', 'bad', 'nice', 'mean']):
            return JsonResponse({
                'isCorrect': False,
                'message': 'You\'re thinking about his character! Try to be more specific about Peter\'s personality traits. How does he act in the story?',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': 'Curious and mischievous',
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about how Peter Rabbit behaves in the story. What does he do that gets him into trouble? What drives his actions?',
                'feedback_type': 'needs_improvement',
                'show_answer': True,
                'correct_answer': 'Curious and mischievous',
                'misspelled_words': []
            })
            
    except Exception as e:
        logger.error(f"Peter personality fallback error: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_peter_question8_answer(request):
    """
    API endpoint to check Peter Rabbit Question 8 answer - Setting
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
                'show_answer': False,
                'misspelled_words': []
            })

        if not user_answer[0].isupper():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Remember to start your answer with a capital letter.',
                'feedback_type': 'correction',
                'show_answer': False,
                'highlight_issue': 'capitalization',
                'misspelled_words': []
            })

        # AI-powered analysis for the Peter Rabbit setting question
        return analyze_peter_setting_answer(user_answer)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Error in check_peter_question8_answer: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def analyze_peter_setting_answer(user_answer):
    """
    Use AI to analyze the Peter Rabbit setting answer specifically
    """
    api_key = os.getenv('OPENROUTER_API_KEY2')
    if not api_key:
        return create_peter_setting_fallback_response(user_answer)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Setting Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student correctly identified the setting of "The Tale of Peter Rabbit". Your task is twofold:
1. Evaluate the correctness of the student's answer about where the story takes place.
2. Identify any misspelled English words in their answer.

IMPORTANT CONTEXT: In "The Tale of Peter Rabbit", the main setting is Mr. McGregor's garden. Other correct setting descriptions include:
- Mr. McGregor's garden
- The garden
- McGregor's garden 
- The vegetable garden
- Mr. McGregor's farm
- The farm
- The countryside
- The field
- The farmyard

CORRECT ANSWERS for the setting include any mention of:
- Garden (with or without "Mr. McGregor's")
- Farm (with or without "Mr. McGregor's") 
- Countryside/farmyard/field
- Vegetable garden/patch

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your feedback message here",
    "feedback_type": "excellent", "good", "partial", or "incorrect",
    "show_answer": true/false,
    "correct_answer": "Mr. McGregor's garden",
    "misspelled_words": ["list", "of", "misspelled", "words"]
}}

Note on "misspelled_words":
- This must be a list of strings.
- Only include words that are clearly misspelled. Do not include proper nouns.
- If there are no spelling mistakes, return an empty list: [].

Guidelines:
- If they mention "garden" or "farm", mark as correct
- If they mention "Mr. McGregor" specifically, mark as excellent
- If they give vague answers like "outside" or "nature", mark as partial
- If they mention completely wrong locations, mark as incorrect
- Always be encouraging and educational about the Peter Rabbit story setting
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
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            
            try:
                parsed_result = json.loads(result_raw)
                # Handle different possible key names from AI response
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                if 'is_correct' in parsed_result and 'isCorrect' not in parsed_result:
                    parsed_result['isCorrect'] = parsed_result['is_correct']
                
                # Ensure misspelled_words is always included
                if 'misspelled_words' not in parsed_result:
                    parsed_result['misspelled_words'] = []
                    
                return JsonResponse(parsed_result)
            except json.JSONDecodeError:
                return create_peter_setting_fallback_response(user_answer)
        
        return JsonResponse({
            'error': f'AI service temporarily unavailable. Please try again.'
        }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_setting_answer: {e}")
        return JsonResponse({
            'error': 'Unable to check answer right now. Please try again.'
        }, status=500)


def create_peter_setting_fallback_response(user_answer):
    """
    Create a fallback response for Peter Rabbit setting question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        
        # Check for correct setting words
        correct_settings = {
            'garden': ['garden', 'gardens'],
            'farm': ['farm', 'farms', 'farmyard'],
            'mcgregor': ['mcgregor', 'mc gregor'],
            'countryside': ['countryside', 'country'],
            'field': ['field', 'fields'],
            'vegetable': ['vegetable', 'vegetables'],
            'patch': ['patch', 'plot']
        }
        
        # Check for incorrect/vague settings
        vague_settings = ['outside', 'nature', 'outdoors', 'place']
        wrong_settings = ['house', 'home', 'forest', 'woods', 'city', 'town', 'school', 'park']
        
        # Count matching setting categories
        setting_matches = 0
        matched_categories = []
        
        for category, words in correct_settings.items():
            if any(word in user_lower for word in words):
                setting_matches += 1
                matched_categories.append(category)
        
        has_vague = any(setting in user_lower for setting in vague_settings)
        has_wrong = any(setting in user_lower for setting in wrong_settings)
        
        if 'mcgregor' in matched_categories and ('garden' in matched_categories or 'farm' in matched_categories):
            return JsonResponse({
                'isCorrect': True,
                'message': 'Excellent! You correctly identified Mr. McGregor\'s garden as the main setting where Peter gets into trouble.',
                'feedback_type': 'excellent',
                'show_answer': False,
                'correct_answer': 'Mr. McGregor\'s garden',
                'misspelled_words': []
            })
        elif setting_matches >= 1 and not has_wrong:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Good! You identified the correct type of setting. The story takes place in Mr. McGregor\'s garden.',
                'feedback_type': 'good',
                'show_answer': False,
                'correct_answer': 'Mr. McGregor\'s garden',
                'misspelled_words': []
            })
        elif has_vague and not has_wrong:
            return JsonResponse({
                'isCorrect': False,
                'message': 'You\'re on the right track! Try to be more specific about where Peter goes that gets him into trouble.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': 'Mr. McGregor\'s garden',
                'misspelled_words': []
            })
        elif has_wrong:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about where Peter goes to look for food. It\'s not indoors, but a specific outdoor place belonging to someone.',
                'feedback_type': 'incorrect',
                'show_answer': True,
                'correct_answer': 'Mr. McGregor\'s garden',
                'misspelled_words': []
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think about where Peter goes that he shouldn\'t. Where does he find the vegetables that get him into trouble?',
                'feedback_type': 'needs_improvement',
                'show_answer': True,
                'correct_answer': 'Mr. McGregor\'s garden',
                'misspelled_words': []
            })
            
    except Exception as e:
        logger.error(f"Peter setting fallback error: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False,
            'misspelled_words': []
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_peter_question9_answer(request):
    """
    API endpoint to check Peter Rabbit Question 9 answer - Main Problem
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

        if not user_answer[0].isalpha():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please start your answer with a letter.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        # Try AI analysis first
        try:
            ai_response = analyze_peter_problem_answer(user_answer)
            if ai_response:
                return JsonResponse(ai_response)
        except Exception as e:
            logger.error(f"AI analysis failed for question 9: {e}")
            # Fall back to manual checking

        # Manual fallback logic
        return JsonResponse(create_peter_problem_fallback_response(user_answer))

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data.'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in check_peter_question9_answer: {e}")
        return JsonResponse({
            'error': 'An error occurred while processing your answer.'
        }, status=500)

def analyze_peter_problem_answer(user_answer):
    """
    Analyze Peter Rabbit main problem answer using AI
    """
    try:
        api_key = os.getenv('OPENROUTER_API_KEY2')
        if not api_key:
            logger.warning("OpenRouter API key not found, using fallback")
            return None

        prompt = f"""
        Analyze this answer about the main problem in "The Tale of Peter Rabbit":
        
        User Answer: "{user_answer}"
        
        Expected problems include: Peter disobeyed his mother, Peter went to Mr. McGregor's garden, Peter got caught by Mr. McGregor, Peter lost his clothes, Peter got into trouble, Peter was almost caught, Peter was chased by Mr. McGregor, etc.
        
        Evaluate if the answer correctly identifies the main problem in the story. Consider:
        1. Does it mention Peter's disobedience or going where he shouldn't?
        2. Does it describe the conflict with Mr. McGregor?
        3. Does it capture the central conflict of the story?
        
        Respond with JSON only:
        {{
            "isCorrect": true/false,
            "message": "Detailed feedback explaining why the answer is correct or incorrect",
            "correct_answer": "Peter disobeyed his mother and went to Mr. McGregor's garden",
            "show_answer": true/false,
            "feedback_type": "encouragement/guidance"
        }}
        """

        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'http://localhost:3000',
                'X-Title': 'Peter Rabbit Quiz'
            },
            json={
                'model': 'openai/gpt-4o-mini',
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.3,
                'max_tokens': 500
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                ai_result = json.loads(json_match.group())
                return ai_result
            else:
                logger.error("No JSON found in AI response")
                return None
        else:
            logger.error(f"OpenRouter API error: {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"Error in analyze_peter_problem_answer: {e}")
        return None

def create_peter_problem_fallback_response(user_answer):
    """
    Create fallback response for Peter Rabbit main problem question
    """
    try:
        user_answer_lower = user_answer.lower()
        
        # Keywords that indicate correct problem identification
        correct_keywords = [
            'disobey', 'disobeyed', 'mother', 'warning', 'garden', 'mcgregor', 
            'caught', 'chased', 'trouble', 'problem', 'lost', 'clothes', 
            'almost', 'nearly', 'danger', 'forbidden', 'shouldn\'t', 'shouldnt'
        ]
        
        # Check if answer contains relevant problem keywords
        found_keywords = [word for word in correct_keywords if word in user_answer_lower]
        
        if found_keywords:
            return {
                'isCorrect': True,
                'message': f"Excellent! You correctly identified the main problem: {', '.join(found_keywords)}. Peter's disobedience and the resulting trouble with Mr. McGregor is indeed the central conflict of the story.",
                'correct_answer': 'Peter disobeyed his mother and went to Mr. McGregor\'s garden',
                'show_answer': False,
                'feedback_type': 'encouragement'
            }
        else:
            return {
                'isCorrect': False,
                'message': f"It looks like your answer '{user_answer}' doesn't mention the key problem elements. Remember to focus on what Peter did wrong and what trouble he got into, such as disobeying his mother or getting caught by Mr. McGregor. Keep trying!",
                'correct_answer': 'Peter disobeyed his mother and went to Mr. McGregor\'s garden',
                'show_answer': True,
                'feedback_type': 'guidance'
            }
    except Exception as e:
        logger.error(f"Error in create_peter_problem_fallback_response: {e}")
        return {
            'isCorrect': False,
            'message': 'An error occurred while checking your answer. Please try again.',
            'correct_answer': 'Peter disobeyed his mother and went to Mr. McGregor\'s garden',
            'show_answer': True,
            'feedback_type': 'guidance'
        }

@csrf_exempt
@require_http_methods(["POST"])
def check_peter_question10_answer(request):
    """
    API endpoint to check Peter Rabbit Question 10 answer - Solution
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

        if not user_answer[0].isalpha():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please start your answer with a letter.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        # Try AI analysis first
        try:
            ai_response = analyze_peter_solution_answer(user_answer)
            if ai_response:
                return JsonResponse(ai_response)
        except Exception as e:
            logger.error(f"AI analysis failed for question 10: {e}")
            # Fall back to manual checking

        # Manual fallback logic
        return JsonResponse(create_peter_solution_fallback_response(user_answer))

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data.'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in check_peter_question10_answer: {e}")
        return JsonResponse({
            'error': 'An error occurred while processing your answer.'
        }, status=500)

def analyze_peter_solution_answer(user_answer):
    """
    Analyze Peter Rabbit solution answer using AI
    """
    try:
        api_key = os.getenv('OPENROUTER_API_KEY2')
        if not api_key:
            logger.warning("OpenRouter API key not found, using fallback")
            return None

        prompt = f"""
        Analyze this answer about how the problem was solved in "The Tale of Peter Rabbit":
        
        User Answer: "{user_answer}"
        
        Expected solutions include: Peter escaped from Mr. McGregor, Peter ran away, Peter got home safely, Peter's mother took care of him, Peter learned his lesson, Peter was rescued, Peter found his way back, Peter was saved, etc.
        
        Evaluate if the answer correctly identifies how the problem was resolved. Consider:
        1. Does it mention Peter escaping or getting away from Mr. McGregor?
        2. Does it describe Peter returning home safely?
        3. Does it capture the resolution of the conflict?
        
        Respond with JSON only:
        {{
            "isCorrect": true/false,
            "message": "Detailed feedback explaining why the answer is correct or incorrect",
            "correct_answer": "Peter escaped from Mr. McGregor and returned home safely",
            "show_answer": true/false,
            "feedback_type": "encouragement/guidance"
        }}
        """

        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'http://localhost:3000',
                'X-Title': 'Peter Rabbit Quiz'
            },
            json={
                'model': 'openai/gpt-4o-mini',
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.3,
                'max_tokens': 500
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                ai_result = json.loads(json_match.group())
                return ai_result
            else:
                logger.error("No JSON found in AI response")
                return None
        else:
            logger.error(f"OpenRouter API error: {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"Error in analyze_peter_solution_answer: {e}")
        return None

def create_peter_solution_fallback_response(user_answer):
    """
    Create fallback response for Peter Rabbit solution question
    """
    try:
        user_answer_lower = user_answer.lower()
        
        # Keywords that indicate correct solution identification
        correct_keywords = [
            'escape', 'escaped', 'ran', 'ran away', 'got away', 'fled', 'home', 
            'safely', 'saved', 'rescued', 'returned', 'back', 'mother', 'took care',
            'learned', 'lesson', 'got home', 'made it', 'survived', 'got out'
        ]
        
        # Check if answer contains relevant solution keywords
        found_keywords = [word for word in correct_keywords if word in user_answer_lower]
        
        if found_keywords:
            return {
                'isCorrect': True,
                'message': f"Excellent! You correctly identified the solution: {', '.join(found_keywords)}. Peter's escape and safe return home is indeed how the problem was resolved.",
                'correct_answer': 'Peter escaped from Mr. McGregor and returned home safely',
                'show_answer': False,
                'feedback_type': 'encouragement'
            }
        else:
            return {
                'isCorrect': False,
                'message': f"It looks like your answer '{user_answer}' doesn't mention the key solution elements. Remember to focus on how Peter got out of trouble, such as escaping from Mr. McGregor or returning home safely. Keep trying!",
                'correct_answer': 'Peter escaped from Mr. McGregor and returned home safely',
                'show_answer': True,
                'feedback_type': 'guidance'
            }
    except Exception as e:
        logger.error(f"Error in create_peter_solution_fallback_response: {e}")
        return {
            'isCorrect': False,
            'message': 'An error occurred while checking your answer. Please try again.',
            'correct_answer': 'Peter escaped from Mr. McGregor and returned home safely',
            'show_answer': True,
            'feedback_type': 'guidance'
        }

@csrf_exempt
@require_http_methods(["POST"])
def check_peter_question11_answer(request):
    """
    API endpoint to check Peter Rabbit Question 11 answer - Lesson Learned
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

        if not user_answer[0].isalpha():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please start your answer with a letter.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        # Try AI analysis first
        try:
            ai_response = analyze_peter_lesson_answer(user_answer)
            if ai_response:
                return JsonResponse(ai_response)
        except Exception as e:
            logger.error(f"AI analysis failed for question 11: {e}")
            # Fall back to manual checking

        # Manual fallback logic
        return JsonResponse(create_peter_lesson_fallback_response(user_answer))

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data.'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in check_peter_question11_answer: {e}")
        return JsonResponse({
            'error': 'An error occurred while processing your answer.'
        }, status=500)

def analyze_peter_lesson_answer(user_answer):
    """
    Analyze Peter Rabbit lesson learned answer using AI
    """
    try:
        api_key = os.getenv('OPENROUTER_API_KEY2')
        if not api_key:
            logger.warning("OpenRouter API key not found, using fallback")
            return None

        prompt = f"""
        Analyze this answer about the lesson learned in "The Tale of Peter Rabbit":
        
        User Answer: "{user_answer}"
        
        Expected lessons include: Peter learned to obey his mother, Peter learned not to disobey, Peter learned to listen to warnings, Peter learned the consequences of disobedience, Peter learned to be more careful, Peter learned to follow rules, Peter learned that actions have consequences, Peter learned to be obedient, etc.
        
        Evaluate if the answer correctly identifies the lesson learned. Consider:
        1. Does it mention learning to obey or listen to parents?
        2. Does it describe learning about consequences of disobedience?
        3. Does it capture the moral lesson of the story?
        
        Respond with JSON only:
        {{
            "isCorrect": true/false,
            "message": "Detailed feedback explaining why the answer is correct or incorrect",
            "correct_answer": "Peter learned to obey his mother and not to disobey warnings",
            "show_answer": true/false,
            "feedback_type": "encouragement/guidance"
        }}
        """

        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'http://localhost:3000',
                'X-Title': 'Peter Rabbit Quiz'
            },
            json={
                'model': 'openai/gpt-4o-mini',
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.3,
                'max_tokens': 500
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                ai_result = json.loads(json_match.group())
                return ai_result
            else:
                logger.error("No JSON found in AI response")
                return None
        else:
            logger.error(f"OpenRouter API error: {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"Error in analyze_peter_lesson_answer: {e}")
        return None

def create_peter_lesson_fallback_response(user_answer):
    """
    Create fallback response for Peter Rabbit lesson learned question
    """
    try:
        user_answer_lower = user_answer.lower()
        
        # Keywords that indicate correct lesson identification
        correct_keywords = [
            'obey', 'obeyed', 'listen', 'mother', 'warning', 'disobey', 'disobeyed',
            'lesson', 'learned', 'learn', 'consequence', 'careful', 'follow', 'rule',
            'obedient', 'obedience', 'shouldn\'t', 'shouldnt', 'must', 'need to'
        ]
        
        # Check if answer contains relevant lesson keywords
        found_keywords = [word for word in correct_keywords if word in user_answer_lower]
        
        if found_keywords:
            return {
                'isCorrect': True,
                'message': f"Excellent! You correctly identified the lesson: {', '.join(found_keywords)}. Peter's experience taught him the importance of obedience and listening to his mother's warnings.",
                'correct_answer': 'Peter learned to obey his mother and not to disobey warnings',
                'show_answer': False,
                'feedback_type': 'encouragement'
            }
        else:
            return {
                'isCorrect': False,
                'message': f"It looks like your answer '{user_answer}' doesn't mention the key lesson elements. Remember to focus on what Peter learned from his experience, such as obeying his mother, listening to warnings, or understanding the consequences of disobedience. Keep trying!",
                'correct_answer': 'Peter learned to obey his mother and not to disobey warnings',
                'show_answer': True,
                'feedback_type': 'guidance'
            }
    except Exception as e:
         logger.error(f"Error in create_peter_lesson_fallback_response: {e}")
         return {
             'isCorrect': False,
             'message': 'An error occurred while checking your answer. Please try again.',
             'correct_answer': 'Peter learned to obey his mother and not to disobey warnings',
             'show_answer': True,
             'feedback_type': 'guidance'
         }

@csrf_exempt
@require_http_methods(["POST"])
def check_peter_question12_answer(request):
    """
    API endpoint to check Peter Rabbit Question 12 answer - Moral of the Story
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

        if not user_answer[0].isalpha():
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please start your answer with a letter.',
                'feedback_type': 'guidance',
                'show_answer': False
            })

        # Try AI analysis first
        try:
            ai_response = analyze_peter_moral_answer(user_answer)
            if ai_response:
                return JsonResponse(ai_response)
        except Exception as e:
            logger.error(f"AI analysis failed for question 12: {e}")
            # Fall back to manual checking

        # Manual fallback logic
        return JsonResponse(create_peter_moral_fallback_response(user_answer))

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data.'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in check_peter_question12_answer: {e}")
        return JsonResponse({
            'error': 'An error occurred while processing your answer.'
        }, status=500)

def analyze_peter_moral_answer(user_answer):
    """
    Analyze Peter Rabbit moral of the story answer using AI
    """
    try:
        api_key = os.getenv('OPENROUTER_API_KEY2')
        if not api_key:
            logger.warning("OpenRouter API key not found, using fallback")
            return None

        prompt = f"""
        Analyze this answer about the moral of "The Tale of Peter Rabbit":
        
        User Answer: "{user_answer}"
        
        Expected morals include: listen to your parents, obey warnings, don't disobey, actions have consequences, be careful, follow rules, respect boundaries, don't go where you're not supposed to, etc.
        
        Evaluate if the answer correctly identifies the moral of the story. Consider:
        1. Does it mention listening to parents or obeying warnings?
        2. Does it describe the consequences of disobedience?
        3. Does it capture the moral lesson of the story?
        
        Respond with JSON only:
        {{
            "isCorrect": true/false,
            "message": "Detailed feedback explaining why the answer is correct or incorrect",
            "correct_answer": "Listen to your parents and obey warnings",
            "show_answer": true/false,
            "feedback_type": "encouragement/guidance"
        }}
        """

        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'http://localhost:3000',
                'X-Title': 'Peter Rabbit Quiz'
            },
            json={
                'model': 'openai/gpt-4o-mini',
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.3,
                'max_tokens': 500
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                ai_result = json.loads(json_match.group())
                return ai_result
            else:
                logger.error("No JSON found in AI response")
                return None
        else:
            logger.error(f"OpenRouter API error: {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"Error in analyze_peter_moral_answer: {e}")
        return None

def create_peter_moral_fallback_response(user_answer):
    """
    Create fallback response for Peter Rabbit moral of the story question
    """
    try:
        user_answer_lower = user_answer.lower()
        
        # Keywords that indicate correct moral identification
        correct_keywords = [
            'listen', 'obey', 'obeyed', 'parent', 'mother', 'father', 'warning', 
            'disobey', 'disobeyed', 'consequence', 'careful', 'follow', 'rule',
            'respect', 'boundary', 'supposed', 'shouldn\'t', 'shouldnt', 'must',
            'need to', 'important', 'lesson', 'learn', 'learned'
        ]
        
        # Check if answer contains relevant moral keywords
        found_keywords = [word for word in correct_keywords if word in user_answer_lower]
        
        if found_keywords:
            return {
                'isCorrect': True,
                'message': f"Excellent! You correctly identified the moral: {', '.join(found_keywords)}. The story teaches us the importance of listening to our parents and following their warnings.",
                'correct_answer': 'Listen to your parents and obey warnings',
                'show_answer': False,
                'feedback_type': 'encouragement'
            }
        else:
            return {
                'isCorrect': False,
                'message': f"It looks like your answer '{user_answer}' doesn't mention the key moral elements. Remember to focus on what the story teaches us, such as listening to parents, obeying warnings, or understanding consequences. Keep trying!",
                'correct_answer': 'Listen to your parents and obey warnings',
                'show_answer': True,
                'feedback_type': 'guidance'
            }
    except Exception as e:
        logger.error(f"Error in create_peter_moral_fallback_response: {e}")
        return {
            'isCorrect': False,
            'message': 'An error occurred while checking your answer. Please try again.',
            'correct_answer': 'Listen to your parents and obey warnings',
            'show_answer': True,
            'feedback_type': 'guidance'
        }
@csrf_exempt
@require_http_methods(["POST"])
def check_peter_question13_answer(request):
    """
    API endpoint to check Peter Rabbit Question 13 answer - Reading Feelings
    """
    try:
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please share how you felt while reading.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 3:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please share more about how you felt while reading the story.',
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

        # AI-powered analysis for the reading feelings question
        return analyze_peter_reading_feelings_answer(user_answer)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Error in check_peter_question13_answer: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def analyze_peter_reading_feelings_answer(user_answer):
    """
    Use AI to analyze the reading feelings answer specifically
    """
    api_key = os.getenv('OPENROUTER_API_KEY2')
    if not api_key:
        return create_peter_reading_feelings_fallback_response(user_answer)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Reading Feelings Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student thoughtfully shared their feelings about reading "The Tale of Peter Rabbit".

IMPORTANT CONTEXT: This is a personal reflection question about reading feelings. There are no "wrong" emotions - any genuine feeling about reading the story is valid. The goal is to encourage students to reflect on their reading experience.

VALID FEELINGS include any genuine emotions such as:
- Excited, happy, joyful (enjoying the adventure)
- Worried, nervous, scared (concerned for Peter)
- Curious, interested (wanting to know what happens)
- Sad, concerned (when Peter gets in trouble)
- Relieved (when Peter escapes)
- Entertained, amused (finding the story funny)
- Any other genuine emotional response

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your encouraging feedback message here",
    "feedback_type": "excellent", "good", "partial", or "needs_improvement",
    "show_answer": false
}}

Guidelines:
- If they express any genuine feeling or emotion, mark as correct
- If they give detailed feelings with explanations, mark as excellent
- If they mention basic feelings, mark as good
- If they give vague responses like "ok" or "fine", encourage more detail
- If they don't express feelings but talk about the story, guide them to emotions
- Always be encouraging and validate their emotional response
- For feelings questions, never show a "correct answer" since all genuine feelings are valid
- Always set show_answer to false
- Focus on whether they're sharing their personal emotional experience

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this reading feelings answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 250
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                return JsonResponse(parsed_result)
            except json.JSONDecodeError:
                return create_peter_reading_feelings_fallback_response(user_answer)
        
        return JsonResponse({
            'error': f'AI service temporarily unavailable. Please try again.'
        }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_reading_feelings_answer: {e}")
        return JsonResponse({
            'error': 'Unable to check answer right now. Please try again.'
        }, status=500)


def create_peter_reading_feelings_fallback_response(user_answer):
    """
    Create a fallback response for reading feelings question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        
        # Check for emotion words
        positive_feelings = ['happy', 'excited', 'joy', 'fun', 'good', 'great', 'love', 'like', 'enjoy', 'amazing', 'wonderful']
        negative_feelings = ['sad', 'scared', 'worried', 'nervous', 'anxious', 'concerned', 'upset', 'angry', 'afraid']
        neutral_feelings = ['ok', 'okay', 'fine', 'alright', 'normal']
        curious_feelings = ['curious', 'interested', 'wondering', 'excited', 'eager']
        
        has_positive = any(word in user_lower for word in positive_feelings)
        has_negative = any(word in user_lower for word in negative_feelings)
        has_neutral = any(word in user_lower for word in neutral_feelings)
        has_curious = any(word in user_lower for word in curious_feelings)
        
        # Check for explanations or reasons
        has_because = 'because' in user_lower
        has_when = 'when' in user_lower
        has_explanation = any(word in user_lower for word in ['felt', 'feel', 'made me', 'was', 'thought'])
        
        if (has_positive or has_negative or has_curious) and len(user_answer) >= 15:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Thank you for sharing your feelings about reading Peter Rabbit! It\'s wonderful when stories make us feel different emotions. Your personal response to the story is valuable.',
                'feedback_type': 'excellent',
                'show_answer': False
            })
        elif (has_positive or has_negative or has_curious) and len(user_answer) >= 8:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Thanks for sharing how you felt! Reading can bring up many different emotions, and yours are completely valid.',
                'feedback_type': 'good',
                'show_answer': False
            })
        elif has_neutral and len(user_answer) < 8:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Can you tell us more about your feelings? Did any part of Peter\'s adventure make you feel excited, worried, or curious? Share what emotions you experienced while reading.',
                'feedback_type': 'partial',
                'show_answer': False
            })
        elif len(user_answer) >= 10 and has_explanation:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Thank you for sharing your thoughts about the story! Your personal response shows you were engaged with Peter\'s adventure.',
                'feedback_type': 'good',
                'show_answer': False
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please share more about your feelings while reading. For example: Were you excited during Peter\'s adventure? Worried when he got in trouble? Curious about what would happen next?',
                'feedback_type': 'needs_improvement',
                'show_answer': False
            })
    except Exception as e:
        logger.error(f"Peter reading feelings fallback error: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': False
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_peter_question14_answer(request):
    """
    API endpoint to check Peter Rabbit Question 14 answer - Story Part Connection
    """
    try:
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
        
        if not user_answer:
            return JsonResponse({
                'error': 'Please tell us which part of the story made you feel that way.'
            }, status=400)

        # Basic validation checks
        if len(user_answer) < 5:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please describe which specific part of the story caused your feelings.',
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

        # AI-powered analysis for the story part connection question
        return analyze_peter_story_part_answer(user_answer)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Error in check_peter_question14_answer: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def analyze_peter_story_part_answer(user_answer):
    """
    Use AI to analyze the story part connection answer specifically
    """
    api_key = os.getenv('OPENROUTER_API_KEY2')
    if not api_key:
        return create_peter_story_part_fallback_response(user_answer)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "Peter Rabbit Story Part Checker"
    }

    prompt = f"""You are a helpful reading teacher checking if a student can connect their emotional response to specific parts of "The Tale of Peter Rabbit".

IMPORTANT CONTEXT: This question follows a feelings question, asking students to identify which specific part of the story made them feel a certain way. The goal is to help students make text-to-emotion connections.

KEY STORY EVENTS in Peter Rabbit that might evoke emotions:
- Peter disobeying his mother's warning (concern, worry)
- Peter entering Mr. McGregor's garden (excitement, anticipation)
- Peter eating vegetables in the garden (amusement, satisfaction)
- Peter meeting Mr. McGregor (fear, tension)
- Mr. McGregor chasing Peter (suspense, worry)
- Peter getting caught in the net (panic, fear)
- Peter escaping from danger (relief, excitement)
- Peter losing his jacket and shoes (sadness, consequence)
- Peter getting home safely (relief, happiness)
- Peter being sick and having medicine (sympathy, consequence)

IMPORTANT: Always respond with valid JSON in this exact format:
{{
    "isCorrect": true/false,
    "message": "Your encouraging feedback message here",
    "feedback_type": "excellent", "good", "partial", or "needs_improvement",
    "show_answer": true/false,
    "correct_answer": "Example responses when show_answer is true"
}}

Guidelines:
- If they mention any specific story event or scene, mark as correct and set show_answer to false
- If they connect their feeling to a particular moment, mark as excellent and set show_answer to false
- If they mention general parts but not specific moments, mark as good and set show_answer to false
- If they repeat their feeling without identifying a story part, mark as incorrect and set show_answer to true
- If they mention events not in the story, mark as incorrect and set show_answer to true
- If they give vague or insufficient responses, mark as incorrect and set show_answer to true
- When show_answer is true, provide example story parts that could evoke emotions
- Always validate their emotional response while focusing on text connection
- Focus on whether they can identify specific story moments

Student's answer: "{user_answer}\""""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f'Please analyze this story part connection answer: "{user_answer}"'}
        ],
        "temperature": 0.3,
        "max_tokens": 250
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            result_raw = response.json()['choices'][0]['message']['content'].strip()
            
            try:
                parsed_result = json.loads(result_raw)
                if 'result' in parsed_result and 'message' not in parsed_result:
                    parsed_result['message'] = parsed_result['result']
                return JsonResponse(parsed_result)
            except json.JSONDecodeError:
                return create_peter_story_part_fallback_response(user_answer)
        
        return JsonResponse({
            'error': f'AI service temporarily unavailable. Please try again.'
        }, status=500)

    except requests.RequestException as e:
        logger.error(f"Request exception in analyze_peter_story_part_answer: {e}")
        return JsonResponse({
            'error': 'Unable to check answer right now. Please try again.'
        }, status=500)


def create_peter_story_part_fallback_response(user_answer):
    """
    Create a fallback response for story part connection question if AI service fails
    """
    try:
        user_lower = user_answer.lower()
        
        # Check for specific story events
        story_events = {
            'garden': ['garden', 'mcgregor', 'vegetables', 'eating', 'lettuce', 'radish'],
            'chase': ['chase', 'chased', 'running', 'run', 'caught', 'escape'],
            'danger': ['danger', 'scared', 'frightened', 'caught', 'net', 'stuck'],
            'home': ['home', 'mother', 'sick', 'medicine', 'bed', 'safe'],
            'disobey': ['disobey', 'warning', 'told not to', 'mother said', 'naughty']
        }
        
        # General story references
        general_refs = ['story', 'part', 'when', 'scene', 'chapter', 'beginning', 'middle', 'end']
        
        # Check for specific events
        specific_events = []
        for event_type, keywords in story_events.items():
            if any(keyword in user_lower for keyword in keywords):
                specific_events.append(event_type)
        
        has_general_ref = any(word in user_lower for word in general_refs)
        has_specific_event = len(specific_events) > 0
        
        # Example answers to show when response is incorrect
        example_answers = "Examples: When Peter entered Mr. McGregor's garden, When Mr. McGregor chased Peter, When Peter got caught in the net, When Peter escaped and got home safely, When Peter was sick and needed medicine"
        
        if has_specific_event and len(user_answer) >= 15:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Perfect! You connected your feelings to a specific part of Peter\'s story. This shows you\'re really thinking about how different story events can make readers feel different emotions.',
                'feedback_type': 'excellent',
                'show_answer': False
            })
        elif has_specific_event:
            return JsonResponse({
                'isCorrect': True,
                'message': 'Good connection! You identified a specific part of the story that caused your feelings.',
                'feedback_type': 'good',
                'show_answer': False
            })
        elif has_general_ref and len(user_answer) >= 10:
            return JsonResponse({
                'isCorrect': False,
                'message': 'You mentioned a part of the story, but try to be more specific about exactly what happened that made you feel that way.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': example_answers
            })
        elif len(user_answer) >= 8:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Think of a specific moment or event in Peter\'s adventure that caused your feelings.',
                'feedback_type': 'partial',
                'show_answer': True,
                'correct_answer': example_answers
            })
        else:
            return JsonResponse({
                'isCorrect': False,
                'message': 'Please describe a specific part of Peter Rabbit\'s story that made you feel a certain way.',
                'feedback_type': 'needs_improvement',
                'show_answer': True,
                'correct_answer': example_answers
            })
    except Exception as e:
        logger.error(f"Peter story part fallback error: {e}")
        return JsonResponse({
            'isCorrect': False,
            'message': 'Please try again.',
            'feedback_type': 'error',
            'show_answer': True,
            'correct_answer': example_answers
        })