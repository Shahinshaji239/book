import React, { useState } from "react";
import { FaSearch, FaRegBell } from "react-icons/fa";
import { IoIosArrowDown } from "react-icons/io";
import Header from "./Header";

export default function PetAct13() {
  const [currentQuestion, setCurrentQuestion] = useState(1);
  const [favouriteCharacterAnswer, setFavouriteCharacterAnswer] = useState('');
  
  const totalQuestions = 2;

  const handleNextQuestion = () => {
    if (favouriteCharacterAnswer.trim()) {
      console.log('Setting answer:', favouriteCharacterAnswer);
      setCurrentQuestion(currentQuestion + 1);
    } else {
      alert('Please answer where the story takes place before proceeding.');
    }
  };

  const handleTryAgain = () => {
    setFavouriteCharacterAnswer('');
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
             margin-top: 71px;
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
             padding: 30px;
             box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
             border-bottom: 5px solid #ffd700;
             height: 350px;
             display: flex;
             flex-direction: column;
             justify-content: center;
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
            <h1 className="banner-title">The Setting</h1>
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
             src="/peterrabbit.svg" 
             alt="Goldilocks and the Three Bears Book Cover"
             className="book-cover"
           />
         </div>

         {/* Content with Button Section */}
         <div className="content-with-button">
           {/* Question Section */}
           <div className="question-section">
             <div className="answer-field">
               <div className="field-label">
                  How did you feel while reading?
               </div>
               <input
                 className="answer-input"
                 placeholder="type answer here"
                 value={favouriteCharacterAnswer}
                 onChange={(e) => setFavouriteCharacterAnswer(e.target.value)}
               />
             </div>
           </div>

           {/* Button Section - Now outside the white box */}
           <div className="button-section">
             <button 
               className="btn-next"
               onClick={handleNextQuestion}
               disabled={!favouriteCharacterAnswer.trim()}
             >
               NEXT QUESTION
             </button>
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