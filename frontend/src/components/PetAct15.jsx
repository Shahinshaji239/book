import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import { FaPlay, FaMicrophone, FaMicrophoneSlash, FaRocket } from "react-icons/fa";
import Header from "./Header";

export default function PetAct15() {
  const navigate = useNavigate();
  const [currentQuestion, setCurrentQuestion] = useState(15);
  const totalQuestions = 15;

  // --- STATE MANAGEMENT ---
  const [starRating, setStarRating] = useState(0);
  const [typedAnswer, setTypedAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showAnswer, setShowAnswer] = useState(false);

  const [interactionStage, setInteractionStage] = useState('voice');
  const [isQuestionFinished, setIsQuestionFinished] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentAudio, setCurrentAudio] = useState(null);
  const [currentUtterance, setCurrentUtterance] = useState(null);
  const [voiceEnabled, setVoiceEnabled] = useState(true);

  const ELEVENLABS_API_KEY = import.meta.env.VITE_ELEVENLABS_API_KEY;
  const VOICE_ID = 'pqHfZKP75CvOlQylNhV4';

  const {
    transcript,
    finalTranscript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition
  } = useSpeechRecognition();

  // --- NEW FUNCTION TO START SESSION ---
  const startSession = () => {
    resetTranscript();
    setInteractionStage('voice');
    setIsQuestionFinished(false);

    if (!browserSupportsSpeechRecognition) {
      alert("This browser doesn't support speech recognition.");
      return;
    }

    const questionAudio = new Audio('/rate.mp3');

    const timer = setTimeout(() => {
      questionAudio.play().catch(() => console.warn("Audio autoplay blocked."));
    }, 500);

    questionAudio.onended = () => {
      console.log("DEBUG: Question audio finished.");
      setIsQuestionFinished(true);
    };

    return () => {
      clearTimeout(timer);
      questionAudio.pause();
      SpeechRecognition.stopListening();
    };
  };

  // --- AUTO START ON PAGE LOAD ---
  useEffect(() => {
    const cleanup = startSession();
    return cleanup;
  }, []);

  // Effect 2: Starts listening after the question is finished
  useEffect(() => {
    if (isQuestionFinished && !listening && interactionStage === 'voice') {
      console.log("DEBUG: Conditions met. Starting to listen...");
      SpeechRecognition.startListening({ continuous: false, language: 'en-US' });
    }
  }, [isQuestionFinished, listening, interactionStage]);

  // Effect 3: Auto-submit voice answer
  useEffect(() => {
    if (finalTranscript && !isLoading) {
      const capitalizedAnswer = finalTranscript.charAt(0).toUpperCase() + finalTranscript.slice(1);
      submitAnswer(capitalizedAnswer, 'voice');
    }
  }, [finalTranscript, isLoading]);

  // --- AUDIO & HELPER FUNCTIONS ---
  const stopSpeaking = () => {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      setCurrentAudio(null);
    }
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setCurrentUtterance(null);
    setIsSpeaking(false);
  };

  const speakWithElevenLabs = async (text, onEndCallback = () => { }) => {
    try {
      const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}/stream`, {
        method: 'POST',
        headers: {
          'Accept': 'audio/mpeg',
          'Content-Type': 'application/json',
          'xi-api-key': ELEVENLABS_API_KEY
        },
        body: JSON.stringify({
          text: text,
          model_id: 'eleven_monolingual_v1',
          voice_settings: { stability: 0.6, similarity_boost: 0.7 }
        })
      });

      if (!response.ok) throw new Error(`ElevenLabs API error: ${response.status}`);

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      setCurrentAudio(audio);

      audio.onended = () => {
        setIsSpeaking(false);
        setCurrentAudio(null);
        URL.revokeObjectURL(audioUrl);
        onEndCallback();
      };

      await audio.play();
    } catch (error) {
      console.error('ElevenLabs TTS error:', error);
      onEndCallback();
    }
  };

  const speakWithBrowserSynthesis = (text, options = {}, onEndCallback = () => { }) => {
    const utterance = new SpeechSynthesisUtterance(text);
    setCurrentUtterance(utterance);

    utterance.onend = () => {
      setIsSpeaking(false);
      setCurrentUtterance(null);
      onEndCallback();
    };

    window.speechSynthesis.speak(utterance);
  };

  const speakText = (text, onEndCallback = () => { }) => {
    if (!voiceEnabled || !text) {
      onEndCallback();
      return;
    }
    stopSpeaking();
    setIsSpeaking(true);

    if (ELEVENLABS_API_KEY) {
      speakWithElevenLabs(text, onEndCallback);
    } else {
      speakWithBrowserSynthesis(text, {}, onEndCallback);
    }
  };

  // --- DYNAMIC SUBMIT ANSWER FUNCTION ---
  const submitAnswer = async (answer, submissionType) => {
    SpeechRecognition.stopListening();
    setIsLoading(true);
    if (submissionType === 'text') setFeedback(null);

    try {
      const response = await fetch('http://localhost:8000/api/check-peter-question15/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          answer: answer.trim(),
          rating: starRating 
        })
      });

      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(data.error || data.message || 'An unknown error occurred.');
      }

      if (submissionType === 'voice') {
        speakText(data.message, () => {
          setInteractionStage('text');
          const nextPromptAudio = new Audio('/input_audio.mp3');
          nextPromptAudio.play().catch(e => console.error("Prompt audio failed", e));
        });
      } else {
        setFeedback(data);
        setShowAnswer(data.show_answer);
        setTimeout(() => speakText(data.message), 300);
      }
    } catch (error) {
      console.error('Submission error:', error);
      const errorFeedback = { message: error.message, isCorrect: false };
      if (submissionType === 'text') setFeedback(errorFeedback);
      else speakText(error.message, () => setInteractionStage('text'));
    } finally {
      setIsLoading(false);
      resetTranscript();
    }
  };

  const handleTextSubmit = () => {
    if (typedAnswer.trim() && starRating > 0) {
      submitAnswer(typedAnswer, 'text');
    }
  };

  const handleStarClick = (rating) => {
    setStarRating(rating);
  };

  const renderHighlightedText = (text, misspelledWords) => {
    if (!misspelledWords || misspelledWords.length === 0) {
      return text;
    }
    const regex = new RegExp(`(${misspelledWords.join('|')})`, 'gi');
    const parts = text.split(regex);

    return parts.map((part, index) =>
      misspelledWords.some(word => word.toLowerCase() === part.toLowerCase())
        ? <span key={index} style={{ backgroundColor: '#FFD700', borderRadius: '3px' }}>{part}</span>
        : part
    );
  };

  const handleProceedToNext = () => {
    stopSpeaking();
    navigate('/');
  };

  const handleTryAgain = () => {
    stopSpeaking();
    setStarRating(0);
    setTypedAnswer('');
    setFeedback(null);
    setShowAnswer(false);
  };

  return (
    <div style={{
      backgroundColor: "#f5f5f5",
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
    }}>

      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=Comic+Neue&display=swap');
          @import url('https://fonts.googleapis.com/css2?family=Sen:wght@400;600;800&display=swap');
          
          .banner-section {
            position: relative;
            width: 100%;
            height: auto;
            margin-bottom: 0;
            flex-shrink: 0;
          }
          
          .banner-img {
            width: 100%;
            height: auto;
            object-fit: cover;
          }
          
          .banner-content {
            position: absolute;
            top: 50%;
            left: 80px;
            transform: translateY(-50%);
            color: white;
            z-index: 5;
          }
          
          .banner-title {
            font-family: 'Gulten';
            font-size: 48px;
            font-weight: 800;
            color: #2c5f7c;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
          }
          
          .question-indicator {
            position: absolute;
            top: 50%;
            right: 80px;
            transform: translateY(-50%);
            background: rgba(255, 255, 255, 0.9);
            padding: 8px 16px;
            border-radius: 20px;
            font-family: 'Sen', sans-serif;
            font-weight: 600;
            color: #2c5f7c;
            font-size: 14px;
          }

          .audio-play-button {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(35, 167, 172, 0.9);
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            z-index: 10;
            color: white;
            font-size: 18px;
            box-shadow: 0 4px 12px rgba(35, 167, 172, 0.3);
          }

          .audio-play-button:hover {
            background: rgba(30, 138, 143, 0.95);
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(35, 167, 172, 0.4);
          }

          .audio-play-button.playing {
            background: rgba(40, 167, 69, 0.9);
            animation: pulse 2s infinite;
          }

          @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
          }

          .voice-toggle-button {
            position: absolute;
            top: 20px;
            display: none;
            right: 80px;
            background: ${voiceEnabled ? '#28a745' : '#dc3545'};
            border: none;
            border-radius: 20px;
            padding: 8px 16px;
            color: white;
            font-size: 12px;
            cursor: pointer;
            font-family: 'Sen', sans-serif;
            font-weight: 600;
            z-index: 10;
            transition: all 0.3s ease;
          }

          .voice-toggle-button:hover {
            transform: scale(1.05);
          }
          
          .yellow-strip {
            width: 100%;
            height: 8px;
            background: #ffd700;
            margin-bottom: 10px;
            flex-shrink: 0;
          }
          
          .main-content {
            flex: 1;
            padding: 40px 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 120px;
            min-height: 0;
          }

          .content-with-button {
            flex: 1;
            max-width: 650px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-top: 20px;
          }
         
          .book-image-section {
            flex: 0 0 auto;
            margin-top: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
          }
         
          .book-cover {
            width: 280px;
            height: 350px;
            border-radius: 15px;
            transition: transform 0.3s ease;
            object-fit: cover;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
          }
         
          .question-section {
            background: white;
            border-radius: 20px;
            margin-top: 20px;
            padding: 40px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            border-bottom: 5px solid #ffd700;
          }
         
         .question-title {
           font-family: 'Sen', sans-serif;
           font-size: 32px;
           font-weight: 600;
           color: #333;
           margin-bottom: 30px;
         }
         
         .answer-field {
           margin-bottom: 30px;
         }
         
         .field-label {
           font-family: 'Sen', sans-serif;
           font-size: 24px;
           font-weight: 600;
           color: #333;
           margin-bottom: 15px;
           display: block;
         }

         .field-subtitle {
           font-family: 'Sen', sans-serif;
           font-size: 12px;
           font-weight: 600;
           color: #ff9500;
           background-color: #fff3d4;
           padding: 8px 12px;
           border-radius: 6px;
           margin-bottom: 20px;
           text-transform: uppercase;
           letter-spacing: 0.5px;
           display: inline-block;
         }

         .star-rating {
           display: flex;
           gap: 8px;
           margin-bottom: 25px;
           justify-content: center;
         }

         .star {
           background: none;
           border: none;
           font-size: 40px;
           cursor: pointer;
           transition: all 0.3s ease;
           padding: 4px;
           border-radius: 50%;
         }

         .star.outline {
           color: #ddd;
           filter: drop-shadow(0 0 2px rgba(0,0,0,0.1));
         }

         .star.filled {
           color: #ffd700;
           filter: drop-shadow(0 0 4px rgba(255, 215, 0, 0.5));
           text-shadow: 0 0 8px rgba(255, 215, 0, 0.3);
         }

         .star:hover {
           transform: scale(1.2);
         }

         .star.filled:hover {
           filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.8));
         }

         .rating-label {
           font-family: 'Sen', sans-serif;
           font-size: 18px;
           font-weight: 600;
           color: #333;
           margin-bottom: 15px;
           display: block;
         }

         .answer-textarea {
           width: 100%;
           padding: 18px 24px;
           font-size: 16px;
           border: 2px solid #e0e0e0;
           border-radius: 12px;
           font-family: 'Segoe UI', sans-serif;
           background-color: #f8f9fa;
           transition: all 0.3s ease;
           box-sizing: border-box;
           resize: vertical;
           min-height: 100px;
         }
         
         .answer-textarea:focus {
           outline: none;
           border-color: #5bc0de;
           background-color: white;
           box-shadow: 0 0 0 3px rgba(91, 192, 222, 0.1);
         }
         
         .answer-textarea::placeholder {
           color: #999;
           font-style: italic;
         }
         
         .answer-input {
           width: 100%;
           padding: 18px 24px;
           font-size: 16px;
           border: 2px solid #e0e0e0;
           border-radius: 12px;
           font-family: 'Segoe UI', sans-serif;
           background-color: #f8f9fa;
           transition: all 0.3s ease;
           box-sizing: border-box;
         }
         
         .answer-input:focus {
           outline: none;
           border-color: #5bc0de;
           background-color: white;
           box-shadow: 0 0 0 3px rgba(91, 192, 222, 0.1);
         }
         
         .answer-input::placeholder {
           color: #999;
           font-style: italic;
         }
         
         .button-section {
           display: flex;
           justify-content: flex-end;
           gap: 15px;
         }
         
         .btn-next {
           background: #5bc0de;
           color: white;
           border: none;
           padding: 14px 32px;
           border-radius: 10px;
           font-family: 'Sen', sans-serif;
           font-weight: 600;
           font-size: 14px;
           cursor: pointer;
           transition: all 0.3s ease;
           text-transform: uppercase;
           letter-spacing: 0.5px;
           box-shadow: 0 4px 12px rgba(91, 192, 222, 0.3);
         }
         
         .btn-next:disabled {
           background: #ccc;
           cursor: not-allowed;
           box-shadow: none;
         }
         
         .btn-next:hover:not(:disabled) {
           background: #46a8c7;
           transform: translateY(-2px);
           box-shadow: 0 6px 16px rgba(91, 192, 222, 0.4);
         }
         
         .btn-try-again {
           background: #dc3545;
           color: white;
           border: none;
           padding: 14px 32px;
           border-radius: 10px;
           font-family: 'Sen', sans-serif;
           font-weight: 600;
           font-size: 14px;
           cursor: pointer;
           transition: all 0.3s ease;
           text-transform: uppercase;
           letter-spacing: 0.5px;
           box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
         }
         
         .btn-try-again:hover {
           background: #c82333;
           transform: translateY(-2px);
           box-shadow: 0 6px 16px rgba(220, 53, 69, 0.4);
         }
         
         .btn-proceed {
           background: #28a745;
           color: white;
           border: none;
           padding: 14px 32px;
           border-radius: 10px;
           font-family: 'Sen', sans-serif;
           font-weight: 600;
           font-size: 14px;
           cursor: pointer;
           transition: all 0.3s ease;
           text-transform: uppercase;
           letter-spacing: 0.5px;
           box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
         }
         
         .btn-proceed:hover {
           background: #218838;
           transform: translateY(-2px);
           box-shadow: 0 6px 16px rgba(40, 167, 69, 0.4);
         }
         
         .feedback-section {
           background: white;
           border-radius: 20px;
           margin-top: 20px;
           padding: 30px;
           box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
           border-left: 5px solid;
           position: relative;
         }
         
         .feedback-section.correct {
           border-left-color: #28a745;
           background: linear-gradient(135deg, #f8fff9 0%, #ffffff 100%);
         }
         
         .feedback-section.incorrect {
           border-left-color: #dc3545;
           background: linear-gradient(135deg, #fff8f8 0%, #ffffff 100%);
         }

         .feedback-section.excellent {
           border-left-color: #28a745;
           background: linear-gradient(135deg, #f8fff9 0%, #ffffff 100%);
         }
         
         .feedback-section.good {
           border-left-color: #17a2b8;
           background: linear-gradient(135deg, #f0fcff 0%, #ffffff 100%);
         }
         
         .feedback-title {
           font-family: 'Sen', sans-serif;
           font-size: 24px;
           font-weight: 600;
           margin-bottom: 15px;
           display: flex;
           align-items: center;
           gap: 10px;
         }
         
         .feedback-title.correct {
           color: #28a745;
         }
         
         .feedback-title.incorrect {
           color: #dc3545;
         }

         .feedback-title.excellent {
           color: #28a745;
         }
         
         .feedback-title.good {
           color: #17a2b8;
         }

         .voice-replay-button {
           position: absolute;
           top: 15px;
           right: 15px;
           background: rgba(35, 167, 172, 0.1);
           border: 1px solid #23A7AC;
           border-radius: 20px;
           padding: 6px 12px;
           color: #23A7AC;
           font-size: 12px;
           cursor: pointer;
           font-family: 'Sen', sans-serif;
           font-weight: 600;
           transition: all 0.3s ease;
         }

         .voice-replay-button:hover {
           background: #23A7AC;
           color: white;
         }

         .voice-replay-button.speaking {
           background: #28a745;
           color: white;
           border-color: #28a745;
         }
         
         .feedback-message {
           font-family: 'Sen', sans-serif;
           font-size: 16px;
           color: #333;
           margin-bottom: 20px;
           line-height: 1.5;
         }
         
         .correct-answer {
           background: #e8f5e8;
           border: 1px solid #28a745;
           border-radius: 10px;
           padding: 15px;
           margin-top: 15px;
         }
         
         .correct-answer-title {
           font-family: 'Sen', sans-serif;
           font-size: 14px;
           font-weight: 600;
           color: #28a745;
           margin-bottom: 8px;
         }
         
         .correct-answer-text {
           font-family: 'Sen', sans-serif;
           font-size: 16px;
           color: #333;
           font-weight: 500;
         }
         
         .loading-spinner {
           display: inline-block;
           width: 16px;
           height: 16px;
           border: 2px solid #ffffff;
           border-radius: 50%;
           border-top-color: transparent;
           animation: spin 1s ease-in-out infinite;
           margin-right: 8px;
         }
         
         @keyframes spin {
           to { transform: rotate(360deg); }
         }
         
          .footer-section {
            width: 100%;
            height: 120px;
            position: relative;
            overflow: hidden;
            flex-shrink: 0;
          }
          
          .footer-img {
            width: 100%;
            height: 120px;
            object-fit: cover;
            display: block;
          }

          /* IMPROVED RESPONSIVE DESIGN - SAME AS GODACT1 */
          @media (max-width: 1024px) {
            .main-content {
              padding: 30px 40px;
              gap: 60px;
            }
            
            .book-cover {
              width: 240px;
              height: 300px;
            }
            
            .banner-title {
              font-size: 36px;
            }
          }
          
          @media (max-width: 768px) {
            .main-content {
              flex-direction: column;
              padding: 20px;
              gap: 30px;
              align-items: stretch;
            }
            
            .book-image-section {
              order: 1;
              margin-top: 0;
              padding: 0 20px;
            }
            
            .book-cover {
              width: 100%;
              max-width: 280px;
              height: auto;
              aspect-ratio: 4/5;
            }
            
            .content-with-button {
              order: 2;
              max-width: 100%;
              margin-top: 0;
            }
            
            .question-section {
              padding: 25px 20px;
              margin-top: 0;
            }

            .question-title {
              font-size: 24px;
              margin-bottom: 20px;
              text-align: center;
            }
            
            .field-label {
              font-size: 20px;
              margin-bottom: 12px;
              text-align: center;
            }

            .field-subtitle {
              font-size: 10px;
              padding: 6px 10px;
              text-align: center;
            }

            .star-rating {
              gap: 6px;
              margin-bottom: 20px;
            }

            .star {
              font-size: 32px;
            }

            .rating-label {
              font-size: 16px;
              margin-bottom: 12px;
              text-align: center;
            }

            .answer-textarea {
              padding: 15px 18px;
              font-size: 16px;
              min-height: 80px;
            }
            
            .answer-input {
              padding: 15px 18px;
              font-size: 16px;
            }
            
            .button-section {
              justify-content: center;
              flex-wrap: wrap;
              gap: 12px;
            }
            
            .btn-next, .btn-try-again, .btn-proceed {
              padding: 12px 24px;
              font-size: 13px;
              min-width: 120px;
            }
            
            .feedback-section {
              padding: 20px;
              margin-top: 15px;
            }
            
            .feedback-title {
              font-size: 20px;
            }
            
            .feedback-message {
              font-size: 15px;
            }
            
            .banner-title {
              font-size: 24px;
              left: 30px;
            }
            
            .banner-section {
              height: 120px;
            }
            
            .question-indicator {
              right: 30px;
              padding: 6px 12px;
              font-size: 12px;
            }

            .audio-play-button {
              top: 15px;
              right: 15px;
              width: 40px;
              height: 40px;
              font-size: 14px;
            }

            .voice-toggle-button {
              right: 60px;
              padding: 5px 10px;
              font-size: 10px;
              display: block;
            }
            
            .voice-replay-button {
              position: static;
              margin-bottom: 15px;
              width: fit-content;
              align-self: flex-end;
            }
          }

          @media (max-width: 480px) {
            .main-content {
              padding: 15px;
              gap: 20px;
            }
            
            .book-image-section {
              padding: 0 10px;
            }
            
            .question-section {
              padding: 20px 15px;
            }

            .question-title {
              font-size: 20px;
              margin-bottom: 15px;
            }
            
            .field-label {
              font-size: 18px;
            }

            .field-subtitle {
              font-size: 9px;
              padding: 5px 8px;
            }

            .star-rating {
              gap: 4px;
              margin-bottom: 15px;
            }

            .star {
              font-size: 28px;
            }

            .rating-label {
              font-size: 14px;
              margin-bottom: 10px;
            }

            .answer-textarea {
              padding: 12px 15px;
              font-size: 15px;
              min-height: 70px;
            }
            
            .answer-input {
              padding: 12px 15px;
              font-size: 15px;
            }
            
            .btn-next, .btn-try-again, .btn-proceed {
              padding: 10px 20px;
              font-size: 12px;
              min-width: 100px;
            }
            
            .feedback-section {
              padding: 15px;
            }
            
            .feedback-title {
              font-size: 18px;
            }
            
            .feedback-message {
              font-size: 14px;
            }
            
            .banner-title {
              font-size: 18px;
              left: 20px;
            }
            
            .question-indicator {
              right: 20px;
              padding: 4px 8px;
              font-size: 11px;
            }

            .audio-play-button {
              width: 35px;
              height: 35px;
              font-size: 12px;
            }

            .voice-toggle-button {
              right: 50px;
              padding: 4px 8px;
              font-size: 9px;
            }
          }

          /* iPhone-specific adjustments */
          @media (max-width: 414px) and (max-height: 896px) {
            .banner-section {
              height: 100px;
            }
            
            .main-content {
              padding: 10px;
            }
            
            .book-cover {
              max-width: 250px;
            }
            
            .question-section {
              border-radius: 15px;
            }

            .answer-textarea {
              border-radius: 10px;
            }

            .question-title {
              font-size: 18px;
            }

            .field-label {
              font-size: 15px;
            }

            .star {
              font-size: 24px;
            }
          }
       `}
      </style>
      <Header />

      <div className="banner-section">
        <img src="/banner.png" alt="Banner Background" className="banner-img" />
        
        <div className="banner-content">
          <h1 className="banner-title">My Star Rating</h1>
        </div>
        
        <div className="question-indicator">
          QUESTION {currentQuestion}/{totalQuestions}
        </div>

        {/* --- NEW START SESSION BUTTON --- */}
        <button
          className="audio-play-button"
          onClick={startSession}
          title="Start Session"
        >
          <FaRocket />
        </button>
      </div>

      <div className="main-content">
        <div className="book-image-section">
          <img src="/peterrabbit.svg" alt="Peter Rabbit Book Cover" className="book-cover" />
        </div>

        <div className="content-with-button">

          {/* --- CONDITIONAL UI (from GodAct2) --- */}
          {interactionStage === 'voice' ? (
            // UI for voice input stage
            <div className="voice-input-section" style={{ textAlign: 'center', padding: '40px', background: 'white', borderRadius: '20px', boxShadow: '0 8px 25px rgba(0,0,0,0.1)' }}>
              {listening ? (
                <>
                  <FaMicrophone size={50} color="#5bc0de" style={{ marginBottom: '20px' }} />
                  <p>Listening...</p>
                </>
              ) : (
                <>
                  <FaMicrophoneSlash size={50} color="#6c757d" style={{ marginBottom: '20px' }} />
                  <p>{isLoading ? 'Checking answer...' : 'Say your answer'}</p>
                </>
              )}
            </div>
          ) : (
            // UI for text input stage (your original PetAct15 UI)
            <>
              <div className="question-section">
                <h2 className="question-title">Rate this book and explain why</h2>
                <div className="answer-field">
                  <div className="field-subtitle">RATE THE BOOK</div>
                  
                  <div className="star-rating">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        className={`star ${starRating >= star ? 'filled' : 'outline'}`}
                        onClick={() => handleStarClick(star)}
                      >
                        ★
                      </button>
                    ))}
                  </div>

                  <label className="rating-label">Why I gave this rating</label>
                  {!feedback ? (
                    // If there's no feedback yet, show the normal editable textarea
                    <textarea
                      className="answer-textarea"
                      placeholder="type answer here"
                      value={typedAnswer}
                      onChange={(e) => setTypedAnswer(e.target.value)}
                      disabled={isLoading}
                      rows="4"
                    />
                  ) : (
                    // After feedback, show the non-editable highlighted version of the answer
                    <div className="answer-textarea" style={{ backgroundColor: '#e9ecef', cursor: 'default', minHeight: '100px', padding: '18px 24px' }}>
                      {renderHighlightedText(typedAnswer, feedback.misspelled_words)}
                    </div>
                  )}
                </div>
              </div>

              {feedback && (
                <div className={`feedback-section ${feedback.isCorrect ? 'correct' : feedback.feedback_type || 'excellent'}`}>
                  {/* Voice Replay Button */}
                  <button
                    className={`voice-replay-button ${isSpeaking ? 'speaking' : ''}`}
                    onClick={() => {
                      if (isSpeaking) {
                        stopSpeaking();
                      } else {
                        let voiceText = feedback.message;
                        if (feedback.correct_answer && showAnswer) {
                          voiceText += ` The correct answer is: ${feedback.correct_answer}`;
                        }
                        speakText(voiceText);
                      }
                    }}
                    title={isSpeaking ? "Stop speaking" : "Replay feedback"}
                  >
                    {isSpeaking ? '⏹️ Stop' : '🔊 Replay'}
                  </button>

                  <div className={`feedback-title ${feedback.isCorrect ? 'correct' : feedback.feedback_type || 'excellent'}`}>
                    Thank you for your feedback!
                  </div>
                  <div className="feedback-message">
                    {feedback.message}
                  </div>
                  {showAnswer && feedback.correct_answer && (
                    <div className="correct-answer">
                      <div className="correct-answer-title">Complete Answer:</div>
                      <div className="correct-answer-text">{feedback.correct_answer}</div>
                    </div>
                  )}
                </div>
              )}

              <div className="button-section">
                {!feedback ? (
                  <button
                    className="btn-next"
                    onClick={handleTextSubmit}
                    disabled={!typedAnswer.trim() || starRating === 0 || isLoading}
                  >
                    {isLoading ? 'CHECKING...' : 'CHECK ANSWER'}
                  </button>
                ) : (
                  <div style={{ display: 'flex', gap: '15px' }}>
                    {!feedback.isCorrect && (
                      <button className="btn-try-again" onClick={handleTryAgain}>
                        TRY AGAIN
                      </button>
                    )}
                    <button className="btn-proceed" onClick={handleProceedToNext}>
                      FINISH
                    </button>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      <div className="footer-section">
        <img src="/footer.png" alt="Footer" className="footer-img" />
      </div>
    </div>
  );
}