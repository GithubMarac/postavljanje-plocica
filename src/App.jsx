import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence, useMotionValue } from 'framer-motion';
import { Ruler, Hammer, Droplets, X, ChevronLeft, ChevronRight } from 'lucide-react';

// --- PLACEHOLDER TOWN DATA (replace with your own images) ---
const towns = [
  {
    name: 'Zagreb',
    images: [
      'https://images.unsplash.com/photo-1600585152220-90363fe7e115?w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1600573472550-8090b5e0745e?w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1600566752355-35792bedcfea?w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1600566752447-f0fd8b3aed07?w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1600047509358-9dc75507daeb?w=800&auto=format&fit=crop',
    ],
  },
  {
    name: 'Split',
    images: [
      'https://images.unsplash.com/photo-1560185007-5f0bb1866cab?w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1560185007-cde436f6a4d0?w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1560184993-26c1f3e0bc1e?w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1560184897-502f8e9c6a2f?w=800&auto=format&fit=crop',
    ],
  },
  {
    name: 'Rijeka',
    images: [
      'https://images.unsplash.com/photo-1598928506311-c55e8b3b3b0e?w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1598928506311-0f3f4b3b3b0e?w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1598928506311-5f3f4b3b3b0e?w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1598928506311-8b3b3b3b0e?w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1598928506311-9b3b3b3b0e?w=800&auto=format&fit=crop',
    ],
  },
  {
    name: 'Osijek',
    images: [
      'https://images.unsplash.com/photo-1580587771525-78b9b9b9b9b9?w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1580587771525-78b9b9b9b9b9?w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1580587771525-78b9b9b9b9b9?w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1580587771525-78b9b9b9b9b9?w=800&auto=format&fit=crop',
    ],
  },
];

// --- MOSAIC SPLASH SCREEN ---
const MosaicSplash = ({ onComplete }) => {
  const gridItems = Array.from({ length: 25 });
  useEffect(() => {
    const timer = setTimeout(() => onComplete(), 2500);
    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <motion.div
      className="fixed inset-0 z-50 flex flex-wrap bg-slate-900"
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      {gridItems.map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 1, scale: 1 }}
          animate={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.8, delay: Math.random() * 1.5, ease: 'easeInOut' }}
          className="w-1/5 h-1/5 bg-slate-800 border border-slate-700"
        />
      ))}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-4xl md:text-6xl font-bold text-white tracking-widest uppercase"
        >
          Keramika
        </motion.h2>
      </div>
    </motion.div>
  );
};

// --- WHATSAPP FLOATING BUTTON ---
const WhatsAppButton = () => (
  <a
    href="https://wa.me/385912345678"
    target="_blank"
    rel="noopener noreferrer"
    className="fixed bottom-6 right-6 z-40 bg-[#25D366] text-white p-4 rounded-full shadow-2xl hover:scale-110 transition-transform flex items-center justify-center group"
  >
    <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor" className="text-white">
      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
    </svg>
    <span className="absolute right-16 bg-slate-900 text-white text-sm px-3 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
      Pošalji poruku
    </span>
  </a>
);

// --- SWIPEABLE IMAGE (LIGHTBOX) ---
const SwipeableImage = ({ src, onPrev, onNext }) => {
  const x = useMotionValue(0);
  const handleDragEnd = (_, info) => {
    if (info.offset.x > 100) onPrev();
    else if (info.offset.x < -100) onNext();
  };

  return (
    <motion.div
      className="w-full h-full flex items-center justify-center"
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.2}
      onDragEnd={handleDragEnd}
      style={{ x }}
    >
      <motion.img
        src={src}
        alt=""
        className="max-w-full max-h-full object-contain rounded-lg shadow-2xl"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
      />
    </motion.div>
  );
};

