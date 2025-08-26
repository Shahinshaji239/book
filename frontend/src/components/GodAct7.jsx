import React, { useState } from "react";
import { FaSearch, FaRegBell } from "react-icons/fa";
import { IoIosArrowDown } from "react-icons/io";
import Header from "./Header";


export default function GodAct7() {
  const [currentQuestion, setCurrentQuestion] = useState(7);
  const [favouriteCharacterAnswer, setFavouriteCharacterAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showAnswer, setShowAnswer] = useState(false);
  
  const totalQuestions = 9;

  const submitAnswer = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/check-goldilocks-favourite-character/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          answer: favouriteCharacterAnswer.trim()
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.error) {
        setFeedback({ message: data.error, is_correct: false });
      } else {
        setFeedback(data);
        setShowAnswer(data.show_answer);
      }
    } catch (error) {
      console.error('Network error:', error);
      if (error.message.includes('404')) {
        setFeedback({ message: 'API endpoint not found. Please check if the backend server is running.', is_correct: false });
      } else {
        setFeedback({ message: 'Network error. Please check your connection and try again.', is_correct: false });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleNextQuestion = async () => {
    if (favouriteCharacterAnswer.trim()) {
      if (currentQuestion === 7) {
        // For question 7, check the answer first
        await submitAnswer();
      } else {
        // For subsequent questions, proceed directly
        console.log('Favourite character answer:', favouriteCharacterAnswer);
        setCurrentQuestion(currentQuestion + 1);
        setFeedback(null);
        setShowAnswer(false);
      }
    } else {
      alert('Please write about your favourite character before proceeding.');
    }
  };

  const handleProceedToNext = () => {
    // Logic to go to Question 8 - you can implement routing here
    console.log('Proceeding to Question 8...');
    // Example: navigate('/question8') or setCurrentQuestion(8)
    alert('Question 8 will be implemented next!');
  };

  const handleTryAgain = () => {
    setFavouriteCharacterAnswer('');
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
            font-size: 22px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
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
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
          }

          .sentence-starters {
            font-family: 'Sen', sans-serif;
            font-size: 14px;
            color: #666;
            margin-bottom: 15px;
            font-style: italic;
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
            min-height: 120px;
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
          
          .btn-next:hover {
            background: #46a8c7;
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(91, 192, 222, 0.4);
          }
          
          .btn-next:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
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
          }
          
          .feedback-section.correct {
            border-left-color: #28a745;
            background: linear-gradient(135deg, #f8fff9 0%, #ffffff 100%);
          }
          
          .feedback-section.incorrect {
            border-left-color: #dc3545;
            background: linear-gradient(135deg, #fff8f8 0%, #ffffff 100%);
          }
          
          .feedback-section.partial {
            border-left-color: #ffc107;
            background: linear-gradient(135deg, #fffdf5 0%, #ffffff 100%);
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
          
          .feedback-title.partial {
            color: #ffc107;
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
      
          
          @media (max-width: 1200px) {
            .main-content {
              padding: 40px;
              gap: 30px;
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
              padding: 30px 20px;
              gap: 30px;
              text-align: center;
            }
            
            .book-cover {
              width: 220px;
              height: 280px;
            }
            
            .banner-title {
              font-size: 28px;
            }
            
            .banner-section {
              padding: 0 20px;
              height: 160px;
            }
            
            .content-with-button {
              max-width: 100%;
            }
            
            .button-section {
              justify-content: center;
            }
          }
        `}
      </style>

      {/* Header */}
      <Header />
      
             {/* Banner Section */}
       <div className="banner-section">
          <img 
            src="/banner.png" 
            alt="Banner Background" 
            className="banner-img"
          />
          <div className="banner-content">
            <h1 className="banner-title">My Favourite Character</h1>
          </div>
          <div className="question-indicator">
            QUESTION {currentQuestion}/{totalQuestions}
          </div>
        </div>
        
        {/* Yellow Strip */}
 
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
           {/* Question Section */}
           <div className="question-section">
             <div className="answer-field">
               <div className="field-subtitle">WRITE 1-2 SENTENCES</div>
               <div className="field-label">
                 Sentence starters: My favourite character is... / I like them because...
               </div>
               <textarea
                 className="answer-textarea"
                 placeholder="type answer here"
                 value={favouriteCharacterAnswer}
                 onChange={(e) => setFavouriteCharacterAnswer(e.target.value)}
                 rows="6"
                 disabled={isLoading}
               />
             </div>
           </div>

           {/* Feedback Section */}
           {feedback && (
             <div className={`feedback-section ${
               feedback.is_correct ? 'correct' : 
               feedback.feedback_type === 'partial' ? 'partial' : 'incorrect'
             }`}>
               <div className={`feedback-title ${
                 feedback.is_correct ? 'correct' : 
                 feedback.feedback_type === 'partial' ? 'partial' : 'incorrect'
               }`}>
                 {feedback.is_correct ? '✓ Great Job!' : 
                  feedback.feedback_type === 'partial' ? '~ Good Start' : '✗ Needs More Detail'}
               </div>
               <div className="feedback-message">
                 {feedback.message}
               </div>
               {showAnswer && feedback.correct_answer && (
                 <div className="correct-answer">
                   <div className="correct-answer-title">Example Answer:</div>
                   <div className="correct-answer-text">{feedback.correct_answer}</div>
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
                 disabled={!favouriteCharacterAnswer.trim() || isLoading}
               >
                 {isLoading ? (
                   <>
                     <span className="loading-spinner"></span>
                     CHECKING...
                   </>
                 ) : (
                   'CHECK ANSWER'
                 )}
               </button>
             ) : (
               <div style={{ display: 'flex', gap: '15px' }}>
                 {!feedback.is_correct && (
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