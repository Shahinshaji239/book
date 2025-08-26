import React, { useState, useRef, useEffect } from "react";
import HTMLFlipBook from "react-pageflip";

// Page Components
const PageCover = React.forwardRef(({ title, subtitle, className = '', backgroundImage, children }, ref) => (
  <div
    className={`page page-cover ${className}`}
    ref={ref}
    data-density="hard"
    style={backgroundImage ? { 
      backgroundImage: `url(${backgroundImage})`, 
      backgroundSize: 'cover', 
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat'
    } : {}}
  >
    <div className="page-content page-cover__content">
      {children}
    </div>
  </div>
));

const StoryPage = React.forwardRef(({ content, pageNumber }, ref) => {
  return (
    <div className="page story-page" ref={ref}>
      <div className="page-content">
        {content.illustration && (
          <div className="story-illustration">
            <img 
              src={content.illustration} 
              alt={content.alt}
              className="story-image"
              loading="lazy"
            />
          </div>
        )}

        {content.characterNames && (
          <div className="character-names">
            {content.characterNames.map((name, idx) => (
              <div key={idx} className="character-name">{name}</div>
            ))}
          </div>
        )}

        <div className="story-text-content">
          <p className="story-text">{content.text}</p>
          {content.subText && (
            <p className="story-subtext">{content.subText}</p>
          )}
          {content.quote && (
            <div className="story-quote">"{content.quote}"</div>
          )}
        </div>

        {content.isEnd && (
          <div className="story-end">THE END</div>
        )}

        <div className="page-number">{pageNumber}</div>
      </div>
    </div>
  );
});

