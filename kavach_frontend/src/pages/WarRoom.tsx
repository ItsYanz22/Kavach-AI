import { useMemo, useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, Clock, Phone, Video, MoreVertical, Smile, Paperclip, Mic, Send, ShieldAlert } from "lucide-react";
import ChatBubble from "@/components/ChatBubble";
import AlertOverlay from "@/components/AlertOverlay";
import { getWsUrl } from "@/lib/api";

const WarRoom = () => {
  const navigate = useNavigate();
  const [countdown, setCountdown] = useState(30);
  const [alertType, setAlertType] = useState<"scammed" | "safe" | null>(null);
  const [showAlert, setShowAlert] = useState(false);
  const [visibleMessages, setVisibleMessages] = useState(0);
  const [typingVisible, setTypingVisible] = useState(false);
  const [paymentStage, setPaymentStage] = useState<"idle" | "processing" | "flash" | "debited">("idle");
  const [debitedAmount, setDebitedAmount] = useState(0);
  
  const [messages, setMessages] = useState<{ sender: "received" | "sent", message: string, time: string, senderName?: string }[]>([]);
  const [userInput, setUserInput] = useState("");
  const wsRef = useRef<WebSocket | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  
  const [scamAmount, setScamAmount] = useState<number>(2847);
  const [scamTip, setScamTip] = useState<string>("Real utility companies never threaten immediate disconnection via SMS, and never use shortened links for payments.");
  const [scamType, setScamType] = useState<string>("Electricity Scam");

  const dangerMode = countdown <= 10;

  const connectWs = () => {
    if (wsRef.current) wsRef.current.close();
    const wsUrl = getWsUrl();
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      ws.send(jsonStr({ message: "Generate a randomized scam scenario as if you are texting me for the first time." }));
      setTypingVisible(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.message) {
          setMessages(prev => [...prev, {
            sender: "received",
            senderName: data.sender || "Unknown",
            message: data.message,
            time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
          }]);
          setVisibleMessages(prev => prev + 1);
          setTypingVisible(false);

          if (data.amount) setScamAmount(data.amount);
          if (data.tip) setScamTip(data.tip);
          if (data.scam_type) setScamType(data.scam_type);
        }
      } catch (e) {
        console.error(e);
      }
    };
    wsRef.current = ws;
  };

  const jsonStr = (obj: any) => JSON.stringify(obj);

  useEffect(() => {
    connectWs();
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

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

  // Auto-scroll
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
    setPaymentStage("processing");
    setTimeout(() => setPaymentStage("flash"), 1000);
    setTimeout(() => setPaymentStage("debited"), 1180);
    setTimeout(() => {
      setAlertType("scammed");
      setShowAlert(true);
      setPaymentStage("idle");
    }, 2600);
  };

  const handleAnalyze = () => {
    const scamMsg = messages.find(m => m.sender === "received")?.message || "";
    navigate("/analysis", { state: { text: scamMsg } });
  };

  const handleIgnore = () => {
    setAlertType("safe");
    setShowAlert(true);
  };

  const handleChangeScenario = () => {
    setMessages([]);
    setVisibleMessages(0);
    setTypingVisible(false);
    setCountdown(30);
    setPaymentStage("idle");
    connectWs();
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

          {/* Encryption notice */}
          <div className="flex justify-center my-3">
            <div className="wa-system-msg flex items-center gap-1.5 px-3 py-1 text-[11.5px]">
              <span>🔒</span>
              <span>Messages are end-to-end encrypted. No one outside of this chat can read them.</span>
            </div>
          </div>

          {/* Date chip */}
          <div className="flex justify-center my-2">
            <div className="wa-system-msg px-3 py-1 text-[12px] font-medium">TODAY</div>
          </div>

          {/* Scam warning banner */}
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

          {/* Messages */}
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

            {/* Typing indicator */}
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

        {/* Countdown warning strip */}
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

        {/* WhatsApp Input Bar */}
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
      <div className="lg:w-[380px] p-6 flex flex-col justify-center gap-4 bg-card/30 backdrop-blur-sm shrink-0">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h2 className="text-xl font-bold text-foreground mb-1">⚡ What will you do?</h2>
          <p className="text-sm text-muted-foreground mb-6">
            You received a suspicious message. Choose wisely — one wrong move and you could lose everything.
          </p>
          <p className="text-xs text-cyber mb-4">Experience scams safely before they happen in real life.</p>

          <div className="space-y-3">
            <motion.button
              whileHover={{ scale: 1.03, boxShadow: "0 0 30px hsla(0,84%,60%,0.4)" }}
              whileTap={{ scale: 0.97 }}
              onClick={handlePayNow}
              className="w-full py-4 rounded-xl bg-danger/15 text-danger font-semibold border border-danger/30 hover:bg-danger/25 transition-all duration-300 flex items-center justify-center gap-2"
            >
              <span className="text-lg">💳</span> Pay Now — ₹{scamAmount.toLocaleString("en-IN")}
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.03, boxShadow: "0 0 30px hsla(45,93%,58%,0.3)" }}
              whileTap={{ scale: 0.97 }}
              onClick={handleIgnore}
              className="w-full py-4 rounded-xl bg-warning/15 text-warning font-semibold border border-warning/30 hover:bg-warning/25 transition-all duration-300 flex items-center justify-center gap-2"
            >
              <span className="text-lg">🚫</span> Ignore & Delete
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.03, boxShadow: "0 0 30px hsla(199,89%,48%,0.3)" }}
              whileTap={{ scale: 0.97 }}
              onClick={handleAnalyze}
              className="w-full py-4 rounded-xl bg-cyber/15 text-cyber font-semibold border border-cyber/30 hover:bg-cyber/25 transition-all duration-300 flex items-center justify-center gap-2"
            >
              <span className="text-lg">🔍</span> Analyze with Kavach AI
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={handleChangeScenario}
              className="w-full py-3 rounded-xl bg-secondary text-foreground font-semibold border border-border hover:bg-secondary/80 transition-all duration-300"
            >
              Load Next Scenario
            </motion.button>
          </div>

          {/* Hints */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 2 }}
            className="mt-6 p-3 rounded-lg border border-border bg-secondary/20"
          >
            <p className="text-[11px] text-muted-foreground leading-relaxed">
              💡 <span className="text-foreground font-medium">Tip:</span> {scamTip}
            </p>
          </motion.div>
        </motion.div>
      </div>

      <AlertOverlay type={alertType || "scammed"} show={showAlert} onClose={() => setShowAlert(false)} />
    </div>
  );
};

export default WarRoom;
