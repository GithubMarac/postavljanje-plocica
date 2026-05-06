import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Ruler, Hammer, Droplets, Phone, CheckCircle2, Mail, MapPin } from 'lucide-react';

// --- MOSAIC SPLASH SCREEN COMPONENT ---
const MosaicSplash = ({ onComplete }) => {
  const gridItems = Array.from({ length: 25 }); // 5x5 grid

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
          transition={{
            duration: 0.8,
            delay: Math.random() * 1.5,
            ease: 'easeInOut',
          }}
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

// --- WHATSAPP FLOATING BUTTON (fixed SVG) ---
const WhatsAppButton = () => (
  <a
    href="https://wa.me/385912345678" // Ovdje unesi svoj broj
    target="_blank"
    rel="noopener noreferrer"
    className="fixed bottom-6 right-6 z-50 bg-[#25D366] text-white p-4 rounded-full shadow-2xl hover:scale-110 transition-transform flex items-center justify-center group"
  >
    <svg
      viewBox="0 0 24 24"
      width="28"
      height="28"
      stroke="none"
      strokeWidth="0"
      fill="currentColor"
      className="text-white"
    >
      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
    </svg>
    <span className="absolute right-16 bg-slate-900 text-white text-sm px-3 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
      Pošalji poruku
    </span>
  </a>
);

// --- MAIN PAGE COMPONENT ---
export default function App() {
  const [isLoading, setIsLoading] = useState(true);

  // Stabilan callback za splash screen
  const handleSplashComplete = useCallback(() => {
    setIsLoading(false);
  }, []);

  const fadeUp = {
    hidden: { opacity: 0, y: 40 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8 } },
  };

  return (
    <div className="bg-slate-50 text-slate-800 font-sans">
      <AnimatePresence>
        {isLoading && <MosaicSplash onComplete={handleSplashComplete} />}
      </AnimatePresence>

      {!isLoading && (
        <>
          <WhatsAppButton />

          {/* SCROLL SNAP KONTEJNER */}
          <main className="h-screen w-full overflow-y-auto snap-y snap-mandatory scroll-smooth">
            {/* 1. SEKCIJA: O MENI */}
            <section className="h-screen w-full snap-start relative flex flex-col items-center justify-center bg-slate-900 text-white overflow-hidden px-4">
              <div className="absolute inset-0 opacity-30 bg-[url('https://images.unsplash.com/photo-1620641788421-7a1c342ea42e?q=80&w=2000&auto=format&fit=crop')] bg-cover bg-center" />
              <div className="relative z-10 text-center max-w-5xl mx-auto">
                <motion.h1
                  variants={fadeUp}
                  initial="hidden"
                  whileInView="visible"
                  className="text-4xl md:text-6xl font-extrabold mb-6"
                >
                  Vrhunska <span className="text-amber-500">Keramika Zagreb</span>
                </motion.h1>
                <motion.p
                  variants={fadeUp}
                  initial="hidden"
                  whileInView="visible"
                  className="text-lg md:text-xl mb-12 text-slate-300 max-w-2xl mx-auto"
                >
                  S dugogodišnjim iskustvom specijalizirani smo za postavljanje svih vrsta keramike,
                  porculana i mozaika. Svakom projektu pristupamo s maksimalnom pažnjom.
                </motion.p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {[
                    { icon: <Ruler size={32} />, title: 'Preciznost', desc: 'Laserska nivelacija' },
                    { icon: <Hammer size={32} />, title: 'Kvaliteta', desc: 'Vrhunski materijali' },
                    { icon: <Droplets size={32} />, title: 'Zaštita', desc: 'Hidroizolacija' },
                  ].map((item, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.2 }}
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

            {/* 2. SEKCIJA: MOJI RADOVI */}
            <section className="h-screen w-full snap-start flex flex-col items-center justify-center bg-slate-50 px-4 py-12">
              <div className="max-w-6xl w-full mx-auto">
                <motion.div initial="hidden" whileInView="visible" variants={fadeUp} className="text-center mb-10">
                  <h2 className="text-3xl md:text-5xl font-bold text-slate-900">Moji Radovi</h2>
                  <p className="text-slate-500 mt-2">Galerija nedavnih projekata</p>
                </motion.div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
                  {[1, 2, 3, 4, 5, 6, 7, 8].map((item, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, scale: 0.9 }}
                      whileInView={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.1 }}
                      className="aspect-square bg-slate-200 rounded-xl overflow-hidden relative group shadow-sm"
                    >
                      {/* Ovdje ubacite prave slike sa src="..." unutar img taga */}
                      <div className="absolute inset-0 bg-slate-300 flex items-center justify-center text-slate-500">
                        Slika {item}
                      </div>
                      <div className="absolute inset-0 bg-amber-500/90 opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-center justify-center">
                        <span className="font-bold text-white text-lg tracking-wide">Povećaj</span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </section>

            {/* 3. SEKCIJA: CJENIK (completed) */}
            <section className="h-screen w-full snap-start flex flex-col items-center justify-center bg-slate-900 text-white px-4">
              <div className="max-w-4xl w-full mx-auto">
                <motion.div
                  initial="hidden"
                  whileInView="visible"
                  variants={fadeUp}
                  className="text-center mb-12"
                >
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
        </>
      )}
    </div>
  );
}