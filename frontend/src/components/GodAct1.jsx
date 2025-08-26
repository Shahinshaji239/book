import React, { useState, useEffect, useRef } from "react";
import { Room, RoomEvent, Track } from 'livekit-client';
import Header from "./Header";

export default function VoiceIntegratedGodAct1() {
  // Question and answer states
  const [currentQuestion, setCurrentQuestion] = useState(1);
  const [titleAnswer, setTitleAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showAnswer, setShowAnswer] = useState(false);

  // Voice bot states
  const [voiceMode, setVoiceMode] = useState('connecting'); // 'connecting', 'listening', 'processing', 'vocal_feedback', 'prompting', 'writing', 'complete'
  const [voiceFeedback, setVoiceFeedback] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [hasVoiceResponse, setHasVoiceResponse] = useState(false);
  const [room, setRoom] = useState(null);
  const [agentResponse, setAgentResponse] = useState('');
  const [connectionError, setConnectionError] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [voiceTranscript, setVoiceTranscript] = useState('');
  const [botQuestion, setBotQuestion] = useState('');

  const totalQuestions = 9;
  const roomRef = useRef(null);
  const audioElementRef = useRef(null);

  // Questions for Goldilocks and the Three Bears
  const questions = [
    "What is the title of this story?",
    "Who is the author of this story?",
    "What genre is this story - Fiction or Non-Fiction?",
    "Who are the main characters in this story?",
    "Where does the story take place?",
    "What are three important events that happen in the story?",
    "What is the problem or conflict in the story?",
    "Who is your favorite character and why?",
    "What lesson or moral does this story teach us?"
  ];

  // Connect to LiveKit Room
  const connectToVoiceBot = async () => {
    try {
      setVoiceMode('connecting');
      setConnectionError(null);

      // Get token from backend
      const tokenResponse = await fetch('http://localhost:8000/voice_assistant/token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          identity: `student_${Date.now()}`,
          room: 'goldilocks_question1'
        })
      });

      if (!tokenResponse.ok) {
        throw new Error(`Token request failed: ${tokenResponse.status}`);
      }

      const tokenData = await tokenResponse.json();
      
      if (tokenData.error) {
        throw new Error(tokenData.error);
      }

      console.log('Token received successfully');
      console.log('Token data:', { url: tokenData.url, hasToken: !!tokenData.token });

      // Validate token data
      if (!tokenData.url || !tokenData.token) {
        throw new Error('Invalid token data received from server');
      }

      // Create and connect to LiveKit room
      const newRoom = new Room({
        adaptiveStream: true,
        dynacast: true,
        videoCaptureDefaults: {
          resolution: { width: 1280, height: 720 }
        }
      });
      roomRef.current = newRoom;
      setRoom(newRoom);

      // Set up room event handlers
      newRoom.on(RoomEvent.Connected, () => {
        console.log('Connected to LiveKit room');
        setIsConnected(true);
        setVoiceMode('listening');
        // Bot will automatically start asking questions
      });

      newRoom.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
        console.log('Track subscribed:', track.kind);
        if (track.kind === Track.Kind.Audio && participant.isAgent) {
          const audioElement = track.attach();
          audioElementRef.current = audioElement;
          audioElement.muted = false;
          document.body.appendChild(audioElement);
          
          // Handle autoplay policy
          const playAudio = () => {
            audioElement.play().catch(e => {
              console.log('Audio autoplay blocked, waiting for user interaction');
            });
          };
          
          playAudio();
          
          // Add click listener to enable audio on first user interaction
          const enableAudio = () => {
            playAudio();
            document.removeEventListener('click', enableAudio);
          };
          document.addEventListener('click', enableAudio);
        }
      });

      newRoom.on(RoomEvent.TrackUnsubscribed, (track, publication, participant) => {
        if (track.kind === Track.Kind.Audio) {
          track.detach();
        }
      });

      newRoom.on(RoomEvent.DataReceived, (payload, participant) => {
        if (participant?.isAgent) {
          const message = new TextDecoder().decode(payload);
          console.log('Agent message:', message);
          
          try {
            const data = JSON.parse(message);
            
            if (data.type === 'transcript') {
              // User spoke, now processing
              setVoiceTranscript(data.content);
              setVoiceMode('processing');
              
            } else if (data.type === 'vocal_analysis') {
              // Bot provides vocal feedback about the spoken response
              setVoiceFeedback({
                transcript: data.transcript,
                feedback: data.feedback,
                confidence: data.confidence
              });
              setHasVoiceResponse(true);
              setVoiceMode('vocal_feedback');
              
            } else if (data.type === 'prompt_writing') {
              // Bot prompts to write the answer
              setVoiceMode('prompting');
              // Auto-populate text field with voice transcript
              if (voiceTranscript || data.transcript) {
                setTitleAnswer(voiceTranscript || data.transcript);
              }
              
            } else if (data.type === 'question_asked') {
              // Bot asked a question
              setBotQuestion(data.question);
              setVoiceMode('listening');
              
            } else if (data.type === 'analysis') {
              // Fallback for simpler implementation
              setVoiceFeedback({
                transcript: data.transcript,
                feedback: data.feedback,
                confidence: data.confidence
              });
              setHasVoiceResponse(true);
              setVoiceTranscript(data.transcript);
              
              // Go through proper workflow: vocal_feedback -> prompting
              setVoiceMode('vocal_feedback');
              
              // Simulate bot providing vocal feedback first
              setTimeout(() => {
                setVoiceMode('prompting');
                setTitleAnswer(data.transcript);
              }, 3000);
            }
          } catch (e) {
            console.log('Non-JSON message from agent:', message);
            setAgentResponse(message);
          }
        }
      });

      newRoom.on(RoomEvent.Disconnected, () => {
        console.log('Disconnected from LiveKit room');
        setIsConnected(false);
        setVoiceMode('listening');
        cleanup();
      });

      // Connect to the room
      await newRoom.connect(tokenData.url, tokenData.token);

    } catch (error) {
      console.error('Error connecting to voice bot:', error);
      setConnectionError(error.message);
      setVoiceMode('listening');
    }
  };

  // Cleanup function
  const cleanup = () => {
    if (audioElementRef.current) {
      document.body.removeChild(audioElementRef.current);
      audioElementRef.current = null;
    }
  };

  // Initialize connection
  useEffect(() => {
    connectToVoiceBot();

    // Cleanup on unmount
    return () => {
      if (roomRef.current) {
        roomRef.current.disconnect();
      }
      cleanup();
    };
  }, []);

  // Start voice recording
  const startVoiceRecording = async () => {
    if (!room || !isConnected) {
      console.error('Room not connected');
      return;
    }

    try {
      setIsRecording(true);
      setVoiceMode('listening');
      
      // Request microphone permission and enable it
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log('Microphone permission granted');
      
      await room.localParticipant.enableCameraAndMicrophone(false, true);
      console.log('Voice recording started');
      
      // Send a message to the agent to start listening
      await sendMessageToAgent('start_listening');
    } catch (error) {
      console.error('Error starting voice recording:', error);
      alert('Please allow microphone access to use voice features');
      setIsRecording(false);
      setVoiceMode('listening');
    }
  };

  // Stop voice recording
  const stopVoiceRecording = async () => {
    if (!room || !isConnected) {
      console.error('Room not connected');
      return;
    }

    try {
      setIsRecording(false);
      setVoiceMode('processing');
      await room.localParticipant.setMicrophoneEnabled(false);
      console.log('Voice recording stopped');
      
      // Send a message to the agent to stop listening and process
      await sendMessageToAgent('stop_listening');
    } catch (error) {
      console.error('Error stopping voice recording:', error);
    }
  };

  // Submit written answer
  const submitAnswer = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/check-question1/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          answer: titleAnswer.trim()
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.error) {
        setFeedback({ message: data.error, isCorrect: false });
      } else {
        setFeedback(data);
        setShowAnswer(data.show_answer);
        setVoiceMode('complete');
        
        // Provide final voice feedback
        const feedbackText = data.isCorrect ? 
          `Excellent! ${data.message}` : 
          `${data.message} Let me help you with the correct answer.`;
        speakText(feedbackText);
      }
    } catch (error) {
      console.error('Network error:', error);
      setFeedback({ message: 'Network error. Please check your connection and try again.', isCorrect: false });
    } finally {
      setIsLoading(false);
    }
  };

  const handleNextQuestion = async () => {
    if (titleAnswer.trim()) {
      await submitAnswer();
    } else {
      alert('Please enter an answer before proceeding.');
    }
  };

  const handleProceedToNext = () => {
    setCurrentQuestion(currentQuestion + 1);
    setFeedback(null);
    setShowAnswer(false);
    setTitleAnswer('');
    setVoiceFeedback(null);
    setHasVoiceResponse(false);
    setVoiceMode('listening');
    setBotQuestion('');
  };

  const handleTryAgain = () => {
    setTitleAnswer('');
    setFeedback(null);
    setShowAnswer(false);
    setVoiceMode('writing');
  };

  const resetVoiceSession = async () => {
    setVoiceFeedback(null);
    setHasVoiceResponse(false);
    setTitleAnswer('');
    setVoiceMode('listening');
    
    // Re-enable microphone for new attempt
    if (room && isConnected) {
      await room.localParticipant.setMicrophoneEnabled(true);
    }
  };

  const sendMessageToAgent = async (message) => {
    if (!room || !isConnected) {
      console.error('Room not connected');
      return;
    }

    try {
      const encoder = new TextEncoder();
      const data = encoder.encode(JSON.stringify({
        type: 'question',
        question: 'title',
        message: message
      }));
      
      await room.localParticipant.publishData(data, true);
    } catch (error) {
      console.error('Error sending message to agent:', error);
    }
  };

  // Text-to-speech function
  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 0.8;
      speechSynthesis.speak(utterance);
    }
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
          
          .voice-section {
            background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%);
            border-radius: 20px;
            margin-top: 20px;
            padding: 30px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #2196F3;
            text-align: center;
          }

          .voice-status {
            font-family: 'Sen', sans-serif;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #1976D2;
          }

          .voice-controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
          }

          .mic-button {
            background: #2196F3;
            color: white;
            border: none;
            border-radius: 50%;
            width: 80px;
            height: 80px;
            font-size: 24px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
          }

          .mic-button:hover:not(:disabled) {
            background: #1976D2;
            transform: scale(1.05);
            box-shadow: 0 6px 16px rgba(33, 150, 243, 0.4);
          }

          .mic-button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
          }

          .mic-button.recording {
            background: #f44336;
            animation: pulse 2s infinite;
          }

          .mic-button.processing {
            background: #ff9800;
          }

          @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
          }

          .voice-feedback-section {
            background: #e8f5e9;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #4caf50;
          }

          .voice-transcript {
            background: #f3e5f5;
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
            font-style: italic;
            color: #6a1b9a;
            border-left: 3px solid #9c27b0;
          }

          .mode-indicator {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 20px;
          }

          .mode-connecting { background: #fff3e0; color: #f57c00; }
          .mode-listening { background: #e3f2fd; color: #1976d2; }
          .mode-processing { background: #fff3e0; color: #f57c00; }
          .mode-vocal_feedback { background: #f3e5f5; color: #7b1fa2; }
          .mode-prompting { background: #e8f5e9; color: #388e3c; }
          .mode-writing { background: #fce4ec; color: #c2185b; }
          .mode-complete { background: #e0f2f1; color: #00695c; }

          .audio-visualizer {
            width: 200px;
            height: 50px;
            margin: 20px auto;
            display: flex;
            align-items: end;
            gap: 3px;
            justify-content: center;
          }

          .audio-bar {
            width: 4px;
            background: #2196F3;
            border-radius: 2px;
            animation: audioWave 1.5s ease-in-out infinite;
          }

          .audio-bar:nth-child(1) { animation-delay: 0s; }
          .audio-bar:nth-child(2) { animation-delay: 0.1s; }
          .audio-bar:nth-child(3) { animation-delay: 0.2s; }
          .audio-bar:nth-child(4) { animation-delay: 0.3s; }
          .audio-bar:nth-child(5) { animation-delay: 0.4s; }

          @keyframes audioWave {
            0%, 100% { height: 10px; }
            50% { height: 30px; }
          }

          .workflow-progress {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin: 20px 0;
            padding: 15px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 10px;
          }

          .progress-step {
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
          }

          .progress-step.active {
            background: #2196F3;
            color: white;
          }

          .progress-step.completed {
            background: #4caf50;
            color: white;
          }

          .progress-step.pending {
            background: #e0e0e0;
            color: #999;
          }

          .bot-question {
            background: #fff3e0;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #ff9800;
            font-family: 'Sen', sans-serif;
            font-size: 18px;
            color: #e65100;
            font-weight: 600;
          }

          /* Existing styles from original component */
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
            max-width: 500px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-top: 20px;
          }
         
          .book-image-section {
            flex: 0 0 auto;
            margin-top: 20px;
          }
         
          .book-cover {
            width: 280px;
            height: 350px;
            border-radius: 15px;
            transition: transform 0.3s ease;
            object-fit: cover;
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
          
          .answer-input.voice-filled {
            background-color: #e3f2fd;
            border-color: #2196F3;
          }
          
          .button-section {
            display: flex;
            justify-content: flex-end;
            gap: 15px;
          }
          
          .btn-next {
            background: #23A7AC;
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
            background: #1e8a8f;
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

          .btn-reset-voice {
            background: #ff9800;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-family: 'Sen', sans-serif;
            font-weight: 600;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
          }

          .btn-reset-voice:hover {
            background: #f57c00;
          }
          
          .feedback-section {
            background: white;
            border-radius: 20px;
            margin-top: 20px;
            padding: 30px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            border-left: 5px solid;
          }
          
          .feedback-section.correct {
            border-left-color: #28a745;
            background: linear-gradient(135deg, #f8fff9 0%, #ffffff 100%);
          }
          
          .feedback-section.incorrect {
            border-left-color: #dc3545;
            background: linear-gradient(135deg, #fff8f8 0%, #ffffff 100%);
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
          
          .feedback-message {
            font-family: 'Sen', sans-serif;
            font-size: 16px;
            color: #333;
            margin-bottom: 20px;
            line-height: 1.5;
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
        `}
      </style>

      <Header />
      
      {/* Banner Section */}
      <div className="banner-section">
        <img 
          src="/banner.png" 
          alt="Banner Background" 
          className="banner-img"
        />
        <div className="banner-content">
          <h1 className="banner-title">Book Facts</h1>
        </div>
        <div className="question-indicator">
          QUESTION {currentQuestion}/{totalQuestions}
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Book Image Section */}
        <div className="book-image-section">
          <img 
            src="/goldilocks.png" 
            alt="Goldilocks and the Three Bears Book Cover"
            className="book-cover"
          />
        </div>

        {/* Content with Button Section */}
        <div className="content-with-button">
          
          {/* Voice Interaction Section */}
          <div className="voice-section">
            <div className={`mode-indicator mode-${voiceMode}`}>
              {voiceMode === 'connecting' && '🔗 Connecting to Voice Bot...'}
              {voiceMode === 'listening' && '🎤 Voice Bot: Ready to Listen'}
              {voiceMode === 'processing' && '🤖 Processing your response...'}
              {voiceMode === 'vocal_feedback' && '💬 Voice Bot: Giving Feedback'}
              {voiceMode === 'prompting' && '✍️ Voice Bot: Write your answer below'}
              {voiceMode === 'writing' && '📝 Text Mode: Complete your answer'}
              {voiceMode === 'complete' && '✅ Question Complete!'}
            </div>

            {/* Progress Workflow */}
            <div className="workflow-progress">
              <div className={`progress-step ${
                ['listening', 'processing', 'vocal_feedback', 'prompting', 'writing', 'complete'].includes(voiceMode) ? 'completed' : 
                voiceMode === 'listening' ? 'active' : 'pending'
              }`}>
                1. Voice Answer
              </div>
              <div className={`progress-step ${
                ['vocal_feedback', 'prompting', 'writing', 'complete'].includes(voiceMode) ? 'completed' : 
                voiceMode === 'processing' ? 'active' : 'pending'
              }`}>
                2. Voice Feedback
              </div>
              <div className={`progress-step ${
                voiceMode === 'complete' ? 'completed' : 
                ['writing'].includes(voiceMode) ? 'active' : 'pending'
              }`}>
                3. Written Answer
              </div>
            </div>

            {/* Bot Question Display */}
            {botQuestion && (
              <div className="bot-question">
                🤖 Bot asked: "{botQuestion}"
              </div>
            )}

            <div className="voice-status">
              {voiceMode === 'connecting' && "🔗 Connecting to your voice assistant..."}
              {voiceMode === 'listening' && !hasVoiceResponse && "🎧 Listen to the question, then click the microphone to answer!"}
              {voiceMode === 'processing' && "🤖 Voice Bot is analyzing your response..."}
              {voiceMode === 'vocal_feedback' && "💬 Voice Bot is giving you feedback about your answer"}
              {voiceMode === 'prompting' && "✍️ Voice Bot says: 'Now please write your answer in the text box below'"}
              {voiceMode === 'writing' && "📝 Complete your written response"}
              {voiceMode === 'complete' && "✅ Excellent work!"}
            </div>

            <div className="voice-controls">
              {voiceMode === 'listening' && !hasVoiceResponse && (
                <>
                  <button
                    className={`mic-button ${isRecording ? 'recording' : ''}`}
                    onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
                    disabled={voiceMode === 'processing'}
                  >
                    {isRecording ? '🔴' : '🎤'}
                  </button>
                  {isRecording && (
                    <div className="audio-visualizer">
                      <div className="audio-bar"></div>
                      <div className="audio-bar"></div>
                      <div className="audio-bar"></div>
                      <div className="audio-bar"></div>
                      <div className="audio-bar"></div>
                    </div>
                  )}
                </>
              )}
              
              {voiceMode === 'processing' && (
                <button className="mic-button processing" disabled>
                  ⏳
                </button>
              )}

              {hasVoiceResponse && voiceMode !== 'complete' && (
                <button className="btn-reset-voice" onClick={resetVoiceSession}>
                  Record Again
                </button>
              )}
            </div>

            {/* Voice Feedback */}
            {voiceFeedback && (
              <div className="voice-feedback-section">
                <div style={{ color: '#4caf50', fontWeight: 'bold', marginBottom: '10px' }}>
                  Voice Response Received! ✓
                </div>
                <div className="voice-transcript">
                  "I heard: {voiceFeedback.transcript}"
                </div>
                <div style={{ color: '#333', fontSize: '14px' }}>
                  {voiceFeedback.feedback}
                </div>
              </div>
            )}
          </div>

          {/* Question Section */}
          <div className="question-section">
            <div className="answer-field">
              <label className="field-label">Your Answer</label>
              <input
                type="text"
                className={`answer-input ${hasVoiceResponse ? 'voice-filled' : ''}`}
                placeholder={hasVoiceResponse ? "Confirm or edit your voice answer" : "Voice Bot will ask you to type here"}
                value={titleAnswer}
                onChange={(e) => setTitleAnswer(e.target.value)}
                disabled={isLoading || voiceMode === 'listening' || voiceMode === 'processing' || voiceMode === 'vocal_feedback'}
              />
              {hasVoiceResponse && (
                <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                  ✓ Pre-filled from your voice response
                </div>
              )}
            </div>
          </div>

          {/* Text Feedback Section */}
          {feedback && (
            <div className={`feedback-section ${feedback.isCorrect ? 'correct' : 'incorrect'}`}>
              <div className={`feedback-title ${feedback.isCorrect ? 'correct' : 'incorrect'}`}>
                {feedback.isCorrect ? '✓ Correct!' : '✗ Incorrect'}
              </div>
              <div className="feedback-message">
                {feedback.message}
              </div>
              {showAnswer && feedback.correct_answer && (
                <div style={{
                  background: '#e8f5e8',
                  border: '1px solid #28a745',
                  borderRadius: '10px',
                  padding: '15px',
                  marginTop: '15px'
                }}>
                  <div style={{
                    fontFamily: 'Sen, sans-serif',
                    fontSize: '14px',
                    fontWeight: 600,
                    color: '#28a745',
                    marginBottom: '8px'
                  }}>
                    Correct Answer:
                  </div>
                  <div style={{
                    fontFamily: 'Sen, sans-serif',
                    fontSize: '16px',
                    color: '#333',
                    fontWeight: 500
                  }}>
                    {feedback.correct_answer}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Button Section */}
          <div className="button-section">
            {!feedback ? (
              <button 
                className="btn-next"
                onClick={handleNextQuestion}
                disabled={!titleAnswer.trim() || isLoading || voiceMode === 'listening' || voiceMode === 'connecting' || voiceMode === 'processing' || voiceMode === 'vocal_feedback'}
              >
                {isLoading ? (
                  <>
                    <span style={{
                      display: 'inline-block',
                      width: '16px',
                      height: '16px',
                      border: '2px solid #ffffff',
                      borderRadius: '50%',
                      borderTopColor: 'transparent',
                      animation: 'spin 1s ease-in-out infinite',
                      marginRight: '8px'
                    }}></span>
                    CHECKING...
                  </>
                ) : (
                  'CHECK ANSWER'
                )}
              </button>
            ) : (
              <div style={{ display: 'flex', gap: '15px' }}>
                {!feedback.isCorrect && (
                  <button 
                    className="btn-try-again"
                    onClick={handleTryAgain}
                  >
                    TRY AGAIN
                  </button>
                )}
                <button 
                  className="btn-proceed"
                  onClick={handleProceedToNext}
                >
                  NEXT QUESTION
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="footer-section">
        <img 
          src="/footer.png" 
          alt="Footer" 
          className="footer-img"
        />
      </div>
    </div>
  );
}