import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Ruler, Hammer, Droplets, Phone } from 'lucide-react';

// --- MOSAIC SPLASH SCREEN COMPONENT ---
const MosaicSplash = ({ onComplete }) => {
  const gridItems = Array.from({ length: 25 }); // 5x5 grid

  useEffect(() => {
    const timer = setTimeout(() => onComplete(), 2500); // Splash duration
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
            delay: Math.random() * 1.5, // Random mosaic dissolve effect
            ease: "easeInOut" 
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

// --- MAIN PAGE COMPONENT ---
export default function App() {
  const [isLoading, setIsLoading] = useState(true);

  // Animation variants for scrolling
  const fadeUp = {
    hidden: { opacity: 0, y: 40 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8 } }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans">
      <AnimatePresence>
        {isLoading && <MosaicSplash onComplete={() => setIsLoading(false)} />}
      </AnimatePresence>

      {!isLoading && (
        <motion.main 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }} 
          transition={{ duration: 1 }}
        >
          {/* HERO SECTION - SEO OPTIMIZED */}
          <header className="relative h-screen flex items-center justify-center bg-slate-900 text-white overflow-hidden">
            {/* Background Image Placeholder */}
            <div className="absolute inset-0 opacity-40 bg-[url('https://images.unsplash.com/photo-1620641788421-7a1c342ea42e?q=80&w=2000&auto=format&fit=crop')] bg-cover bg-center" />
            
            <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
              <motion.h1 
                className="text-5xl md:text-7xl font-extrabold mb-6 leading-tight"
                variants={fadeUp} initial="hidden" animate="visible"
              >
                Vrhunsko <span className="text-amber-500">Postavljanje Pločica Zagreb</span>
              </motion.h1>
              <motion.p 
                className="text-lg md:text-2xl mb-10 text-slate-300"
                variants={fadeUp} initial="hidden" animate="visible" transition={{ delay: 0.2 }}
              >
                Preciznost, kvaliteta i dugotrajnost. Vaš pouzdan partner za sve keramičarske radove.
              </motion.p>
              <motion.button 
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-amber-500 text-slate-900 px-8 py-4 rounded-full font-bold text-lg flex items-center gap-2 mx-auto"
              >
                <Phone size={24} />
                Zatražite Besplatnu Ponudu
              </motion.button>
            </div>
          </header>

          {/* ABOUT US SECTION */}
          <section className="py-24 px-4 max-w-6xl mx-auto">
            <motion.div 
              initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-100px" }} variants={fadeUp}
              className="text-center mb-16"
            >
              <h2 className="text-3xl md:text-5xl font-bold mb-6">O Nama</h2>
              <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                S dugogodišnjim iskustvom na području Zagreba i okolice, specijalizirani smo za postavljanje svih vrsta keramike, porculana i mozaika. Svakom projektu pristupamo s maksimalnom pažnjom prema detaljima.
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8">
              {[
                { icon: <Ruler size={40} />, title: "Preciznost", desc: "Laserska nivelacija i milimetarska točnost pri svakom rezu." },
                { icon: <Hammer size={40} />, title: "Kvalitetni Materijali", desc: "Koristimo samo najbolja ljepila i mase za fugiranje." },
                { icon: <Droplets size={40} />, title: "Hidroizolacija", desc: "Stručna priprema i zaštita kupaonica i vanjskih terasa." }
              ].map((item, index) => (
                <motion.div 
                  key={index}
                  initial="hidden" whileInView="visible" viewport={{ once: true }}
                  variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { delay: index * 0.2 }}}}
                  className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow text-center"
                >
                  <div className="text-amber-500 flex justify-center mb-4">{item.icon}</div>
                  <h3 className="text-xl font-bold mb-3">{item.title}</h3>
                  <p className="text-slate-600">{item.desc}</p>
                </motion.div>
              ))}
            </div>
          </section>

          {/* OUR WORK (GALLERY) */}
          <section className="py-24 bg-slate-900 text-white px-4">
            <div className="max-w-6xl mx-auto">
              <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp}>
                <h2 className="text-3xl md:text-5xl font-bold mb-12 text-center">Naši Radovi</h2>
              </motion.div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {/* Placeholders for gallery images */}
                {[1, 2, 3, 4, 5, 6, 7, 8].map((item, index) => (
                  <motion.div 
                    key={index}
                    initial="hidden" whileInView="visible" viewport={{ once: true }}
                    variants={{ hidden: { opacity: 0, scale: 0.9 }, visible: { opacity: 1, scale: 1, transition: { delay: index * 0.1 }}}}
                    className="aspect-square bg-slate-800 rounded-lg overflow-hidden relative group"
                  >
                    <div className="absolute inset-0 bg-slate-700 flex items-center justify-center text-slate-500">
                      Slika {item}
                    </div>
                    <div className="absolute inset-0 bg-amber-500/80 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <span className="font-bold text-lg">Povećaj</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </section>

        </motion.main>
      )}
    </div>
  );
}