// Story content array for Goldilocks
const STORY_PAGES = [
  {
    text: "Once upon a time there were three Bears, who lived together in a house of their own, in a wood.",
    characterNames: ["Little Wee Bear,", "Middle-sized Bear,", "and Great Big Bear"],
    illustration: "https://images.unsplash.com/photo-1551963831-b3b1ca40c98e?w=500&h=400&fit=crop",
    alt: "Three bears in their cozy woodland home"
  },
  {
    text: "They had each a bowl for their porridge; a little bowl for the Little Wee Bear; and a middle-sized bowl for the Middle-sized Bear; and a great bowl for the Great Big Bear.",
    illustration: "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=500&h=400&fit=crop",
    alt: "Three different sized bowls for porridge"
  },
  {
    text: "And they had each a chair to sit in; a little chair for the Little Wee Bear; and a middle-sized chair for the Middle-sized Bear; and a great chair for the Great Big Bear.",
    illustration: "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500&h=400&fit=crop",
    alt: "Three different sized chairs"
  },
  {
    text: "And they had each a bed to sleep in; a little bed for the Little Wee Bear; and a middle-sized bed for the Middle-sized Bear; and a great bed for the Great Big Bear.",
    illustration: "https://images.unsplash.com/photo-1540518614846-7eded433c457?w=500&h=400&fit=crop",
    alt: "Three different sized beds"
  },
  {
    text: "One day, after they had made the porridge for their breakfast, and poured it into their porridge-bowls, they walked out into the wood while the porridge was cooling.",
    subText: "They were polite, well-brought-up Bears who didn't want to burn their mouths by beginning too soon.",
    illustration: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500&h=400&fit=crop",
    alt: "Bears walking through the forest"
  },
  {
    text: "While they were away, a little girl called Goldilocks, who lived at the other side of the wood, passed by the house and looked in at the window.",
    subText: "She had been sent on an errand by her mother, but she was not at all a well-brought-up little girl.",
    illustration: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=500&h=400&fit=crop",
    alt: "Goldilocks peering through the window"
  },
  {
    text: "Then seeing nobody in the house, she lifted the latch. The door was not fastened, because the Bears were good Bears, who did nobody any harm.",
    subText: "So Goldilocks opened the door and went in, well pleased when she saw the porridge on the table.",
    illustration: "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=500&h=400&fit=crop",
    alt: "Goldilocks entering the bears' house"
  },
  {
    text: "First she tasted the porridge of the Great Big Bear, and that was too hot for her.",
    illustration: "https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=500&h=400&fit=crop",
    alt: "Goldilocks tasting the Great Big Bear's porridge"
  },
  {
    text: "Next she tasted the porridge of the Middle-sized Bear, but that was too cold for her.",
    illustration: "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=500&h=400&fit=crop",
    alt: "Goldilocks trying the Middle-sized Bear's porridge"
  },
  {
    text: "And then she went to the porridge of the Little Wee Bear, and tasted it, and that was neither too hot nor too cold, but just right!",
    subText: "She liked it so well that she ate it all up, every bit!",
    illustration: "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&h=400&fit=crop",
    alt: "Goldilocks eating all of Little Wee Bear's porridge"
  },
  {
    text: "Then Goldilocks, who was tired from catching butterflies instead of running her errand, sat down in the chair of the Great Big Bear, but that was too hard for her.",
    illustration: "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500&h=400&fit=crop",
    alt: "Goldilocks in the Great Big Bear's hard chair"
  },
  {
    text: "And then she sat down in the chair of the Middle-sized Bear, and that was too soft for her.",
    illustration: "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=500&h=400&fit=crop",
    alt: "Goldilocks sinking into the Middle-sized Bear's soft chair"
  },
  {
    text: "But when she sat down in the chair of the Little Wee Bear, that was neither too hard nor too soft, but just right.",
    subText: "So she seated herself in it, and there she sat till the bottom of the chair came out, and down she came, plump upon the ground!",
    illustration: "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=500&h=400&fit=crop",
    alt: "Goldilocks breaking the Little Wee Bear's chair"
  },
  {
    text: "Now, being determined to rest, Goldilocks went upstairs into the bedchamber where the Three Bears slept.",
    illustration: "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=500&h=400&fit=crop",
    alt: "Goldilocks going upstairs to the bedroom"
  },
  {
    text: "First she lay down upon the bed of the Great Big Bear, but that was too high at the head for her.",
    illustration: "https://images.unsplash.com/photo-1540518614846-7eded433c457?w=500&h=400&fit=crop",
    alt: "Goldilocks on the Great Big Bear's bed"
  },
  {
    text: "And next she lay down upon the bed of the Middle-sized Bear, and that was too high at the foot for her.",
    illustration: "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=500&h=400&fit=crop",
    alt: "Goldilocks trying the Middle-sized Bear's bed"
  },
  {
    text: "And then she lay down upon the bed of the Little Wee Bear, and that was neither too high at the head nor at the foot, but just right.",
    subText: "So she covered herself up comfortably, and lay there till she fell fast asleep.",
    illustration: "https://images.unsplash.com/photo-1541781408260-0c53119cd761?w=500&h=400&fit=crop",
    alt: "Goldilocks sleeping peacefully in Little Wee Bear's bed"
  },
  {
    text: "By this time the Three Bears thought their porridge would be cool enough, so they came home to breakfast.",
    subText: "But careless Goldilocks had left the spoon of the Great Big Bear standing in his porridge.",
    illustration: "https://images.unsplash.com/photo-1551963831-b3b1ca40c98e?w=500&h=400&fit=crop",
    alt: "The Three Bears returning home"
  },
  {
    text: "The Great Big Bear looked at his porridge and saw someone had been there.",
    quote: "SOMEBODY HAS BEEN AT MY PORRIDGE!",
    subText: "said the Great Big Bear in his great, rough, gruff voice.",
    illustration: "https://images.unsplash.com/photo-1551963831-b3b1ca40c98e?w=500&h=400&fit=crop",
    alt: "Great Big Bear discovering his disturbed porridge"
  },
  {
    text: "Then the Middle-sized Bear looked at his porridge and saw the spoon was standing in it too.",
    quote: "SOMEBODY HAS BEEN AT MY PORRIDGE!",
    subText: "said the Middle-sized Bear in his middle-sized voice.",
    illustration: "https://images.unsplash.com/photo-1551963831-b3b1ca40c98e?w=500&h=400&fit=crop",
    alt: "Middle-sized Bear finding his disturbed porridge"
  },
  {
    text: "Then the Little Wee Bear looked at his bowl, and there was the spoon in the porridge-bowl, but the porridge was all gone!",
    quote: "SOMEBODY HAS BEEN AT MY PORRIDGE, AND HAS EATEN IT ALL UP!",
    subText: "said the Little Wee Bear in his little wee voice.",
    illustration: "https://images.unsplash.com/photo-1551963831-b3b1ca40c98e?w=500&h=400&fit=crop",
    alt: "Little Wee Bear discovering his empty bowl"
  },
  {
    text: "Upon this the Three Bears began to look about them. The careless Goldilocks had not put the hard cushion straight when she rose from the Great Big Bear's chair.",
    quote: "SOMEBODY HAS BEEN SITTING IN MY CHAIR!",
    subText: "said the Great Big Bear in his great, rough, gruff voice.",
    illustration: "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500&h=400&fit=crop",
    alt: "Great Big Bear's disturbed chair"
  },
  {
    text: "And the careless Goldilocks had squashed down the soft cushion of the Middle-sized Bear.",
    quote: "SOMEBODY HAS BEEN SITTING IN MY CHAIR!",
    subText: "said the Middle-sized Bear in his middle-sized voice.",
    illustration: "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=500&h=400&fit=crop",
    alt: "Middle-sized Bear's squashed cushion"
  },
  {
    text: "But when the Little Wee Bear came to look at his chair...",
    quote: "SOMEBODY HAS BEEN SITTING IN MY CHAIR, AND HAS BROKEN IT ALL TO PIECES!",
    subText: "said the Little Wee Bear in his little wee voice.",
    illustration: "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=500&h=400&fit=crop",
    alt: "Little Wee Bear's broken chair"
  },
  {
    text: "Then the Three Bears thought they had better search upstairs in case it was a burglar, so they went up to their bedchamber.",
    illustration: "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=500&h=400&fit=crop",
    alt: "Three Bears going upstairs to investigate"
  },
  {
    text: "Goldilocks had pulled the pillow of the Great Big Bear out of its place.",
    quote: "SOMEBODY HAS BEEN LYING IN MY BED!",
    subText: "said the Great Big Bear in his great, rough, gruff voice.",
    illustration: "https://images.unsplash.com/photo-1540518614846-7eded433c457?w=500&h=400&fit=crop",
    alt: "Great Big Bear's disturbed bed"
  },
  {
    text: "And Goldilocks had pulled the bolster of the Middle-sized Bear out of its place.",
    quote: "SOMEBODY HAS BEEN LYING IN MY BED!",
    subText: "said the Middle-sized Bear in his middle-sized voice.",
    illustration: "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=500&h=400&fit=crop",
    alt: "Middle-sized Bear's messed bed"
  },
  {
    text: "But when the Little Wee Bear came to look at his bed, there was the bolster in its place, and the pillow was in its place upon the bolster. And upon the pillow...?",
    subText: "There was Goldilocks's yellow head—which was not in its place, for she had no business there!",
    illustration: "https://images.unsplash.com/photo-1541781408260-0c53119cd761?w=500&h=400&fit=crop",
    alt: "Goldilocks sleeping in Little Wee Bear's bed"
  },
  {
    text: "Now Goldilocks had heard the great, rough, gruff voice of the Great Big Bear in her sleep, but it was like the roaring of wind. She had heard the middle-sized voice too, like someone speaking in a dream.",
    quote: "SOMEBODY HAS BEEN LYING IN MY BED,—AND HERE SHE IS STILL!",
    subText: "But when she heard the little wee voice of the Little Wee Bear, it was so sharp and shrill that it awakened her at once!",
    illustration: "https://images.unsplash.com/photo-1541781408260-0c53119cd761?w=500&h=400&fit=crop",
    alt: "Goldilocks waking up to find the Three Bears"
  },
  {
    text: "Up she started, and when she saw the Three Bears on one side of the bed, she tumbled herself out at the other, and ran to the window.",
    subText: "The window was open, because the Bears, like good, tidy Bears as they were, always opened their bedchamber window when they got up in the morning.",
    illustration: "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=500&h=400&fit=crop",
    alt: "Goldilocks jumping out the window to escape"
  },
  {
    text: "So naughty, frightened little Goldilocks jumped out the window! And whether she broke her neck in the fall, or ran into the wood and was lost there, or found her way out and got whipped for being a bad girl and playing truant, no one can say.",
    subText: "But the Three Bears never saw anything more of her.",
    illustration: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500&h=400&fit=crop",
    alt: "Goldilocks running away through the forest",
    isEnd: true
  }
];

