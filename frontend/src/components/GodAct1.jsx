import React, { useState, useEffect, useRef } from "react";
import { Room, RoomEvent, Track, ConnectionState } from 'livekit-client';
import Header from "./Header";

export default function VoiceIntegratedGodAct1() {
  // --- STATE MANAGEMENT ---

  // Question and answer states
  const [currentQuestion, setCurrentQuestion] = useState(1);
  const [titleAnswer, setTitleAnswer] = useState('');
  const [writtenFeedback, setWrittenFeedback] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showAnswer, setShowAnswer] = useState(false);

  // Voice bot workflow state machine
  const [workflowStep, setWorkflowStep] = useState('idle');
  // Steps: idle, connecting, error, step1_bot_asking, step2_user_answering, processing, step3_bot_feedback, step4_bot_prompting, step5_user_writing, step6_complete
  
  const [connectionError, setConnectionError] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [voiceTranscript, setVoiceTranscript] = useState('');
  const [vocalFeedbackMsg, setVocalFeedbackMsg] = useState('');
  const [botQuestion, setBotQuestion] = useState('');

  const totalQuestions = 9;
  const roomRef = useRef(null);
  const audioElementRef = useRef(null);
  
  // --- LIVEKIT CONNECTION & EVENT HANDLING ---

  const handleAgentMessage = (data) => {
    switch (data.type) {
      case 'question_asked':
        setBotQuestion(data.question);
        setWorkflowStep('step2_user_answering');
        break;
      case 'vocal_analysis':
        setVoiceTranscript(data.transcript);
        setVocalFeedbackMsg(data.feedback);
        // This step is very quick, so we immediately move to the next after the bot gives vocal feedback
        setTimeout(() => {
            setWorkflowStep('step4_bot_prompting');
        }, 1000); // Give a moment for the user to hear the feedback
        break;
      case 'prompt_writing':
        setTitleAnswer(voiceTranscript); // Pre-fill the input
        setWorkflowStep('step5_user_writing');
        break;
      default:
        console.log("Unknown agent message type:", data.type);
    }
  };

  const connectToVoiceBot = async () => {
    if (roomRef.current) {
        await roomRef.current.disconnect();
    }

    setWorkflowStep('connecting');
    setConnectionError(null);

    try {
      const tokenResponse = await fetch('http://localhost:8000/voice_assistant/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identity: `student_${Date.now()}`, room: `goldilocks_q${currentQuestion}` })
      });
      if (!tokenResponse.ok) throw new Error(`Token request failed`);
      
      const tokenData = await tokenResponse.json();
      if (tokenData.error || !tokenData.url || !tokenData.token) throw new Error('Invalid token data');

      const room = new Room({ adaptiveStream: true, dynacast: true });
      roomRef.current = room;

      room.on(RoomEvent.ConnectionStateChanged, (state) => {
        if (state === ConnectionState.Connected) {
          setWorkflowStep('step1_bot_asking');
        }
        if (state === ConnectionState.Failed) {
            setConnectionError("Connection failed. Please check your network and firewall settings.");
            setWorkflowStep('error');
        }
      });

      room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
        if (track.kind === Track.Kind.Audio && participant.isAgent) {
          const audioElement = track.attach();
          audioElementRef.current = audioElement;
          document.body.appendChild(audioElement);
          audioElement.play().catch(e => console.error('Autoplay was blocked:', e));
        }
      });
      
      room.on(RoomEvent.DataReceived, (payload, participant) => {
        if (participant?.isAgent) {
          const message = new TextDecoder().decode(payload);
          try {
            const data = JSON.parse(message);
            handleAgentMessage(data);
          } catch (e) {
            console.log('Non-JSON message from agent:', message);
          }
        }
      });

      await room.connect(tokenData.url, tokenData.token);
    } catch (error) {
      console.error('Error connecting to voice bot:', error);
      setConnectionError(error.message);
      setWorkflowStep('error');
    }
  };
  
  // Cleanup effect
  useEffect(() => {
    return () => {
      if (roomRef.current) roomRef.current.disconnect();
      if (audioElementRef.current) audioElementRef.current.remove();
    };
  }, []);

  // --- USER ACTIONS ---
  
  const startRecording = async () => {
    if (!roomRef.current) return;
    try {
      // Resume AudioContext on user gesture
      await roomRef.current.startAudio();
      await roomRef.current.localParticipant.setMicrophoneEnabled(true);
      setIsRecording(true);
    } catch (error) {
      alert('Could not start recording. Please allow microphone access.');
    }
  };

  const stopRecording = async () => {
    if (!roomRef.current) return;
    await roomRef.current.localParticipant.setMicrophoneEnabled(false);
    setIsRecording(false);
    setWorkflowStep('processing');
  };

  const submitWrittenAnswer = async () => {
    if (!titleAnswer.trim()) {
      alert('Please enter an answer before checking.');
      return;
    }
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/check-question${currentQuestion}/`, { // DYNAMIC ENDPOINT
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answer: titleAnswer.trim() })
      });
      const data = await response.json();
      setWrittenFeedback(data);
      setShowAnswer(data.show_answer);
      setWorkflowStep('step6_complete');
    } catch (error) {
      setWrittenFeedback({ message: 'Could not check your answer. Please try again.', is_correct: false });
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleProceedToNext = () => {
      if (currentQuestion < totalQuestions) {
          setCurrentQuestion(currentQuestion + 1);
          // Reset all states for the new question
          setTitleAnswer('');
          setWrittenFeedback(null);
          setShowAnswer(false);
          setVoiceTranscript('');
          setVocalFeedbackMsg('');
          setBotQuestion('');
          setWorkflowStep('idle'); // Go back to the initial "Start Session" screen
      } else {
          // Handle quiz completion logic
          alert("You've completed the quiz!");
      }
  };

  const handleTryAgain = () => {
      setTitleAnswer('');
      setWrittenFeedback(null);
      setShowAnswer(false);
      setWorkflowStep('step5_user_writing');
  };

  const resetVoiceSession = () => {
    setVoiceTranscript('');
    setVocalFeedbackMsg('');
    setTitleAnswer('');
    setWorkflowStep('step2_user_answering');
  };

  // --- UI RENDERING ---

  const getStatusMessage = () => {
    switch(workflowStep) {
        case 'idle': return "Click 'Start Session' to begin.";
        case 'connecting': return "🔗 Connecting to your voice assistant...";
        case 'error': return `❌ Connection Error: ${connectionError}`;
        case 'step1_bot_asking': return "🎧 Listen for the question...";
        case 'step2_user_answering': return "🎤 Click the microphone and speak your answer.";
        case 'processing': return "🤖 Analyzing your voice...";
        case 'step3_bot_feedback': return "💬 Listen to the feedback...";
        case 'step4_bot_prompting': return "💬 Listen to the feedback...";
        case 'step5_user_writing': return "✍️ Now, type your final answer below.";
        case 'step6_complete': return "✅ Great job! Let's see your result.";
        default: return "Loading...";
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
        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=Comic+Neue&display=swap');
          @import url('https://fonts.googleapis.com/css2?family=Sen:wght@400;600;800&display=swap');
          
          .voice-section { background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%); border-radius: 20px; margin-top: 20px; padding: 30px; box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1); border-left: 5px solid #2196F3; text-align: center; }
          .voice-status { font-family: 'Sen', sans-serif; font-size: 24px; font-weight: 600; margin-bottom: 20px; color: #1976D2; min-height: 60px; display: flex; align-items: center; justify-content: center; }
          .voice-controls { display: flex; justify-content: center; gap: 15px; margin: 20px 0; min-height: 80px; align-items: center; }
          .mic-button { background: #2196F3; color: white; border: none; border-radius: 50%; width: 80px; height: 80px; font-size: 24px; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3); display: flex; align-items: center; justify-content: center; }
          .mic-button:hover:not(:disabled) { background: #1976D2; transform: scale(1.05); }
          .mic-button:disabled { background: #ccc; cursor: not-allowed; transform: none; box-shadow: none; }
          .mic-button.recording { background: #f44336; animation: pulse 2s infinite; }
          .mic-button.processing { background: #ff9800; }
          @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
          .voice-feedback-section { background: #e8f5e9; border-radius: 15px; padding: 20px; margin: 20px 0; border-left: 4px solid #4caf50; text-align: left; }
          .voice-transcript { background: #f3e5f5; border-radius: 10px; padding: 15px; margin-top: 10px; font-style: italic; color: #6a1b9a; border-left: 3px solid #9c27b0; }
          .bot-question { background: #fff3e0; border-radius: 15px; padding: 20px; margin: 20px 0; border-left: 4px solid #ff9800; font-family: 'Sen', sans-serif; font-size: 18px; color: #e65100; font-weight: 600; }
          .banner-section { position: relative; width: 100%; height: auto; margin-bottom: 0; flex-shrink: 0; }
          .banner-img { width: 100%; height: auto; object-fit: cover; }
          .banner-content { position: absolute; top: 50%; left: 80px; transform: translateY(-50%); color: white; z-index: 5; }
          .banner-title { font-family: 'Gulten'; font-size: 48px; font-weight: 800; color: #2c5f7c; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); }
          .question-indicator { position: absolute; top: 50%; right: 80px; transform: translateY(-50%); background: rgba(255, 255, 255, 0.9); padding: 8px 16px; border-radius: 20px; font-family: 'Sen', sans-serif; font-weight: 600; color: #2c5f7c; font-size: 14px; }
          .main-content { flex: 1; padding: 40px 60px; display: flex; align-items: center; justify-content: center; gap: 120px; min-height: 0; }
          .content-with-button { flex: 1; max-width: 500px; display: flex; flex-direction: column; gap: 20px; margin-top: 20px; }
          .book-image-section { flex: 0 0 auto; margin-top: 20px; }
          .book-cover { width: 280px; height: 350px; border-radius: 15px; transition: transform 0.3s ease; object-fit: cover; }
          .question-section { background: white; border-radius: 20px; margin-top: 20px; padding: 40px; box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1); border-bottom: 5px solid #ffd700; }
          .answer-field { margin-bottom: 30px; }
          .field-label { font-family: 'Sen', sans-serif; font-size: 24px; font-weight: 600; color: #333; margin-bottom: 15px; display: block; }
          .answer-input { width: 100%; padding: 18px 24px; font-size: 16px; border: 2px solid #e0e0e0; border-radius: 12px; font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; transition: all 0.3s ease; box-sizing: border-box; }
          .answer-input:focus { outline: none; border-color: #5bc0de; background-color: white; box-shadow: 0 0 0 3px rgba(91, 192, 222, 0.1); }
          .answer-input.voice-filled { background-color: #e3f2fd; border-color: #2196F3; }
          .button-section { display: flex; justify-content: flex-end; gap: 15px; }
          .btn-next { background: #23A7AC; color: white; border: none; padding: 14px 32px; border-radius: 10px; font-family: 'Sen', sans-serif; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 4px 12px rgba(91, 192, 222, 0.3); }
          .btn-next:disabled { background: #ccc; cursor: not-allowed; box-shadow: none; }
          .btn-next:hover:not(:disabled) { background: #1e8a8f; transform: translateY(-2px); box-shadow: 0 6px 16px rgba(91, 192, 222, 0.4); }
          .btn-try-again { background: #dc3545; color: white; border: none; padding: 14px 32px; border-radius: 10px; font-family: 'Sen', sans-serif; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3); }
          .btn-try-again:hover { background: #c82333; transform: translateY(-2px); box-shadow: 0 6px 16px rgba(220, 53, 69, 0.4); }
          .btn-proceed { background: #28a745; color: white; border: none; padding: 14px 32px; border-radius: 10px; font-family: 'Sen', sans-serif; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3); }
          .btn-proceed:hover { background: #218838; transform: translateY(-2px); box-shadow: 0 6px 16px rgba(40, 167, 69, 0.4); }
          .btn-reset-voice { background: #ff9800; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-family: 'Sen', sans-serif; font-weight: 600; font-size: 12px; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 0.5px; }
          .btn-reset-voice:hover { background: #f57c00; }
          .feedback-section { background: white; border-radius: 20px; margin-top: 20px; padding: 30px; box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1); border-left: 5px solid; }
          .feedback-section.correct { border-left-color: #28a745; background: linear-gradient(135deg, #f8fff9 0%, #ffffff 100%); }
          .feedback-section.incorrect { border-left-color: #dc3545; background: linear-gradient(135deg, #fff8f8 0%, #ffffff 100%); }
          .feedback-title { font-family: 'Sen', sans-serif; font-size: 24px; font-weight: 600; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
          .feedback-title.correct { color: #28a745; }
          .feedback-title.incorrect { color: #dc3545; }
          .feedback-message { font-family: 'Sen', sans-serif; font-size: 16px; color: #333; margin-bottom: 20px; line-height: 1.5; }
          .correct-answer { background: #e8f5e8; border: 1px solid #28a745; border-radius: 10px; padding: 15px; margin-top: 15px; }
          .correct-answer-title { font-family: 'Sen', sans-serif; font-size: 14px; font-weight: 600; color: #28a745; margin-bottom: 8px; }
          .correct-answer-text { font-family: 'Sen', sans-serif; font-size: 16px; color: #333; font-weight: 500; }
          .footer-section { width: 100%; height: 120px; position: relative; overflow: hidden; flex-shrink: 0; }
          .footer-img { width: 100%; height: 120px; object-fit: cover; display: block; }
        `}</style>

        <Header />
      
        <div className="banner-section">
            <img src="/banner.png" alt="Banner Background" className="banner-img" />
            <div className="banner-content"><h1 className="banner-title">Book Facts</h1></div>
            <div className="question-indicator">QUESTION {currentQuestion}/{totalQuestions}</div>
        </div>

        <div className="main-content">
            <div className="book-image-section">
                <img src="/goldilocks.png" alt="Goldilocks Book Cover" className="book-cover" />
            </div>

            <div className="content-with-button">
              {workflowStep === 'idle' ? (
                  <div className="voice-section">
                      <div className="voice-status">Ready to Start Question {currentQuestion}?</div>
                      <button className="btn-proceed" onClick={connectToVoiceBot}>
                          Start Session
                      </button>
                  </div>
              ) : (
                <>
                  <div className="voice-section">
                      <div className="voice-status">{getStatusMessage()}</div>

                      {botQuestion && (
                        <div className="bot-question">
                          🤖 Bot asked: "{botQuestion}"
                        </div>
                      )}

                      <div className="voice-controls">
                        {workflowStep === 'step2_user_answering' && (
                            <button
                              className={`mic-button ${isRecording ? 'recording' : ''}`}
                              onClick={isRecording ? stopRecording : startRecording}
                            >
                              {isRecording ? '🔴' : '�'}
                            </button>
                        )}
                        {workflowStep === 'processing' && (
                          <button className="mic-button processing" disabled>⏳</button>
                        )}
                        {voiceTranscript && workflowStep !== 'step6_complete' && (
                          <button className="btn-reset-voice" onClick={resetVoiceSession}>
                            Try Speaking Again
                          </button>
                        )}
                      </div>

                      {voiceTranscript && (
                        <div className="voice-feedback-section">
                          <div style={{ fontWeight: 'bold' }}>Your spoken answer:</div>
                          <div className="voice-transcript">
                            "{voiceTranscript}"
                          </div>
                          {vocalFeedbackMsg && <p>{vocalFeedbackMsg}</p>}
                        </div>
                      )}
                  </div>

                  <div className="question-section">
                      <div className="answer-field">
                        <label className="field-label">Your Written Answer</label>
                        <input
                          type="text"
                          className={`answer-input ${voiceTranscript ? 'voice-filled' : ''}`}
                          placeholder="Type your final answer here"
                          value={titleAnswer}
                          onChange={(e) => setTitleAnswer(e.target.value)}
                          disabled={workflowStep !== 'step5_user_writing'}
                        />
                      </div>
                  </div>
                  
                  {writtenFeedback && (
                      <div className={`feedback-section ${writtenFeedback.is_correct ? 'correct' : 'incorrect'}`}>
                         <div className={`feedback-title ${writtenFeedback.is_correct ? 'correct' : 'incorrect'}`}>
                           {writtenFeedback.is_correct ? '✓ Correct!' : '✗ Needs Improvement'}
                         </div>
                         <div className="feedback-message">{writtenFeedback.message}</div>
                         {showAnswer && writtenFeedback.correct_answer && (
                           <div className="correct-answer">
                             <div className="correct-answer-title">Correct Answer:</div>
                             <div className="correct-answer-text">{writtenFeedback.correct_answer}</div>
                           </div>
                         )}
                      </div>
                  )}

                  <div className="button-section">
                    {workflowStep === 'step5_user_writing' && !writtenFeedback && (
                      <button 
                        className="btn-next"
                        onClick={submitWrittenAnswer}
                        disabled={isLoading}
                      >
                        {isLoading ? 'Checking...' : 'Check Answer'}
                      </button>
                    )}
                    
                    {workflowStep === 'step6_complete' && (
                      <div style={{ display: 'flex', gap: '15px' }}>
                        {!writtenFeedback.is_correct && (
                          <button className="btn-try-again" onClick={handleTryAgain}>
                            Try Again
                          </button>
                        )}
                        <button className="btn-proceed" onClick={handleProceedToNext}>
                          {currentQuestion < totalQuestions ? 'Next Question' : 'Finish Quiz'}
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
