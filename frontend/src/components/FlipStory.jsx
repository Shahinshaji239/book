import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
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
        </div>

        {content.isEnd && (
          <div className="story-end">THE END</div>
        )}

        <div className="page-number">{pageNumber}</div>
      </div>
    </div>
  );
});

// Story content array
const STORY_PAGES = [
  {
    text: "Once upon a time there were four little Rabbits, and their names were—",
    characterNames: ["Flopsy,", "Mopsy,", "Cotton-tail,", "and Peter."],
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter08.jpg",
    alt: "The four little rabbits"
  },
  {
    text: "They lived with their Mother in a sand-bank, underneath the root of a very big fir-tree.",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter11.jpg",
    alt: "Mother Rabbit talking to her children"
  },
  {
    text: "'Now my dears,' said old Mrs. Rabbit one morning, 'you may go into the fields or down the lane, but don't go into Mr. McGregor's garden: your Father had an accident there; he was put in a pie by Mrs. McGregor.'",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter12.jpg",
    alt: "Mrs. Rabbit giving instructions"
  },
  {
    text: "'Now run along, and don't get into mischief. I am going out.'",
    subText: "Then old Mrs. Rabbit took a basket and her umbrella, and went through the wood to the baker's. She bought a loaf of brown bread and five currant buns.",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter15.jpg",
    alt: "Mrs. Rabbit leaving"
  },
  {
    text: "Flopsy, Mopsy, and Cotton-tail, who were good little bunnies, went down the lane to gather blackberries:",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter16.jpg",
    alt: "The good little bunnies"
  },
  {
    text: "But Peter, who was very naughty, ran straight away to Mr. McGregor's garden, and squeezed under the gate!",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter19.jpg",
    alt: "Peter squeezing under the gate"
  },
  {
    text: "First he ate some lettuces and some French beans; and then he ate some radishes;",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter20.jpg",
    alt: "Peter eating in the garden"
  },
  {
    text: "And then, feeling rather sick, he went to look for some parsley.",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter23.jpg",
    alt: "Peter feeling sick"
  },
  {
    text: "But round the end of a cucumber frame, whom should he meet but Mr. McGregor!",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter24.jpg",
    alt: "Peter meets Mr. McGregor"
  },
  {
    text: "Mr. McGregor was on his hands and knees planting out young cabbages, but he jumped up and ran after Peter, waving a rake and calling out, 'Stop thief!'",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter27.jpg",
    alt: "Mr. McGregor chasing Peter"
  },
  {
    text: "Peter was most dreadfully frightened; he rushed all over the garden, for he had forgotten the way back to the gate. He lost one of his shoes among the cabbages, and the other shoe amongst the potatoes.",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter28.jpg",
    alt: "Peter running frightened"
  },
  {
    text: "After losing them, he ran on four legs and went faster, so that I think he might have got away altogether if he had not unfortunately run into a gooseberry net, and got caught by the large buttons on his jacket. It was a blue jacket with brass buttons, quite new.",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter31.jpg",
    alt: "Peter caught in the gooseberry net"
  },
  {
    text: "Peter gave himself up for lost, and shed big tears; but his sobs were overheard by some friendly sparrows, who flew to him in great excitement, and implored him to exert himself.",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter32.jpg",
    alt: "Peter crying for help"
  },
  {
    text: "Mr. McGregor came up with a sieve, which he intended to pop upon the top of Peter; but Peter wriggled out just in time, leaving his jacket behind him.",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter35.jpg",
    alt: "Peter escaping from Mr. McGregor"
  },
  {
    text: "And rushed into the tool-shed, and jumped into a can. It would have been a beautiful thing to hide in, if it had not had so much water in it.",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter36.jpg",
    alt: "Peter hiding in the tool-shed"
  },
  {
    text: "Mr. McGregor was quite sure that Peter was somewhere in the tool-shed, perhaps hidden underneath a flower-pot. He began to turn them over carefully, looking under each. Presently Peter sneezed—'Kertyschoo!' Mr. McGregor was after him in no time.",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter39.jpg",
    alt: "Mr. McGregor searching"
  },
  {
    text: "And tried to put his foot upon Peter, who jumped out of a window, upsetting three plants. The window was too small for Mr. McGregor, and he was tired of running after Peter. He went back to his work.",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter40.jpg",
    alt: "Peter jumping out the window"
  },
  {
    text: "Peter sat down to rest; he was out of breath and trembling with fright, and he had not the least idea which way to go. Also he was very damp with sitting in that can. After a time he began to wander about, going lippity—lippity—not very fast, and looking all round.",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter43.jpg",
    alt: "Peter resting and frightened"
  },
  {
    text: "He found a door in a wall; but it was locked, and there was no room for a fat little rabbit to squeeze underneath. An old mouse was running in and out over the stone doorstep, carrying peas and beans to her family in the wood. Peter asked her the way to the gate, but she had such a large pea in her mouth that she could not answer. She only shook her head at him. Peter began to cry.",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter44.jpg",
    alt: "Peter finding a locked door"
  },
  {
    text: "Then he tried to find his way straight across the garden, but he became more and more puzzled. Presently, he came to a pond where Mr. McGregor filled his water-cans. A white cat was staring at some gold-fish, she sat very, very still, but now and then the tip of her tail twitched as if it were alive. Peter thought it best to go away without speaking to her; he had heard about cats from his cousin, little Benjamin Bunny.",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter47.jpg",
    alt: "Peter by the pond with the cat"
  },
  {
    text: "He went back towards the tool-shed, but suddenly, quite close to him, he heard the noise of a hoe—scr-r-ritch, scratch, scratch, scritch. Peter scuttered underneath the bushes. But presently, as nothing happened, he came out, and climbed upon a wheelbarrow and peeped over. The first thing he saw was Mr. McGregor hoeing onions. His back was turned towards Peter, and beyond him was the gate!",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter48.jpg",
    alt: "Peter seeing Mr. McGregor and the gate"
  },
  {
    text: "Peter got down very quietly off the wheelbarrow; and started running as fast as he could go, along a straight walk behind some black-currant bushes. Mr. McGregor caught sight of him at the corner, but Peter did not care. He slipped underneath the gate, and was safe at last in the wood outside the garden.",
    subText: "Mr. McGregor hung up the little jacket and the shoes for a scare-crow to frighten the blackbirds.",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter51.jpg",
    alt: "Peter escaping through the gate"
  },
  {
    text: "Peter never stopped running or looked behind him till he got home to the big fir-tree. He was so tired that he flopped down upon the nice soft sand on the floor of the rabbit-hole and shut his eyes. His mother was busy cooking; she wondered what he had done with his clothes. It was the second little jacket and pair of shoes that Peter had lost in a fortnight!",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter55.jpg",
    alt: "Peter home and exhausted"
  },
  {
    text: "I am sorry to say that Peter was not very well during the evening. His mother put him to bed, and made some camomile tea; and she gave a dose of it to Peter! 'One table-spoonful to be taken at bed-time.'",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter57.jpg",
    alt: "Peter sick in bed"
  },
  {
    text: "But Flopsy, Mopsy, and Cotton-tail had bread and milk and blackberries for supper.",
    illustration: "https://www.gutenberg.org/cache/epub/14838/images/peter58.jpg",
    alt: "The good bunnies having supper",
    isEnd: true
  }
];