// --- TILE ADHESIVE TRANSITION OVERLAY (no debug, clean) ---
const TileAdhesiveTransition = ({ show }) => {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className="fixed inset-0 z-50 pointer-events-none overflow-hidden"
          initial="hidden"
          animate="sweep"
          exit="hidden"
          variants={{
            hidden: { opacity: 0 },
            sweep: { opacity: 1, transition: { staggerChildren: 0.1 } },
          }}
          key="adhesive-overlay"
        >
          {/* Ribbed sweep (trowel ridges) */}
          <motion.div
            className="absolute inset-0"
            style={{
              background: `repeating-linear-gradient(
                to right,
                rgba(255,255,255,0.4),
                rgba(255,255,255,0.4) 2px,
                transparent 2px,
                transparent 6px
              )`,
            }}
            variants={{
              hidden: { clipPath: 'inset(0 100% 0 0)' },
              sweep: {
                clipPath: 'inset(0 0% 0 0)',
                transition: { duration: 0.6, ease: 'easeInOut' },
              },
            }}
          />
          {/* Drying / brightening flash */}
          <motion.div
            className="absolute inset-0 bg-white"
            variants={{
              hidden: { opacity: 0 },
              sweep: {
                opacity: [0, 0.2, 0],
                transition: { duration: 0.7, times: [0, 0.5, 1], ease: 'easeInOut' },
              },
            }}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// --- MAIN APP ---
export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTown, setSelectedTown] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [activeSection, setActiveSection] = useState(0);
  const [showTransition, setShowTransition] = useState(false);
  const prevSectionRef = useRef(0);

  const handleSplashComplete = useCallback(() => setIsLoading(false), []);

  const fadeUp = {
    hidden: { opacity: 0, y: 40 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8 } },
  };

  // Detect which section is currently visible (snap‑scroll) ------------------
  useEffect(() => {
    const sections = document.querySelectorAll('[data-section]');
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const index = Number(entry.target.dataset.section);
            setActiveSection(index);
          }
        });
      },
      { threshold: 0.5 }
    );

    sections.forEach((sec) => observer.observe(sec));
    return () => observer.disconnect();
  }, []);

  // When section changes, trigger the overlay for 1.5 seconds ----------------
  useEffect(() => {
    if (activeSection !== prevSectionRef.current) {
      prevSectionRef.current = activeSection;
      setShowTransition(true);
      const timer = setTimeout(() => setShowTransition(false), 1500);
      return () => clearTimeout(timer);
    }
  }, [activeSection]);

  // Show one animation right after the splash screen -------------------------
  useEffect(() => {
    const initTimer = setTimeout(() => {
      setShowTransition(true);
      setTimeout(() => setShowTransition(false), 1500);
    }, 600);
    return () => clearTimeout(initTimer);
  }, []);

  return (
    <div className="bg-slate-900 text-white font-sans">
      <AnimatePresence>
        {isLoading && <MosaicSplash onComplete={handleSplashComplete} />}
      </AnimatePresence>

      {!isLoading && (
        <>
          <WhatsAppButton />

          <main className="h-screen w-full overflow-y-auto snap-y snap-mandatory scroll-smooth bg-slate-900">
            {/* 1. O MENI (Hero) */}
            <section
              data-section="0"
              className="h-screen w-full snap-start relative flex flex-col items-center justify-center bg-slate-900 overflow-hidden"
            >
              {/* Diploma background image */}
              <div
                className="absolute inset-0 opacity-20"
                style={{
                  backgroundImage: 'url(https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=1000&auto=format&fit=crop)',
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                }}
              />

              {/* Profile picture in corner (top right) */}
              <div className="absolute top-6 right-6 w-24 h-24 md:w-32 md:h-32 rounded-full overflow-hidden border-4 border-amber-500 shadow-xl z-20">
                <img
                  src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=face"
                  alt="Goran"
                  className="w-full h-full object-cover"
                />
              </div>

              <div className="relative z-10 text-center max-w-2xl mx-auto px-4">
                <motion.h1
                  variants={fadeUp}
                  initial="hidden"
                  whileInView="visible"
                  className="text-4xl md:text-6xl font-extrabold mb-8"
                >
                  O meni
                </motion.h1>
                <motion.p
                  variants={fadeUp}
                  initial="hidden"
                  whileInView="visible"
                  className="text-xl md:text-2xl text-slate-300 leading-relaxed"
                >
                  Zovem se Goran, bavim se keramikom i imam pet godina iskustva. Svaki projekt radim s velikom
                  pažnjom i preciznošću, koristeći vrhunske materijale.
                </motion.p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {[
                    { icon: <Ruler size={32} />, title: 'Preciznost', desc: 'Laserska nivelacija' },
                    { icon: <Hammer size={32} />, title: 'Kvaliteta', desc: 'Vrhunski materijali' },
                    { icon: <Droplets size={32} />, title: 'Zaštita', desc: 'Hidroizolacija' },
                  ].map((item, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, y: 20 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.2 }}
                      className="bg-slate-800/80 backdrop-blur-sm p-6 rounded-2xl border border-slate-700"
                    >
                      <div className="text-amber-500 flex justify-center mb-3">{item.icon}</div>
                      <h3 className="text-lg font-bold mb-1">{item.title}</h3>
                      <p className="text-sm text-slate-400">{item.desc}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </section>

            {/* 2. MOJI RADOVI */}
            <section
              data-section="1"
              className="min-h-screen w-full snap-start flex flex-col justify-center bg-slate-900 px-4 py-12"
            >
              <div className="max-w-6xl w-full mx-auto">
                <motion.div initial="hidden" whileInView="visible" variants={fadeUp} className="text-center mb-12">
                  <h2 className="text-3xl md:text-5xl font-bold">Moji Radovi</h2>
                  <p className="text-slate-400 mt-2">Odaberite grad za pregled projekata</p>
                </motion.div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                  {towns.map((town, townIndex) => (
                    <motion.div
                      key={town.name}
                      initial={{ opacity: 0, y: 30 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      transition={{ delay: townIndex * 0.15 }}
                      whileHover={{ scale: 1.02 }}
                      onClick={() => {
                        setSelectedTown(townIndex);
                        setCurrentIndex(0);
                      }}
                      className="cursor-pointer group relative h-80 rounded-2xl overflow-hidden shadow-lg"
                    >
                      <div className="absolute inset-0">
                        {town.images.slice(0, 4).map((img, imgIdx) => (
                          <div
                            key={imgIdx}
                            className="absolute w-full h-full bg-cover bg-center rounded-2xl transition-all duration-300 group-hover:shadow-2xl"
                            style={{
                              backgroundImage: `url(${img})`,
                              zIndex: 4 - imgIdx,
                              transform: `rotate(${imgIdx % 2 === 0 ? -2 : 2}deg) translate(${imgIdx * 4}px, ${imgIdx * 4}px)`,
                              opacity: imgIdx === 0 ? 1 : 0.9 - imgIdx * 0.1,
                              border: '2px solid rgba(255,255,255,0.15)',
                            }}
                          />
                        ))}
                      </div>
                      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent p-5 z-10">
                        <h3 className="text-2xl font-bold text-white">{town.name}</h3>
                        <p className="text-sm text-slate-300">{town.images.length} projekata</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </section>

            {/* 3. CJENIK */}
            <section
              data-section="2"
              className="h-screen w-full snap-start flex flex-col items-center justify-center bg-slate-900 px-4"
            >
              <div className="max-w-4xl w-full mx-auto">
                <motion.div initial="hidden" whileInView="visible" variants={fadeUp} className="text-center mb-12">
                  <h2 className="text-3xl md:text-5xl font-bold mb-4">Cjenik</h2>
                  <p className="text-slate-300">Transparentne cijene – bez skrivenih troškova</p>
                </motion.div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {[
                    { service: 'Keramika (m²)', price: 'od 12 €', desc: 'standardne pločice' },
                    { service: 'Porculan (m²)', price: 'od 15 €', desc: 'veliki formati' },
                    { service: 'Hidroizolacija', price: 'po dogovoru', desc: 'kupatila, terase' },
                  ].map((item, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, y: 30 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.15 }}
                      className="bg-slate-800/70 border border-slate-700 rounded-2xl p-6 text-center"
                    >
                      <div className="text-amber-400 text-xl font-bold mb-2">{item.price}</div>
                      <h3 className="font-semibold text-lg mb-1">{item.service}</h3>
                      <p className="text-sm text-slate-400">{item.desc}</p>
                    </motion.div>
                  ))}
                </div>
                <motion.p
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  transition={{ delay: 0.6 }}
                  className="text-center mt-10 text-slate-400 text-sm"
                >
                  * Za točnu ponudu pošaljite upit ili nazovite
                </motion.p>
              </div>
            </section>
          </main>

          {/* ======= SECTION TRANSITION OVERLAY (above everything) ======= */}
          <TileAdhesiveTransition show={showTransition} />

          {/* --- LIGHTBOX (town gallery) --- */}
          <AnimatePresence>
            {selectedTown !== null && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center"
                onClick={() => setSelectedTown(null)}
              >
                <button
                  onClick={() => setSelectedTown(null)}
                  className="absolute top-6 right-6 z-50 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
                >
                  <X size={32} className="text-white" />
                </button>

                {towns[selectedTown].images.length > 1 && (
                  <>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setCurrentIndex((prev) => (prev === 0 ? towns[selectedTown].images.length - 1 : prev - 1));
                      }}
                      className="absolute left-4 z-50 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
                    >
                      <ChevronLeft size={40} className="text-white" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setCurrentIndex((prev) => (prev === towns[selectedTown].images.length - 1 ? 0 : prev + 1));
                      }}
                      className="absolute right-4 z-50 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
                    >
                      <ChevronRight size={40} className="text-white" />
                    </button>
                  </>
                )}

                <div className="w-full h-full flex items-center justify-center p-8" onClick={(e) => e.stopPropagation()}>
                  <AnimatePresence mode="wait">
                    <SwipeableImage
                      key={currentIndex}
                      src={towns[selectedTown].images[currentIndex]}
                      onPrev={() =>
                        setCurrentIndex((prev) => (prev === 0 ? towns[selectedTown].images.length - 1 : prev - 1))
                      }
                      onNext={() =>
                        setCurrentIndex((prev) => (prev === towns[selectedTown].images.length - 1 ? 0 : prev + 1))
                      }
                    />
                  </AnimatePresence>
                </div>

                <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 text-white/70 text-sm">
                  {currentIndex + 1} / {towns[selectedTown].images.length}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </>
      )}
    </div>
  );
}