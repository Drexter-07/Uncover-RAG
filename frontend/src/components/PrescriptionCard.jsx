import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, Sparkles, AlertCircle, Zap } from 'lucide-react';

const PrescriptionCard = ({ data }) => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-[#E8D5C4] p-8 rounded-3xl shadow-xl max-w-2xl w-full mx-auto relative overflow-hidden"
    >
      <div className="absolute top-0 right-0 -mr-8 -mt-8 w-32 h-32 bg-white/20 rounded-full blur-2xl"></div>
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-sm uppercase tracking-widest font-semibold opacity-70">Your Personalized Plan</h2>
          <Sparkles className="w-5 h-5" />
        </div>

        <h1 className="text-4xl font-light mb-2">{data.treatment}</h1>
        {data.technology && (
           <div className="flex items-center gap-2 text-sm opacity-80 mb-6">
             <Zap className="w-4 h-4" />
             <span>{data.technology}</span>
           </div>
        )}

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white/40 p-4 rounded-xl backdrop-blur-sm">
            <div className="flex items-center gap-2 mb-2 text-sm font-medium">
              <AlertCircle className="w-4 h-4" />
              Targeting
            </div>
            <p className="text-sm opacity-90 leading-relaxed">{data.concern}</p>
          </div>
          <div className="bg-white/40 p-4 rounded-xl backdrop-blur-sm">
            <div className="flex items-center gap-2 mb-2 text-sm font-medium">
              <Sparkles className="w-4 h-4" />
              Benefit
            </div>
            <p className="text-sm opacity-90 leading-relaxed">{data.benefit}</p>
          </div>
        </div>

        <div className="flex justify-between items-center pt-4 border-t border-black/10">
           <button className="bg-black text-[#E8D5C4] px-8 py-3 rounded-full font-medium flex items-center gap-2 hover:scale-105 transition-transform">
             <Calendar className="w-4 h-4" />
             Book Appointment
           </button>
           <span className="text-xs opacity-50">Valid at all Uncover clinics</span>
        </div>
      </div>
    </motion.div>
  );
};

export default PrescriptionCard;