export default function PeterRabbitFlipbook() {
  const navigate = useNavigate();
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
    console.log("Starting Peter Rabbit Quiz...");
    // Navigate to Readingstory component
    navigate('/readingstory');
  };

  if (!imagesLoaded) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <p>Loading The Tale of Peter Rabbit...</p>
      </div>
    );
  }

  return (
    <div className="flipbook-app">
      <style jsx>{`
        .flipbook-app {
          min-height: 100vh;
          background: linear-gradient(135deg, #faf8f1 0%, #f5f3e9 100%);
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
          color: #2d5016;
        }

        .book-title h1 {
          font-size: 2.5rem;
          margin-bottom: 0.5rem;
          text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        .book-title p {
          font-size: 1.2rem;
          color: #567c3e;
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
          box-shadow: 0 10px 25px rgba(45, 80, 22, 0.15), 0 6px 10px rgba(45, 80, 22, 0.1);
          border-radius: 8px;
          overflow: hidden;
        }

        .page {
          width: 100%;
          height: 100%;
          display: flex;
          overflow: hidden;
          background: #faf8f1;
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
          color: #2d5016;
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
          color: #2d5016;
          text-shadow: 2px 2px 4px rgba(255,255,255,0.5);
          margin-bottom: 1rem;
          letter-spacing: 2px;
        }

        .cover-subtitle {
          font-size: 1.5rem;
          color: #567c3e;
          font-style: italic;
          margin-bottom: 1rem;
        }

        .cover-author {
          font-size: 1.3rem;
          color: #8b7355;
          font-weight: 600;
          letter-spacing: 1px;
        }

        .story-page {
          background: #faf8f1;
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
          box-shadow: 0 4px 12px rgba(45, 80, 22, 0.2);
          object-fit: contain;
        }

        .character-names {
          text-align: center;
          font-size: 1.2rem;
          font-style: italic;
          color: #6b9dc2;
          margin: 15px 0;
          padding: 15px;
          background: rgba(107, 157, 194, 0.1);
          border-radius: 8px;
          border: 2px solid rgba(107, 157, 194, 0.3);
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
          border: 1px solid rgba(139, 115, 85, 0.2);
        }

        .story-text {
          font-size: 1.1rem;
          line-height: 1.8;
          text-align: left;
          color: #2c3e1d;
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
          color: #567c3e;
          font-style: italic;
          margin-bottom: 15px;
          text-indent: 0;
          letter-spacing: 0.2px;
          word-spacing: 1px;
          border-top: 1px solid rgba(139, 115, 85, 0.3);
          padding-top: 15px;
        }

        .story-end {
          text-align: center;
          font-size: 2rem;
          font-weight: bold;
          color: #2d5016;
          margin: 20px 0;
          padding: 20px;
          background: linear-gradient(45deg, rgba(143, 188, 143, 0.2), rgba(212, 175, 55, 0.1));
          border-radius: 15px;
          border: 2px solid #8fbc8f;
          position: relative;
        }

        .story-end::before,
        .story-end::after {
          content: "❦";
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
          font-size: 1.5rem;
          color: #d4af37;
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
          color: #8b7355;
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
          color: #2d5016;
        }

        .nav-button {
          background-color: #8fbc8f;
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
          background-color: #567c3e;
          transform: translateY(-2px);
        }

        .nav-button:disabled {
          background-color: #ccc;
          opacity: 0.6;
          cursor: not-allowed;
        }

        .quiz-button {
          background-color: #d4af37;
          font-size: 1.1rem;
          padding: 12px 24px;
          animation: pulse 2s infinite;
        }

        .quiz-button:hover {
          background-color: #b8941f;
        }

        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }

        .page-indicator {
          font-size: 1rem;
          font-weight: 500;
          color: #567c3e;
          font-family: 'Georgia', serif;
        }

        .mobile-tip {
          margin-top: 10px;
          font-size: 0.9rem;
          color: #8b7355;
          text-align: center;
          font-style: italic;
        }

        .loading-screen {
          position: fixed;
          inset: 0;
          background: linear-gradient(135deg, #faf8f1 0%, #f5f3e9 100%);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          color: #2d5016;
          z-index: 9999;
        }

        .loading-spinner {
          width: 50px;
          height: 50px;
          border: 4px solid #e9ecef;
          border-top: 4px solid #8fbc8f;
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
        <h1>The Tale of Peter Rabbit</h1>
        <p>by Beatrix Potter</p>
      </div>

      <div
        className="flipbook-wrapper"
        onClick={!isBookOpen ? handleOpenBook : undefined}
        role={!isBookOpen ? "button" : undefined}
        aria-label={!isBookOpen ? "Open Peter Rabbit storybook" : undefined}
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
            backgroundImage="https://www.gutenberg.org/cache/epub/14838/images/peter04.jpg"
          >
            <div className="cover-title">THE TALE OF<br/>PETER RABBIT</div>
            <div className="cover-subtitle">A Classic Children's Story</div>
            <div className="cover-author">BY BEATRIX POTTER</div>
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
            backgroundImage="https://www.gutenberg.org/cache/epub/14838/images/peter04.jpg"
          >
            <div style={{
              padding: '40px',
              background: 'rgba(250, 248, 241, 0.9)',
              borderRadius: '15px',
              textAlign: 'center',
              position: 'relative',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center'
            }}>
              <h2 style={{color: '#2d5016', marginBottom: '20px'}}>The End</h2>
              <p style={{color: '#567c3e', fontSize: '1.1rem', lineHeight: 1.6}}>
                Originally published in 1902 by Frederick Warne & Co.<br/>
                This classic children's story is now in the public domain.
              </p>
              
              {/* Next Page Button */}
              <button
                 onClick={startQuiz}
                style={{
                  position: 'absolute',
                  bottom: '20px',
                  right: '20px',
                  backgroundColor: '#8fbc8f',
                  color: 'white',
                  border: 'none',
                  padding: '10px 16px',
                  borderRadius: '8px',
                  fontSize: '0.9rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  fontFamily: 'Georgia, serif',
                  boxShadow: '0 2px 8px rgba(45, 80, 22, 0.2)'
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = '#567c3e';
                  e.target.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = '#8fbc8f';
                  e.target.style.transform = 'translateY(0)';
                }}
                aria-label="Next page"
              >
                Quiz Time!
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