export default function GoldilocksFlipbook() {
  const [isMobile, setIsMobile] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [isBookOpen, setIsBookOpen] = useState(false);
  const [imagesLoaded, setImagesLoaded] = useState(false);
  const [showQuizButton, setShowQuizButton] = useState(false);
  const flipBookRef = useRef();

  useEffect(() => {
    const checkMobile = () => {
      const mobileState = window.innerWidth <= 768;
      if (isMobile !== mobileState) {
        setIsMobile(mobileState);
      }
    };
    checkMobile();

    let resizeTimeout;
    const handleResize = () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(checkMobile, 150);
    };

    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      clearTimeout(resizeTimeout);
    };
  }, [isMobile]);

  // Preload images
  useEffect(() => {
    const preloadImages = async () => {
      const imagePromises = STORY_PAGES.filter(page => page.illustration).map((page) => {
        return new Promise((resolve, reject) => {
          const img = new Image();
          img.src = page.illustration;
          img.onload = resolve;
          img.onerror = reject;
        });
      });

      try {
        await Promise.all(imagePromises);
        setImagesLoaded(true);
        console.log('All images loaded successfully');
      } catch (error) {
        console.error('Error loading images:', error);
        setImagesLoaded(true); // Continue even if some images fail
      }
    };

    preloadImages();
  }, []);

  const totalBookPages = STORY_PAGES.length + 2; // Front cover + Pages + Back cover

  const handleFlip = (e) => {
    const newPage = e.data;
    setCurrentPage(newPage);

    if (newPage > 0 && !isBookOpen) {
      setIsBookOpen(true);
    }

    const lastPageIndex = flipBookRef.current?.pageFlip()?.getPageCount() - 1;

    if (newPage === lastPageIndex) {
      if (!showQuizButton) {
        console.log('Reached back cover, showing quiz button');
        setTimeout(() => setShowQuizButton(true), 500);
      }
    }
  };

  const handleOpenBook = () => {
    if (!isBookOpen && flipBookRef.current && flipBookRef.current.pageFlip()) {
      const currentBookPageIdx = flipBookRef.current.pageFlip().getCurrentPageIndex();
      if (currentBookPageIdx === 0) {
        flipBookRef.current.pageFlip().flipNext();
        setIsBookOpen(true);
      }
    }
  };

  const startQuiz = () => {
    console.log("Starting Goldilocks Quiz...");
    alert("Quiz feature would be implemented here! 🐻");
  };

  if (!imagesLoaded) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <p>Loading Goldilocks and the Three Bears...</p>
      </div>
    );
  }

  return (
    <div className="flipbook-app">
      <style jsx>{`
        .flipbook-app {
          min-height: 100vh;
          background: linear-gradient(135deg, #fff8dc 0%, #daa520 100%);
          font-family: 'Georgia', 'Times New Roman', serif;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 20px;
          position: relative;
        }

        .book-title {
          text-align: center;
          margin-bottom: 20px;
          color: #8b4513;
        }

        .book-title h1 {
          font-size: 2.5rem;
          margin-bottom: 0.5rem;
          text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        .book-title p {
          font-size: 1.2rem;
          color: #a0522d;
          font-style: italic;
        }

        .flipbook-wrapper {
          width: 100%;
          max-width: 1100px;
          height: auto;
          aspect-ratio: 1100 / 733;
          display: flex;
          justify-content: center;
          align-items: center;
          margin-bottom: 20px;
          cursor: ${!isBookOpen ? 'pointer' : 'default'};
        }

        .flipbook-instance {
          width: 100%;
          height: 100%;
          box-shadow: 0 10px 25px rgba(139, 69, 19, 0.15), 0 6px 10px rgba(139, 69, 19, 0.1);
          border-radius: 8px;
          overflow: hidden;
        }

        .page {
          width: 100%;
          height: 100%;
          display: flex;
          overflow: hidden;
          background: #fff8dc;
        }

        .page-content {
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
          position: relative;
          padding: 25px;
          box-sizing: border-box;
        }

        .page-cover {
          background-size: cover;
          background-position: center;
          background-repeat: no-repeat;
          display: flex;
          align-items: center;
          justify-content: center;
          text-align: center;
          color: #8b4513;
          padding: 20px;
        }

        .page-cover__content {
          padding: 20px;
          border-radius: 8px;
          text-align: center;
        }

        .cover-title {
          font-size: 3rem;
          font-weight: bold;
          color: #8b4513;
          text-shadow: 2px 2px 4px rgba(255,255,255,0.5);
          margin-bottom: 1rem;
          letter-spacing: 2px;
        }

        .cover-subtitle {
          font-size: 1.5rem;
          color: #a0522d;
          font-style: italic;
          margin-bottom: 1rem;
        }

        .cover-author {
          font-size: 1.3rem;
          color: #d2691e;
          font-weight: 600;
          letter-spacing: 1px;
        }

        .story-page {
          background: #fff8dc;
        }

        .story-illustration {
          text-align: center;
          margin-bottom: 20px;
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 200px;
        }

        .story-image {
          max-width: 100%;
          max-height: 300px;
          height: auto;
          border-radius: 10px;
          box-shadow: 0 4px 12px rgba(139, 69, 19, 0.2);
          object-fit: contain;
        }

        .character-names {
          text-align: center;
          font-size: 1.2rem;
          font-style: italic;
          color: #cd853f;
          margin: 15px 0;
          padding: 15px;
          background: rgba(205, 133, 63, 0.1);
          border-radius: 8px;
          border: 2px solid rgba(205, 133, 63, 0.3);
        }

        .character-name {
          margin: 5px 0;
        }

        .story-text-content {
          margin-top: auto;
          padding: 20px;
          background: rgba(255, 255, 255, 0.8);
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          border: 1px solid rgba(139, 69, 19, 0.2);
        }

        .story-text {
          font-size: 1.1rem;
          line-height: 1.8;
          text-align: left;
          color: #654321;
          margin-bottom: 15px;
          text-indent: 0;
          font-weight: 400;
          letter-spacing: 0.3px;
          word-spacing: 1px;
        }

        .story-subtext {
          font-size: 1rem;
          line-height: 1.7;
          text-align: left;
          color: #a0522d;
          font-style: italic;
          margin-bottom: 15px;
          text-indent: 0;
          letter-spacing: 0.2px;
          word-spacing: 1px;
          border-top: 1px solid rgba(139, 69, 19, 0.3);
          padding-top: 15px;
        }

        .story-quote {
          font-size: 1.1rem;
          line-height: 1.6;
          text-align: center;
          color: #8b4513;
          font-weight: bold;
          margin: 15px 0;
          padding: 15px;
          background: rgba(218, 165, 32, 0.1);
          border-radius: 8px;
          border-left: 4px solid #daa520;
          font-style: italic;
        }

        .story-end {
          text-align: center;
          font-size: 2rem;
          font-weight: bold;
          color: #8b4513;
          margin: 20px 0;
          padding: 20px;
          background: linear-gradient(45deg, rgba(218, 165, 32, 0.2), rgba(255, 215, 0, 0.1));
          border-radius: 15px;
          border: 2px solid #daa520;
          position: relative;
        }

        .story-end::before,
        .story-end::after {
          content: "🐻";
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
          font-size: 1.5rem;
        }

        .story-end::before {
          left: 20px;
        }

        .story-end::after {
          right: 20px;
        }

        .page-number {
          position: absolute;
          bottom: 10px;
          right: 15px;
          font-size: 0.8rem;
          color: #8b4513;
          background-color: rgba(255,255,255,0.7);
          padding: 2px 6px;
          border-radius: 3px;
        }

        .navigation-controls {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 20px;
          margin-top: 10px;
          color: #8b4513;
        }

        .nav-button {
          background-color: #daa520;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          font-family: 'Georgia', serif;
        }

        .nav-button:hover:not(:disabled) {
          background-color: #b8860b;
          transform: translateY(-2px);
        }

        .nav-button:disabled {
          background-color: #ccc;
          opacity: 0.6;
          cursor: not-allowed;
        }

        .quiz-button {
          background-color: #ff6347;
          font-size: 1.1rem;
          padding: 12px 24px;
          animation: pulse 2s infinite;
        }

        .quiz-button:hover {
          background-color: #dc143c;
        }

        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }

        .page-indicator {
          font-size: 1rem;
          font-weight: 500;
          color: #a0522d;
          font-family: 'Georgia', serif;
        }

        .mobile-tip {
          margin-top: 10px;
          font-size: 0.9rem;
          color: #8b4513;
          text-align: center;
          font-style: italic;
        }

        .loading-screen {
          position: fixed;
          inset: 0;
          background: linear-gradient(135deg, #fff8dc 0%, #daa520 100%);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          color: #8b4513;
          z-index: 9999;
        }

        .loading-spinner {
          width: 50px;
          height: 50px;
          border: 4px solid #e9ecef;
          border-top: 4px solid #daa520;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 20px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .flipbook-app {
            padding: 10px;
          }

          .book-title h1 {
            font-size: 2rem;
          }

          .flipbook-wrapper {
            aspect-ratio: 550 / 733;
            height: 70vh;
            max-height: 600px;
            max-width: 90vw;
            width: auto;
            margin: 10px auto;
          }

          .story-text {
            font-size: 1rem;
            line-height: 1.7;
          }

          .story-subtext {
            font-size: 0.95rem;
            line-height: 1.6;
          }

          .story-text-content {
            padding: 15px;
          }

          .cover-title {
            font-size: 2rem;
          }

          .cover-subtitle {
            font-size: 1.2rem;
          }

          .cover-author {
            font-size: 1rem;
          }

          .story-end {
            font-size: 1.5rem;
            padding: 15px;
          }

          .page-content {
            padding: 15px;
          }
        }
      `}</style>

      <div className="book-title">
        <h1>Goldilocks and the Three Bears</h1>
        <p>A Classic Fairy Tale</p>
      </div>

      <div
        className="flipbook-wrapper"
        onClick={!isBookOpen ? handleOpenBook : undefined}
        role={!isBookOpen ? "button" : undefined}
        aria-label={!isBookOpen ? "Open Goldilocks storybook" : undefined}
        tabIndex={!isBookOpen ? 0 : undefined}
        onKeyPress={!isBookOpen ? (e) => { 
          if (e.key === 'Enter' || e.key === ' ') handleOpenBook(); 
        } : undefined}
      >
        <HTMLFlipBook
          key={isMobile ? 'mobile-book' : 'desktop-book'}
          ref={flipBookRef}
          width={isMobile ? 350 : 550}
          height={isMobile ? 500 : 733}
          minWidth={isMobile ? 300 : 400}
          maxWidth={isMobile ? 400 : 1000}
          minHeight={isMobile ? 450 : 600}
          maxHeight={isMobile ? 600 : 1350}
          size="stretch"
          maxShadowOpacity={0.5}
          showCover={true}
          mobileScrollSupport={true}
          onFlip={handleFlip}
          className="flipbook-instance"
          swipeDistance={isMobile ? 20 : 50}
          usePortrait={isMobile}
          startPage={0}
          drawShadow={true}
          flippingTime={1000}
          useMouseEvents={true}
          autoSize={false}
          showPageCorners={!isMobile}
          disableFlipByClick={false}
          clickEventForward={false}
          style={{
            touchAction: isMobile ? 'none' : 'auto'
          }}
        >
          {/* Front Cover */}
          <PageCover
            className="front-cover"
            backgroundImage="https://images.unsplash.com/photo-1551963831-b3b1ca40c98e?w=800&h=600&fit=crop"
          >
            <div className="cover-title">GOLDILOCKS<br/>AND THE<br/>THREE BEARS</div>
            <div className="cover-subtitle">A Classic Fairy Tale</div>
            <div className="cover-author">TRADITIONAL STORY</div>
          </PageCover>

          {/* Story Pages */}
          {STORY_PAGES.map((page, index) => (
            <StoryPage 
              key={`story-page-${index}`} 
              content={page} 
              pageNumber={index + 2}
            />
          ))}

          {/* Back Cover */}
          <PageCover
            className="back-cover"
            backgroundImage="https://images.unsplash.com/photo-1551963831-b3b1ca40c98e?w=800&h=600&fit=crop"
          >
            <div style={{
              padding: '40px',
              background: 'rgba(255, 248, 220, 0.9)',
              borderRadius: '15px',
              textAlign: 'center',
              position: 'relative',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center'
            }}>
              <h2 style={{color: '#8b4513', marginBottom: '20px'}}>The End</h2>
              <p style={{color: '#a0522d', fontSize: '1.1rem', lineHeight: 1.6}}>
                This classic fairy tale teaches us about respect for others' property<br/>
                and the consequences of our actions.
              </p>
              
              {/* Quiz Button */}
              <button
                onClick={startQuiz}
                style={{
                  position: 'absolute',
                  bottom: '20px',
                  right: '20px',
                  backgroundColor: '#daa520',
                  color: 'white',
                  border: 'none',
                  padding: '10px 16px',
                  borderRadius: '8px',
                  fontSize: '0.9rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  fontFamily: 'Georgia, serif',
                  boxShadow: '0 2px 8px rgba(139, 69, 19, 0.2)'
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = '#b8860b';
                  e.target.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = '#daa520';
                  e.target.style.transform = 'translateY(0)';
                }}
                aria-label="Start quiz"
              >
                Quiz Time! 🐻
              </button>
            </div>
          </PageCover>
        </HTMLFlipBook>
      </div>

      <div className="navigation-controls">
        {!isMobile && (
          <button
            onClick={() => flipBookRef.current?.pageFlip().flipPrev()}
            className="nav-button"
            disabled={currentPage === 0}
            aria-label="Previous page"
          >
            ← Previous
          </button>
        )}
        
        <span className="page-indicator">
          Page {currentPage + 1} of {totalBookPages}
        </span>
        
        {showQuizButton ? (
          <button
            onClick={startQuiz}
            className="nav-button quiz-button"
            aria-label="Start reading quiz"
          >
            Start Quiz! 🎯
          </button>
        ) : !isMobile && (
          <button
            onClick={() => flipBookRef.current?.pageFlip().flipNext()}
            className="nav-button"
            disabled={currentPage >= totalBookPages - 1}
            aria-label="Next page"
          >
            Next →
          </button>
        )}
      </div>

      {isMobile && !isBookOpen && (
        <div className="mobile-tip">
          📖 Tap the book to open and start reading!
        </div>
      )}

      {isMobile && isBookOpen && (
        <p className="mobile-tip">👆 Swipe left/right to flip pages</p>
      )}
    </div>
  );
}