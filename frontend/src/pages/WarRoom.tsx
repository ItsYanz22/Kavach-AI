import React, { useMemo, useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, Clock, Phone, Video, MoreVertical, Smile, Paperclip, Mic, Send, ShieldAlert } from "lucide-react";
import ChatBubble from "@/components/ChatBubble";
import AlertOverlay from "@/components/AlertOverlay";
import { getWsUrl, getBackendUrl } from "@/lib/api";
import { useAuth } from "@/auth/AuthContext";

const WarRoom = () => {
  const navigate = useNavigate();
  const [countdown, setCountdown] = useState(30);
  const [alertType, setAlertType] = useState<"scammed" | "safe" | null>(null);
  const [showAlert, setShowAlert] = useState(false);
  const [visibleMessages, setVisibleMessages] = useState(0);
  const [typingVisible, setTypingVisible] = useState(false);
  const [paymentStage, setPaymentStage] = useState<"idle" | "processing" | "flash" | "debited">("idle");
  const [debitedAmount, setDebitedAmount] = useState(0);
  
  // Analysis Panel State
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisData, setAnalysisData] = useState<{
    highlights: any[],
    reasons: string[],
    message_parts: any[]
  } | null>(null);

  // Feedback State
  const [feedback, setFeedback] = useState<{
    title: string,
    message: string,
    type: "success" | "warning" | "danger"
  } | null>(null);
  
  const { getToken, isAuthenticated, isLoading: authLoading } = useAuth();
  const [messages, setMessages] = useState<{ sender: "received" | "sent", message: string, time: string, senderName?: string }[]>([]);
  const [userInput, setUserInput] = useState("");
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const [scenarioId, setScenarioId] = useState<string | null>(null);

  const [scamAmount, setScamAmount] = useState<number>(0);
  const [scamTip, setScamTip] = useState<string>("");
  const [scamType, setScamType] = useState<string>("");
  const [uiTitle, setUiTitle] = useState<string>("⚡ Initializing scenario...");
  const [uiDescription, setUiDescription] = useState<string>("AI is generating a personalized scam simulation for you. Please wait...");
  const [recommendedActions, setRecommendedActions] = useState<{label: string, action_id: string, type: string}[]>([]);
  const [awaitUserResponse, setAwaitUserResponse] = useState<boolean>(false);
  const [isInitialized, setIsInitialized] = useState<boolean>(false);

  const dangerMode = countdown <= 10;

  const jsonStr = (obj: any) => JSON.stringify(obj);

  const getApiUrl = () => getBackendUrl();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, authLoading, navigate]);

  const connectWs = React.useCallback((force = false) => {
    if (!isAuthenticated) return;
    
    // Prevent reconnect loops and premature closures
    if (!force && wsRef.current && (wsRef.current.readyState === WebSocket.CONNECTING || wsRef.current.readyState === WebSocket.OPEN)) {
      return;
    }
    
    if (wsRef.current) {
      wsRef.current.onclose = null; // Prevent auto-reconnect from firing
      wsRef.current.close();
      wsRef.current = null;
    }
    
    const wsUrl = getWsUrl();
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log("[WarRoom] Connected to AI scenario");
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      
      // Auto-initialize scenario on first connection
      if (!isInitialized) {
        setTimeout(() => {
          console.log("[WarRoom] Auto-starting first scenario...");
          ws.send(JSON.stringify({ message: "start", token: getToken() }));
          setIsInitialized(true);
        }, 500);
      }
    };

    ws.onclose = () => {
      console.log("[WarRoom] Disconnected from AI scenario");
      // Auto-reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        if (isAuthenticated) connectWs();
      }, 3000);
    };

    ws.onerror = (e) => {
      console.error("[WarRoom] WebSocket error:", e);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.scenario_id) setScenarioId(data.scenario_id);
        
        if (data?.message) {
          setMessages(prev => [...prev, {
            sender: "received",
            senderName: data.sender || "Infiltrator",
            message: data.message,
            time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
          }]);
          setVisibleMessages(prev => prev + 1);
          setTypingVisible(false);

          if (data.amount) setScamAmount(data.amount);
          if (data.tip) setScamTip(data.tip);
          if (data.scam_type) setScamType(data.scam_type);
          if (data.ui_title) setUiTitle(data.ui_title);
          if (data.ui_description) setUiDescription(data.ui_description);
          if (data.recommended_actions) setRecommendedActions(data.recommended_actions);
          if (data.await_user_response !== undefined) setAwaitUserResponse(data.await_user_response);
        }
      } catch (e) {
        console.error("WS Message Error:", e);
      }
    };
    wsRef.current = ws;
  }, [isAuthenticated, getToken, isInitialized]);

  useEffect(() => {
    if (isAuthenticated) {
      connectWs();
    }
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) {
        wsRef.current.onclose = null; // Prevent reconnect loop on unmount
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [isAuthenticated, connectWs]);

  const submitChoice = async (choice: string) => {
    if (!isAuthenticated) return;
    
    try {
      const response = await fetch(`${getApiUrl()}/api/learning/simulate/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${getToken()}`
        },
        body: JSON.stringify({
          scenario_id: scenarioId || "war-room-session",
          choice: choice,
          reasoning: "User interaction in War Room"
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log("Progress updated:", result.data);
      }
    } catch (err) {
      console.error("Failed to submit progress:", err);
    }
  };

  const handleSend = () => {
    if (!userInput.trim() || !wsRef.current) return;
    setMessages(prev => [...prev, {
      sender: "sent",
      message: userInput,
      time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
    }]);
    setVisibleMessages(prev => prev + 1);
    wsRef.current.send(jsonStr({ message: userInput }));
    setUserInput("");
    setTypingVisible(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleSend();
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [visibleMessages, typingVisible]);

  useEffect(() => {
    if (countdown <= 0) return;
    const timer = setInterval(() => setCountdown((c) => c - 1), 1000);
    return () => clearInterval(timer);
  }, [countdown]);

  useEffect(() => {
    if (paymentStage !== "debited") {
      setDebitedAmount(0);
      return;
    }
    let frame = 0;
    const totalFrames = 28;
    const id = setInterval(() => {
      frame += 1;
      const value = Math.min(scamAmount, Math.round((frame / totalFrames) * scamAmount));
      setDebitedAmount(value);
      if (frame >= totalFrames) clearInterval(id);
    }, 45);
    return () => clearInterval(id);
  }, [paymentStage, scamAmount]);

  const handlePayNow = () => {
    submitChoice("pay");
    setPaymentStage("processing");
    setTimeout(() => setPaymentStage("flash"), 1000);
    setTimeout(() => setPaymentStage("debited"), 1180);
    setTimeout(() => {
      setAlertType("scammed");
      setShowAlert(true);
      setPaymentStage("idle");
    }, 2600);
  };

  const handleAnalyze = async () => {
    submitChoice("analyze");
    const scamMsg = [...messages].reverse().find(m => m.sender === "received")?.message || "";
    if (!scamMsg) return;

    setIsAnalyzing(true);
    setShowAnalysis(true);
    
    try {
      const response = await fetch(`${getApiUrl()}/api/learning/simulate/explain`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${getToken()}`
        },
        body: JSON.stringify({ message: scamMsg })
      });
      
      if (response.ok) {
        const envelope = await response.json();
        setAnalysisData(envelope.data);
      }
    } catch (err) {
      console.error("Analysis failed:", err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleIgnore = () => {
    submitChoice("ignore");
    wsRef.current?.send(jsonStr({ message: "[SYSTEM: User ignored the message]" }));
    setFeedback({
      title: "🙈 Message Ignored",
      message: "Safe choice! Ignoring suspicious messages prevents scammers from confirming your number is active. However, persistent scammers may try again with higher pressure.",
      type: "success"
    });
  };

  const handleBlock = () => {
    submitChoice("block");
    setFeedback({
      title: "🚫 Sender Blocked",
      message: "EXCELLENT! Blocking is the most effective way to end a social engineering attack. You have successfully avoided this scam.",
      type: "success"
    });
    setTimeout(() => {
      setAlertType("safe");
      setShowAlert(true);
    }, 3000);
  };

  const handleReport = () => {
    submitChoice("report");
    setFeedback({
      title: "⚠️ Scam Reported",
      message: "Great job! Reporting helps protect the entire community. Authorities can track these patterns to shut down fraudulent networks.",
      type: "success"
    });
  };

  const handleChangeScenario = () => {
    setMessages([]);
    setVisibleMessages(0);
    setTypingVisible(false);
    setCountdown(30);
    setPaymentStage("idle");
    setAwaitUserResponse(false);
    setRecommendedActions([]);
    setScamAmount(0);
    setScamTip("");
    setScamType("");
    setUiTitle("⚡ Initializing scenario...");
    setUiDescription("AI is generating a personalized scam simulation for you. Please wait...");
    setAnalysisData(null);
    setFeedback(null);
    setShowAnalysis(false);
    setIsInitialized(false);
    connectWs(true); // Force reconnect
  };

  return (
    <div className={`relative flex flex-col lg:flex-row h-[calc(100vh-3rem)] transition-all duration-300 ${dangerMode ? "war-room-danger-frame war-room-shake-subtle" : ""}`}>
      {/* WhatsApp Chat Side */}
      <div className="flex-1 flex flex-col border-r border-border min-w-0">
        {/* WhatsApp Header */}
        <div className="px-4 py-2 flex items-center gap-3 wa-header shrink-0">
          <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center overflow-hidden">
            <div className="w-full h-full bg-gradient-to-br from-muted-foreground/30 to-muted-foreground/10 flex items-center justify-center">
              <span className="text-lg">👤</span>
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-medium text-foreground text-[15px] leading-tight">Unknown Sender</p>
            <AnimatePresence mode="wait">
              {typingVisible ? (
                <motion.p
                  key="typing"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-xs text-safe"
                >
                  typing...
                </motion.p>
              ) : (
                <motion.p
                  key="status"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-xs text-muted-foreground"
                >
                  +91 9876XXXXX
                </motion.p>
              )}
            </AnimatePresence>
          </div>
          <div className="flex items-center gap-5 text-muted-foreground">
            <Video className="h-5 w-5" />
            <Phone className="h-5 w-5" />
            <MoreVertical className="h-5 w-5" />
          </div>
        </div>

        {/* Chat Area with WhatsApp wallpaper */}
        <div className="flex-1 overflow-auto wa-chat-bg px-3 py-2">
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-3"
          >
            <div className="flex items-center justify-center rounded-lg border border-danger/30 bg-danger/10 px-4 py-2">
              <p className="text-xs text-danger font-medium">⚠️ Urgent payment request detected</p>
            </div>
          </motion.div>

          <div className="flex justify-center my-3">
            <div className="wa-system-msg flex items-center gap-1.5 px-3 py-1 text-[11.5px]">
              <span>🔒</span>
              <span>Messages are end-to-end encrypted. No one outside of this chat can read them.</span>
            </div>
          </div>

          <div className="flex justify-center my-2">
            <div className="wa-system-msg px-3 py-1 text-[12px] font-medium">TODAY</div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-center mb-3"
          >
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-danger/10 border border-danger/20 max-w-sm">
              <ShieldAlert className="h-4 w-4 text-danger shrink-0" />
              <span className="text-[11px] text-danger">Kavach AI: This sender is not in your contacts</span>
            </div>
          </motion.div>

          <div className="space-y-1">
            {messages.slice(0, visibleMessages).map((msg, i) => (
              <ChatBubble
                key={i}
                sender={msg.sender}
                senderName={i === 0 ? msg.senderName : undefined}
                message={msg.message}
                time={msg.time}
                delay={0}
              />
            ))}

            <AnimatePresence>
              {typingVisible && (
                <motion.div
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  className="flex justify-start"
                >
                  <div className="wa-bubble-received rounded-lg rounded-tl-none px-4 py-2.5 shadow-md">
                    <div className="flex gap-1.5 items-center h-4">
                      <motion.div animate={{ y: [0, -4, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0 }} className="w-2 h-2 rounded-full bg-muted-foreground/50" />
                      <motion.div animate={{ y: [0, -4, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.15 }} className="w-2 h-2 rounded-full bg-muted-foreground/50" />
                      <motion.div animate={{ y: [0, -4, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.3 }} className="w-2 h-2 rounded-full bg-muted-foreground/50" />
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          <div ref={chatEndRef} />
        </div>

        <motion.div
          animate={{
            backgroundColor: countdown <= 10
              ? ["hsla(0,84%,60%,0.05)", "hsla(0,84%,60%,0.15)", "hsla(0,84%,60%,0.05)"]
              : "hsla(0,84%,60%,0.05)"
          }}
          transition={{ duration: 1, repeat: Infinity }}
          className="px-4 py-2 border-t border-danger/20 flex items-center justify-between shrink-0"
        >
          <div className="flex items-center gap-2">
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              <AlertTriangle className="h-4 w-4 text-danger" />
            </motion.div>
            <span className="text-xs text-danger font-medium">Scam simulation active</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-3.5 w-3.5 text-danger" />
            <motion.span
              key={countdown}
              initial={{ scale: 1.4, opacity: 0.5 }}
              animate={{ scale: 1, opacity: 1 }}
              className={`font-mono font-bold text-sm tabular-nums ${countdown <= 10 ? "text-danger text-glow-danger neon-flicker" : "text-warning"}`}
            >
              00:{countdown.toString().padStart(2, "0")}
            </motion.span>
          </div>
        </motion.div>

        <AnimatePresence>
          {paymentStage !== "idle" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 z-40 flex items-center justify-center bg-background/80 backdrop-blur-sm"
            >
              {paymentStage === "processing" && (
                <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="rounded-xl border border-danger/30 bg-card px-8 py-6 text-center glow-danger">
                  <div className="mx-auto mb-3 h-8 w-8 rounded-full border-2 border-danger border-t-transparent animate-spin" />
                  <p className="text-danger font-semibold">Processing Payment...</p>
                </motion.div>
              )}
              {paymentStage === "flash" && (
                <>
                  <motion.div
                    initial={{ opacity: 0.1 }}
                    animate={{ opacity: [0.15, 0.95, 0.2] }}
                    transition={{ duration: 0.15 }}
                    className="absolute inset-0 bg-white"
                  />
                  <motion.div
                    initial={{ opacity: 0.1 }}
                    animate={{ opacity: [0.1, 0.7, 0.15] }}
                    transition={{ duration: 0.2 }}
                    className="absolute inset-0 bg-danger"
                  />
                </>
              )}
              {paymentStage === "debited" && (
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="rounded-xl border border-danger/40 bg-card px-8 py-6 text-center glow-danger"
                >
                  <p className="text-sm text-muted-foreground mb-2">Transaction alert</p>
                  <p className="text-xl font-bold text-danger text-glow-danger">INR {debitedAmount.toLocaleString("en-IN")} Debited from your account</p>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        <div className="px-2 py-1.5 flex items-center gap-2 wa-header shrink-0">
          <div className="flex-1 flex items-center gap-2 rounded-full wa-input-bar px-3 py-2">
            <Smile className="h-5 w-5 text-muted-foreground shrink-0" />
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message"
              className="flex-1 text-sm bg-transparent border-none outline-none text-foreground placeholder:text-muted-foreground/50"
            />
            <Paperclip className="h-5 w-5 text-muted-foreground shrink-0" />
          </div>
          <button 
            onClick={handleSend}
            disabled={!userInput.trim()}
            className="w-10 h-10 rounded-full bg-safe flex items-center justify-center shrink-0 disabled:opacity-50 transition-opacity"
          >
            {userInput.trim() ? (
              <Send className="h-5 w-5 text-safe-foreground ml-1" />
            ) : (
              <Mic className="h-5 w-5 text-safe-foreground" />
            )}
          </button>
        </div>
      </div>

      {/* Action Side */}
      <div className={`lg:w-[380px] p-6 flex flex-col justify-center gap-4 bg-card/30 backdrop-blur-sm shrink-0 border-l border-border transition-all duration-500 ${showAnalysis ? "lg:w-[450px]" : "lg:w-[380px]"}`}>
        <AnimatePresence mode="wait">
          {showAnalysis ? (
            <motion.div
              key="analysis-panel"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="h-full flex flex-col"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-cyber flex items-center gap-2">
                  <ShieldAlert className="h-5 w-5" /> Forensic Analysis
                </h2>
                <button 
                  onClick={() => setShowAnalysis(false)}
                  className="text-muted-foreground hover:text-foreground p-1"
                >
                  ✕
                </button>
              </div>

              {isAnalyzing ? (
                <div className="flex-1 flex flex-col items-center justify-center gap-4">
                  <div className="h-10 w-10 border-2 border-cyber border-t-transparent rounded-full animate-spin" />
                  <p className="text-sm text-cyber animate-pulse">Deconstructing attack patterns...</p>
                </div>
              ) : analysisData ? (
                <div className="flex-1 overflow-auto space-y-6 pr-2 custom-scrollbar">
                  <div className="p-4 rounded-xl bg-cyber/10 border border-cyber/20">
                    <p className="text-xs font-semibold text-cyber uppercase tracking-wider mb-2">Message Breakdown</p>
                    <div className="text-sm leading-relaxed text-foreground/90">
                      {analysisData.message_parts.map((part, i) => (
                        <span 
                          key={i} 
                          className={part.highlight_index !== null ? "bg-danger/20 text-danger font-medium px-0.5 rounded" : ""}
                        >
                          {part.text}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Detected Red Flags</p>
                    {analysisData.highlights.map((h, i) => (
                      <div key={i} className="flex gap-3 p-3 rounded-lg bg-secondary/30 border border-border">
                        <div className={`p-2 rounded bg-opacity-20 ${h.color === 'danger' ? 'bg-danger text-danger' : 'bg-warning text-warning'}`}>
                          <AlertTriangle className="h-4 w-4" />
                        </div>
                        <div>
                          <p className="text-sm font-bold">{h.label}</p>
                          <p className="text-xs text-muted-foreground mt-0.5">{h.tooltip}</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="p-4 rounded-xl bg-warning/5 border border-warning/20">
                    <p className="text-xs font-semibold text-warning uppercase tracking-wider mb-2">Scammer Strategy</p>
                    <ul className="list-disc list-inside space-y-1.5">
                      {analysisData.reasons.map((r, i) => (
                        <li key={i} className="text-xs text-muted-foreground">{r}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex items-center justify-center text-muted-foreground text-sm">
                  Failed to load analysis.
                </div>
              )}
              
              <button 
                onClick={() => setShowAnalysis(false)}
                className="mt-6 w-full py-3 rounded-xl bg-cyber/15 text-cyber font-bold border border-cyber/30 hover:bg-cyber/25 transition-all"
              >
                Back to Controls
              </button>
            </motion.div>
          ) : (
            <motion.div
              key="controls-panel"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <h2 className="text-xl font-bold text-foreground mb-1">{uiTitle}</h2>
              <p className="text-sm text-muted-foreground mb-4">
                {uiDescription}
              </p>

              {feedback && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`mb-4 p-4 rounded-xl border ${
                    feedback.type === "success" ? "bg-safe/10 border-safe/30 text-safe" : 
                    feedback.type === "warning" ? "bg-warning/10 border-warning/30 text-warning" : 
                    "bg-danger/10 border-danger/30 text-danger"
                  }`}
                >
                  <p className="text-sm font-bold flex items-center gap-2 mb-1">
                    {feedback.title}
                  </p>
                  <p className="text-[12px] leading-relaxed opacity-90">{feedback.message}</p>
                  <button 
                    onClick={() => setFeedback(null)}
                    className="mt-2 text-[10px] uppercase font-bold tracking-widest hover:underline"
                  >
                    Dismiss
                  </button>
                </motion.div>
              )}

              <div className="space-y-3">
                {recommendedActions.length > 0 ? (
                  recommendedActions.map((action, idx) => {
                    let btnColorClass = "bg-secondary/15 text-foreground border-border hover:bg-secondary/25";
                    let shadowColor = "hsla(0,0%,50%,0.3)";

                    if (action.action_id === "pay") {
                      btnColorClass = "bg-danger/20 text-danger border-danger/40 hover:bg-danger/30 h-16";
                      shadowColor = "hsla(0,84%,60%,0.4)";
                    } else if (action.action_id === "analyze") {
                      btnColorClass = "bg-cyber/15 text-cyber border-cyber/30 hover:bg-cyber/25";
                      shadowColor = "hsla(199,89%,48%,0.3)";
                    } else if (action.action_id === "ignore") {
                      btnColorClass = "bg-warning/15 text-warning border-warning/30 hover:bg-warning/25";
                      shadowColor = "hsla(45,93%,58%,0.3)";
                    } else if (action.action_id === "block") {
                      btnColorClass = "bg-danger/10 text-danger border-danger/20 hover:bg-danger/20";
                      shadowColor = "hsla(0,84%,60%,0.2)";
                    } else if (action.action_id === "report") {
                      btnColorClass = "bg-secondary/40 text-muted-foreground border-border hover:text-foreground";
                    }

                    return (
                      <motion.button
                        key={idx}
                        whileHover={{ scale: 1.02, boxShadow: `0 0 20px ${shadowColor}` }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => {
                          if (action.action_id === "pay") handlePayNow();
                          else if (action.action_id === "ignore") handleIgnore();
                          else if (action.action_id === "analyze") handleAnalyze();
                          else if (action.action_id === "block") handleBlock();
                          else if (action.action_id === "report") handleReport();
                        }}
                        className={`w-full py-3.5 rounded-xl font-bold border transition-all duration-300 flex items-center justify-center ${btnColorClass}`}
                      >
                        <div className="flex flex-col items-center">
                          <span className="text-sm">{action.label}</span>
                          {action.action_id === "pay" && scamAmount > 0 && (
                            <span className="text-[10px] opacity-70">Loss: ₹{scamAmount.toLocaleString("en-IN")}</span>
                          )}
                        </div>
                      </motion.button>
                    );
                  })
                ) : (
                  <div className="text-center py-8 text-muted-foreground italic text-sm">
                    No actions available...
                  </div>
                )}

                <div className="pt-4 border-t border-border/50 mt-4">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleChangeScenario}
                    className="w-full py-3 rounded-xl bg-secondary/50 text-muted-foreground text-xs font-bold border border-border hover:bg-secondary hover:text-foreground transition-all duration-300"
                  >
                    Load Next Simulation
                  </motion.button>
                </div>
              </div>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1 }}
                className="mt-6 p-4 rounded-xl border border-border bg-secondary/10 relative overflow-hidden"
              >
                <div className="absolute top-0 left-0 w-1 h-full bg-cyber" />
                <p className="text-[11px] text-muted-foreground leading-relaxed">
                  <span className="text-cyber font-bold uppercase tracking-wider block mb-1">Defense Tip</span> 
                  {scamTip}
                </p>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <AlertOverlay 
        type={alertType || "scammed"} 
        show={showAlert} 
        onClose={() => setShowAlert(false)}
        scenarioData={{
          amount: scamAmount,
          riskLevel: scamType === "critical" ? "CRITICAL" : scamType === "high" ? "HIGH" : scamType === "medium" ? "MEDIUM" : "LOW",
          scamType: scamType,
          reasons: recommendedActions.map(a => a.label) || []
        }}
      />
    </div>
  );
};

export default WarRoom;
