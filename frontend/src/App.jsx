import React, { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import PrescriptionCard from './components/PrescriptionCard';

const API_BASE_URL = "https://uncover-backend.onrender.com"; 
// const API_BASE_URL = "http://localhost:8000";

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [aiMessage, setAiMessage] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setResult(null); // Reset previous card
    setAiMessage(''); // Reset previous message

    try {
      const response = await fetch(`${API_BASE_URL}/recommend`, { // Ensure URL is full if not proxied
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) throw new Error('Failed to fetch recommendations');

      const data = await response.json();
      
      // 1. Always set the message
      setAiMessage(data.recommendation_text);
      
      // 2. Only set the card if treatments exist
      if (data.related_treatments && data.related_treatments.length > 0) {
        setResult(data.related_treatments[0]);
      } else {
        setResult(null); // Ensure card is hidden if empty
      }

    } catch (error) {
      console.error(error);
      setAiMessage("Sorry, we couldn't fetch a recommendation right now.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50 flex flex-col items-center justify-center p-6 bg-[url('https://images.unsplash.com/photo-1616394584738-fc6e612e71b9?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center bg-no-repeat relative">
      <div className="absolute inset-0 bg-white/70 backdrop-blur-sm"></div>

      <div className="relative z-10 w-full max-w-3xl">
        <header className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-thin tracking-tight mb-4">Uncover.</h1>
          <p className="text-neutral-500 font-light">Advanced Skincare & Hair Restoration</p>
        </header>

        <form onSubmit={handleSearch} className="mb-16 relative">
          <input
            type="text"
            className="w-full bg-transparent border-b border-neutral-300 py-4 text-center text-xl focus:outline-none focus:border-black transition-colors placeholder:text-neutral-300"
            placeholder="Tell us about your skin/hair concern..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button 
            type="submit" 
            className="absolute right-0 top-1/2 -translate-y-1/2 p-2 hover:bg-neutral-100 rounded-full transition-colors"
            disabled={loading}
          >
            {loading ? <Loader2 className="w-6 h-6 animate-spin text-neutral-400" /> : <Search className="w-6 h-6 text-neutral-400" />}
          </button>
        </form>

        <AnimatePresence>
          {loading && (
             <motion.div 
               initial={{ opacity: 0 }} 
               animate={{ opacity: 1 }} 
               exit={{ opacity: 0 }}
               className="space-y-4 max-w-2xl mx-auto"
             >
               <div className="h-64 bg-[#E8D5C4]/20 rounded-3xl animate-pulse"></div>
               <div className="h-4 w-2/3 bg-neutral-200 rounded animate-pulse mx-auto"></div>
             </motion.div>
          )}

          {/* FIXED SECTION: Show if not loading AND (we have a result OR a message) */}
          {!loading && (result || aiMessage) && (
            <div className="space-y-8">
              
              {/* Only show Card if result exists */}
              {result && <PrescriptionCard data={result} />}
              
              {/* Always show Message if it exists */}
              {aiMessage && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="bg-white p-6 rounded-2xl shadow-sm border border-neutral-100 max-w-2xl mx-auto"
                >
                  <div className="flex gap-4">
                    <div className="w-8 h-8 rounded-full bg-black shrink-0"></div>
                    <div>
                      <h3 className="text-sm font-semibold mb-1">Dr. Uncover AI</h3>
                      <p className="text-neutral-600 leading-relaxed text-sm">{aiMessage}</p>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

export default App;