import { useState, useEffect, useRef } from 'react';
import { uploadAudio } from './api';

function App() {
  const [file, setFile] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('language') || localStorage.getItem('defaultLanguage') || 'hi';
  });
  const [sourceLanguage] = useState('auto');
  
  // Translation Pipeline Selection (persisted in localStorage)
  const [pipeline, setPipeline] = useState(() => {
    return localStorage.getItem('pipeline') || 'gemini';
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  // Settings Menu States (persisted in localStorage)
  const [autoTranscribe, setAutoTranscribe] = useState(() => {
    const saved = localStorage.getItem('autoTranscribe');
    return saved ? JSON.parse(saved) : false;
  });
  const [autoLinkSuggestions, setAutoLinkSuggestions] = useState(() => {
    const saved = localStorage.getItem('autoLinkSuggestions');
    return saved ? JSON.parse(saved) : true;
  });
  const [claimExtraction, setClaimExtraction] = useState(() => {
    const saved = localStorage.getItem('claimExtraction');
    return saved ? JSON.parse(saved) : true;
  });
  const [meaningDetailLevel, setMeaningDetailLevel] = useState(() => {
    return localStorage.getItem('meaningDetailLevel') || 'full';
  });
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [linksExpanded, setLinksExpanded] = useState(false);

  const settingsRef = useRef(null);

  // Generate object URL for local audio playing
  useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setAudioUrl(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setAudioUrl(null);
    }
  }, [file]);

  // Click outside listener for the settings menu
  useEffect(() => {
    function handleClickOutside(event) {
      if (settingsRef.current && !settingsRef.current.contains(event.target)) {
        setSettingsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Upload trigger handler
  // langOverride lets callers pass the new language before React state settles
  const triggerUpload = async (fileToUpload, langOverride) => {
    const lang = langOverride ?? language;
    if (!fileToUpload || !lang) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setLinksExpanded(false);

    try {
      const data = await uploadAudio(
        fileToUpload,
        lang,
        sourceLanguage,
        pipeline,
        autoLinkSuggestions,
        claimExtraction
      );
      setResult(data);
    } catch (err) {
      setError(err.message || 'Something went wrong during translation');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = () => {
    triggerUpload(file);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setResult(null);
      setError(null);
      if (autoTranscribe) {
        triggerUpload(selectedFile);
      }
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selectedFile = e.dataTransfer.files[0];
      setFile(selectedFile);
      setResult(null);
      setError(null);
      if (autoTranscribe) {
        triggerUpload(selectedFile);
      }
    }
  };

  return (
    <div className="min-h-screen bg-[#dad3ca] flex items-center justify-center font-sans py-4 sm:py-8 px-4 relative selection:bg-[#25D366] selection:text-white">
      
      {/* Device / Chat Container */}
      <div 
        ref={settingsRef}
        className="w-full max-w-lg bg-[#efeae2] rounded-xl shadow-2xl overflow-hidden flex flex-col border border-slate-300 h-[850px] relative"
      >
        
        {/* WhatsApp Header Bar */}
        <div className="bg-[#075E54] px-4 py-3 flex items-center justify-between text-white shadow-md z-20 shrink-0">
          <div className="flex items-center gap-3">
            {/* Avatar */}
            <div className="w-10 h-10 rounded-full bg-[#128C7E] flex items-center justify-center font-black text-lg shadow-inner">
              D
            </div>
            <div>
              <h1 className="font-bold text-base leading-tight">Deva</h1>
              <p className="text-[10px] text-emerald-100 flex items-center gap-1.5 font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-[#25D366] animate-pulse" />
                Misinformation Verifier
              </p>
            </div>
          </div>

          {/* Settings Menu Icon */}
          <div className="relative">
            <button 
              onClick={() => setSettingsOpen(!settingsOpen)}
              className="p-2 hover:bg-[#128C7E] rounded-full transition-colors cursor-pointer text-white flex items-center justify-center"
              id="settings-button"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2.01.9-2.01 2S10.9 8 12 8zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" />
              </svg>
            </button>
            
            {settingsOpen && (
              <div 
                className="absolute right-0 mt-2 w-72 bg-white text-slate-800 rounded-xl shadow-xl py-4 px-4 z-50 border border-slate-200"
                id="settings-dropdown"
              >
                <h3 className="text-sm font-bold text-[#075E54] border-b border-slate-100 pb-2 mb-3">Settings</h3>
                <div className="space-y-4">
                  
                  {/* Auto-transcribe Toggle */}
                  <div className="flex items-center justify-between">
                    <div className="flex flex-col">
                      <span className="text-xs font-semibold text-slate-700">Auto-transcribe</span>
                      <span className="text-[10px] text-slate-400">Process instantly on upload</span>
                    </div>
                    <button 
                      onClick={() => {
                        const newVal = !autoTranscribe;
                        setAutoTranscribe(newVal);
                        localStorage.setItem('autoTranscribe', JSON.stringify(newVal));
                        if (newVal && file && !result && !loading) {
                          triggerUpload(file);
                        }
                      }}
                      className={`w-10 h-6 flex items-center rounded-full p-1 cursor-pointer transition-colors ${autoTranscribe ? 'bg-[#25D366]' : 'bg-slate-300'}`}
                    >
                      <div className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${autoTranscribe ? 'translate-x-4' : 'translate-x-0'}`} />
                    </button>
                  </div>

                  {/* Output Language */}
                  <div className="flex items-center justify-between">
                    <div className="flex flex-col">
                      <span className="text-xs font-semibold text-slate-700">Output Language</span>
                      <span className="text-[10px] text-slate-400">Translation output language</span>
                    </div>
                    <select
                      value={language}
                      onChange={(e) => {
                        const newVal = e.target.value;
                        setLanguage(newVal);
                        localStorage.setItem('language', newVal);
                        localStorage.setItem('defaultLanguage', newVal);
                        // Re-translate instantly if a result is already showing
                        if (file && result && !loading) {
                          triggerUpload(file, newVal);
                        }
                      }}
                      className="text-xs font-semibold bg-slate-100 border border-slate-300 rounded px-2 py-1 outline-none text-slate-800 cursor-pointer"
                    >
                      <option value="hi">Hindi</option>
                      <option value="ta">Tamil</option>
                      <option value="en">English</option>
                    </select>
                  </div>

                  {/* Meaning Detail Level */}
                  <div className="flex items-center justify-between">
                    <div className="flex flex-col">
                      <span className="text-xs font-semibold text-slate-700">Meaning Detail Level</span>
                      <span className="text-[10px] text-slate-400">Short gist or complete translation</span>
                    </div>
                    <div className="flex items-center bg-slate-100 border border-slate-300 rounded-full p-0.5">
                      <button
                        onClick={() => {
                          setMeaningDetailLevel('main');
                          localStorage.setItem('meaningDetailLevel', 'main');
                        }}
                        className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full transition-all duration-200 cursor-pointer ${
                          meaningDetailLevel === 'main'
                            ? 'bg-[#25D366] text-white shadow-sm'
                            : 'text-slate-500 hover:text-slate-700'
                        }`}
                      >
                        Main
                      </button>
                      <button
                        onClick={() => {
                          setMeaningDetailLevel('full');
                          localStorage.setItem('meaningDetailLevel', 'full');
                        }}
                        className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full transition-all duration-200 cursor-pointer ${
                          meaningDetailLevel === 'full'
                            ? 'bg-[#25D366] text-white shadow-sm'
                            : 'text-slate-500 hover:text-slate-700'
                        }`}
                      >
                        Full
                      </button>
                    </div>
                  </div>



                  {/* Auto Link Suggestions Toggle */}
                  <div className="flex items-center justify-between">
                    <div className="flex flex-col">
                      <span className="text-xs font-semibold text-slate-700">Auto link suggestions</span>
                      <span className="text-[10px] text-slate-400">Fetch matching news/study links</span>
                    </div>
                    <button 
                      onClick={() => {
                        const newVal = !autoLinkSuggestions;
                        setAutoLinkSuggestions(newVal);
                        localStorage.setItem('autoLinkSuggestions', JSON.stringify(newVal));
                      }}
                      className={`w-10 h-6 flex items-center rounded-full p-1 cursor-pointer transition-colors ${autoLinkSuggestions ? 'bg-[#25D366]' : 'bg-slate-300'}`}
                    >
                      <div className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${autoLinkSuggestions ? 'translate-x-4' : 'translate-x-0'}`} />
                    </button>
                  </div>

                  {/* Claim Extraction Toggle */}
                  <div className="flex items-center justify-between">
                    <div className="flex flex-col">
                      <span className="text-xs font-semibold text-slate-700">Claim Extraction</span>
                      <span className="text-[10px] text-slate-400">Extract core factual claim</span>
                    </div>
                    <button 
                      onClick={() => {
                        const newVal = !claimExtraction;
                        setClaimExtraction(newVal);
                        localStorage.setItem('claimExtraction', JSON.stringify(newVal));
                      }}
                      className={`w-10 h-6 flex items-center rounded-full p-1 cursor-pointer transition-colors ${claimExtraction ? 'bg-[#25D366]' : 'bg-slate-300'}`}
                    >
                      <div className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${claimExtraction ? 'translate-x-4' : 'translate-x-0'}`} />
                    </button>
                  </div>

                </div>
              </div>
            )}
          </div>
        </div>

        {/* WhatsApp Chat Message Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 relative bg-[#efeae2]">
          
          {/* System Help Banner */}
          <div className="flex justify-center my-2">
            <span className="bg-white/80 backdrop-blur-sm text-slate-600 text-[10px] font-semibold tracking-wide py-1 px-3 rounded-lg shadow-sm border border-slate-200/50 uppercase">
              🔒 End-to-end verified verification notes
            </span>
          </div>

          {/* Voice Note + Analysis — Left-aligned received message thread */}
          {file && (
            <div className="flex flex-col items-start w-full animate-fade-in gap-1">

              {/* Voice Note Bubble — received style (white, left) */}
              <div className="max-w-[85%] bg-white text-slate-800 rounded-2xl rounded-tl-none px-3.5 py-3 shadow-md">
                {/* Voice Note Info */}
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-full bg-[#efeae2] border border-slate-200 flex items-center justify-center text-[#128C7E]">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-semibold text-slate-700 truncate max-w-[180px]">{file.name}</p>
                    <p className="text-[9px] text-[#667781] font-medium mt-0.5">Voice Note</p>
                  </div>
                </div>

                {audioUrl && (
                  <div className="mt-2.5 pt-2.5 border-t border-slate-100">
                    <audio src={audioUrl} controls className="w-full h-8 rounded-lg bg-transparent" />
                  </div>
                )}

                {/* Timestamp */}
                <div className="flex items-center justify-end gap-1 mt-1">
                  <span className="text-[9px] text-[#667781] font-medium">Just now</span>
                </div>
              </div>

              {/* Loading indicator — inline below voice note */}
              {loading && (
                <div className="max-w-[85%] bg-white text-slate-800 rounded-2xl rounded-tl-none px-4 py-3 shadow-md flex items-center gap-3">
                  <svg className="animate-spin h-4 w-4 text-[#25D366]" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span className="text-xs font-semibold text-[#667781]">Analysing voice note...</span>
                </div>
              )}

              {/* Error — inline below voice note */}
              {error && (
                <div className="max-w-[85%] bg-rose-50 border border-rose-100 text-rose-800 rounded-2xl rounded-tl-none px-4 py-3 shadow-md space-y-1">
                  <p className="text-xs font-bold text-rose-700">Error</p>
                  <p className="text-xs text-rose-900 leading-tight">{error}</p>
                </div>
              )}

              {/* Analysis Result — connected block directly below voice note */}
              {result && (
                <div className="max-w-[90%] bg-white text-slate-800 rounded-2xl rounded-tl-none px-4 py-3.5 shadow-md space-y-4">

                  {/* Bubble Header */}
                  <div className="flex items-center justify-between gap-3 pb-2 border-b border-slate-100">
                    <div className="flex items-center gap-1.5">
                      <span className="px-2 py-0.5 rounded bg-emerald-50 text-[9px] font-bold text-[#128C7E] uppercase tracking-wide">
                        {result.detected_language}
                      </span>
                      <span className="text-[10px] text-[#667781] font-semibold">
                        Via {result.pipeline === 'gemini' ? 'Gemini' : 'Whisper'}
                      </span>
                    </div>
                    <span className="text-[9px] text-[#667781] font-semibold">Verified Output</span>
                  </div>

                  {/* Translated Meaning */}
                  <div className="space-y-1">
                    <h3 className="text-[10px] font-bold text-[#128C7E] uppercase tracking-widest flex items-center gap-1.5">
                      Translated Meaning ({result.target_language === 'hi' ? 'Hindi' : result.target_language === 'ta' ? 'Tamil' : 'English'})
                      <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold uppercase tracking-wide ${
                        meaningDetailLevel === 'main'
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-emerald-100 text-emerald-700'
                      }`}>
                        {meaningDetailLevel === 'main' ? 'Gist' : 'Full'}
                      </span>
                    </h3>
                    <div className="bg-emerald-50/40 border border-emerald-500/10 rounded-xl p-3 text-xs sm:text-sm text-[#128C7E] leading-relaxed font-semibold">
                      {meaningDetailLevel === 'main' && result.translated_main
                        ? result.translated_main
                        : (result.translated_full || result.translated_meaning)}
                    </div>
                  </div>

                  {/* Extracted Claim */}
                  {claimExtraction && result.extracted_claim && result.extracted_claim !== "no_claim_found" && (
                    <div className="space-y-1">
                      <h3 className="text-[10px] font-bold text-[#075E54] uppercase tracking-widest flex items-center gap-1">
                        🔍 Extracted Claim
                      </h3>
                      <div className="bg-[#f8f9fa] rounded-xl p-3 text-xs sm:text-sm text-slate-800 leading-relaxed font-medium">
                        {result.extracted_claim}
                      </div>
                    </div>
                  )}

                  {/* Related Links (WhatsApp Preview style) */}
                  {autoLinkSuggestions && result.recommendations && result.recommendations.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-slate-100">
                      <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Related Previews</h3>
                      <div className="space-y-2.5">
                        {result.recommendations
                          .slice(0, linksExpanded ? result.recommendations.length : 1)
                          .map((rec, index) => (
                          <a
                            key={index}
                            href={rec.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block bg-[#F0F2F5] hover:bg-[#E4E6EB] border-l-4 border-[#128C7E] rounded-r-lg p-2.5 transition-all duration-200 group"
                          >
                            <div className="flex items-start gap-3">
                              {/* Thumbnail */}
                              <div className="w-[50px] h-[50px] shrink-0 rounded bg-white border border-slate-200 flex items-center justify-center overflow-hidden relative">
                                {rec.image ? (
                                  <img
                                    src={rec.image}
                                    alt={rec.title}
                                    className="w-full h-full object-cover"
                                    onError={(e) => {
                                      e.target.style.display = 'none';
                                      const fallbackEl = e.target.nextSibling;
                                      if (fallbackEl) fallbackEl.style.display = 'flex';
                                    }}
                                  />
                                ) : null}
                                <div
                                  className="w-full h-full flex items-center justify-center text-slate-400"
                                  style={{ display: rec.image ? 'none' : 'flex' }}
                                >
                                  {result.content_category === 'current_affairs' ? (
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6m-6 4h3" />
                                    </svg>
                                  ) : (
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                    </svg>
                                  )}
                                </div>
                              </div>
                              {/* Details */}
                              <div className="flex-1 min-w-0">
                                <h4 className="text-xs font-semibold text-slate-800 group-hover:text-[#128C7E] truncate">
                                  {rec.title}
                                </h4>
                                <p className="text-[10px] text-slate-500 font-medium mt-0.5 truncate">
                                  Source: {rec.source}
                                </p>
                              </div>
                            </div>
                          </a>
                        ))}
                      </div>
                      {result.recommendations.length > 1 && (
                        <div className="flex justify-end">
                          <button
                            onClick={() => setLinksExpanded(prev => !prev)}
                            className="text-[11px] font-semibold text-[#25D366] hover:text-[#128C7E] transition-colors cursor-pointer bg-transparent border-none p-0 leading-none"
                          >
                            {linksExpanded ? 'View Less ▴' : 'View More ▾'}
                          </button>
                        </div>
                      )}
                    </div>
                  )}

                </div>
              )}

            </div>
          )}

          {/* Standalone loading (before any file selected) */}
          {!file && loading && (
            <div className="flex justify-start w-full animate-fade-in">
              <div className="max-w-[85%] bg-white text-slate-800 rounded-2xl rounded-tl-none px-4 py-3 shadow-md flex items-center gap-3">
                <svg className="animate-spin h-4 w-4 text-[#25D366]" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span className="text-xs font-semibold text-[#667781]">Analysing voice note...</span>
              </div>
            </div>
          )}

          {/* Standalone error (before any file selected) */}
          {!file && error && (
            <div className="flex justify-start w-full animate-fade-in">
              <div className="max-w-[85%] bg-rose-50 border border-rose-100 text-rose-800 rounded-2xl rounded-tl-none px-4 py-3 shadow-md space-y-1">
                <p className="text-xs font-bold text-rose-700">Error</p>
                <p className="text-xs text-rose-900 leading-tight">{error}</p>
              </div>
            </div>
          )}

        </div>

        {/* WhatsApp Bottom Control Bar */}
        <div className="bg-[#f0f2f5] px-4 py-3 shrink-0 flex flex-col gap-3 border-t border-slate-200 z-10">
          
          {/* Output target language pills removed */}

          {/* Action Trigger Row */}
          <div className="flex items-center gap-3">
            
            {/* Attachment paperclip (File selector) */}
            <div className="relative shrink-0 flex items-center justify-center p-2.5 rounded-full bg-white hover:bg-slate-50 border border-slate-200 cursor-pointer group text-slate-500 hover:text-slate-700 transition-colors">
              <input 
                id="audio-upload" 
                type="file" 
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                accept=".ogg,.mp3,.wav,.m4a" 
                onChange={handleFileChange} 
              />
              <svg className="w-5 h-5 rotate-45" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
              </svg>
            </div>

            {/* Selection Drag Area Box */}
            <div 
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              className={`flex-1 bg-white border border-slate-200 rounded-full py-2.5 px-4 flex items-center justify-between text-xs transition-colors ${dragActive ? 'border-[#25D366] bg-[#25D366]/5' : ''}`}
            >
              <span className="text-slate-400 font-medium truncate">
                {file ? `Selected: ${file.name}` : "Attach voice note (.ogg, .mp3, .wav)"}
              </span>
              {!file && <span className="text-[10px] text-slate-400 font-semibold uppercase">Drop Here</span>}
            </div>

            {/* Manual Send/Transcribe Button */}
            {!autoTranscribe && (
              <button
                onClick={handleUpload}
                disabled={!file || loading}
                className="p-3 bg-[#25D366] disabled:bg-slate-350 disabled:text-slate-500 rounded-full text-white shadow-md hover:scale-105 active:scale-95 transition-all cursor-pointer flex items-center justify-center shrink-0"
              >
                <svg className="w-5 h-5 rotate-90 transform translate-x-[1px] translate-y-[-1px]" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                </svg>
              </button>
            )}

          </div>

        </div>

      </div>

    </div>
  );
}

export default App;
