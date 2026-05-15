import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, CheckCircle, X, ShieldOff, ShieldCheck, Skull, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface AlertOverlayProps {
  type: "scammed" | "safe";
  show: boolean;
  onClose: () => void;
}

// Floating particle component
const Particle = ({ color, delay, index }: { color: string; delay: number; index: number }) => {
  const angle = (index / 12) * Math.PI * 2;
  const distance = 120 + Math.random() * 80;
  const x = Math.cos(angle) * distance;
  const y = Math.sin(angle) * distance;

  return (
    <motion.div
      initial={{ opacity: 1, x: 0, y: 0, scale: 1 }}
      animate={{ opacity: 0, x, y, scale: 0 }}
      transition={{ duration: 1.2, delay, ease: "easeOut" }}
      className="absolute top-1/2 left-1/2 w-2 h-2 rounded-full"
      style={{ backgroundColor: color }}
    />
  );
};

const AlertOverlay = ({ type, show, onClose }: AlertOverlayProps) => {
  const [showParticles, setShowParticles] = useState(false);
  const [showBreakdown, setShowBreakdown] = useState(false);
  const [actionMessage, setActionMessage] = useState("");

  useEffect(() => {
    if (show) {
      setShowParticles(true);
      setShowBreakdown(false);
      setActionMessage("");
      const timer = setTimeout(() => setShowParticles(false), 2000);
      return () => clearTimeout(timer);
    }
  }, [show]);

  const isScam = type === "scammed";
  const particleColor = isScam ? "hsl(0, 84%, 60%)" : "hsl(142, 71%, 45%)";

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="fixed inset-0 z-50 flex items-center justify-center"
          onClick={onClose}
        >
          {/* Background with screen flash */}
          <motion.div
            initial={{ backgroundColor: isScam ? "hsla(0,84%,60%,0.3)" : "hsla(142,71%,45%,0.2)" }}
            animate={{ backgroundColor: "hsla(222,47%,5%,0.95)" }}
            transition={{ duration: 0.5 }}
            className="absolute inset-0 backdrop-blur-md"
          />

          {/* Scan lines overlay for scam */}
          {isScam && (
            <motion.div
              initial={{ opacity: 0.8 }}
              animate={{ opacity: 0 }}
              transition={{ duration: 2 }}
              className="absolute inset-0 pointer-events-none"
              style={{
                backgroundImage: "repeating-linear-gradient(0deg, transparent, transparent 2px, hsla(0,84%,60%,0.03) 2px, hsla(0,84%,60%,0.03) 4px)",
              }}
            />
          )}

          {/* Radial glow */}
          <motion.div
            initial={{ opacity: 0.8, scale: 0.5 }}
            animate={{ opacity: 0.15, scale: 2.5 }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            className={cn(
              "absolute w-96 h-96 rounded-full blur-3xl pointer-events-none",
              isScam ? "bg-danger" : "bg-safe"
            )}
          />

          {/* Particles */}
          {showParticles && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              {Array.from({ length: 16 }).map((_, i) => (
                <Particle key={i} color={particleColor} delay={i * 0.03} index={i} />
              ))}
            </div>
          )}

          {/* Main card */}
          <motion.div
            initial={{ scale: 0.3, opacity: 0, rotateX: 40 }}
            animate={{ scale: 1, opacity: 1, rotateX: 0, x: isScam ? [0, -2, 2, -1, 0] : 0 }}
            exit={{ scale: 0.5, opacity: 0, y: 30 }}
            transition={{ type: "spring", damping: 12, stiffness: 150, duration: 0.45 }}
            className={cn(
              "relative z-10 flex flex-col items-center gap-5 p-6 md:p-8 rounded-2xl border w-[min(92vw,28rem)] text-center bg-card/85 backdrop-blur-xl",
              isScam ? "border-danger/40 alert-pulse-danger" : "border-safe/40"
            )}
            style={{
              boxShadow: isScam
                ? "0 0 60px hsla(0,84%,60%,0.3), 0 0 120px hsla(0,84%,60%,0.1), inset 0 1px 0 hsla(0,84%,60%,0.1)"
                : "0 0 60px hsla(142,71%,45%,0.3), 0 0 120px hsla(142,71%,45%,0.1), inset 0 1px 0 hsla(142,71%,45%,0.1)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <button onClick={onClose} className="absolute top-4 right-4 text-muted-foreground hover:text-foreground transition-colors">
              <X size={18} />
            </button>

            {/* Icon with pulsing ring */}
            <div className="relative">
              <motion.div
                animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                transition={{ duration: 2, repeat: Infinity }}
                className={cn(
                  "absolute inset-0 rounded-full",
                  isScam ? "bg-danger/20" : "bg-safe/20"
                )}
                style={{ margin: "-20px" }}
              />
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ type: "spring", damping: 10, delay: 0.2 }}
              >
                {isScam ? (
                  <div className="relative">
                    <Skull size={72} className="text-danger" style={{ filter: "drop-shadow(0 0 20px hsla(0,84%,60%,0.6))" }} />
                    <motion.div
                      animate={{ opacity: [0, 1, 0] }}
                      transition={{ duration: 0.15, repeat: 3 }}
                      className="absolute inset-0"
                    >
                      <ShieldOff size={72} className="text-danger/50" />
                    </motion.div>
                  </div>
                ) : (
                  <div className="relative">
                    <ShieldCheck size={72} className="text-safe" style={{ filter: "drop-shadow(0 0 20px hsla(142,71%,45%,0.6))" }} />
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                      className="absolute -inset-3"
                    >
                      <Sparkles size={20} className="text-safe absolute top-0 right-0" />
                    </motion.div>
                  </div>
                )}
              </motion.div>
            </div>

            {/* Glitch title for scam */}
            {isScam ? (
              <div className="relative">
                <motion.h2
                  animate={{ x: [0, -2, 3, -1, 0] }}
                  transition={{ duration: 0.3, repeat: 3, delay: 0.5 }}
                  className="text-2xl md:text-3xl font-bold text-danger text-glow-danger glitch-title"
                >
                  YOU GOT SCAMMED
                </motion.h2>
              </div>
            ) : (
              <motion.h2
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-3xl font-bold text-safe text-glow-safe"
              >
                THREAT NEUTRALIZED
              </motion.h2>
            )}

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="text-muted-foreground text-sm leading-relaxed max-w-xs"
            >
              {isScam
                ? "In a real scenario, you would have lost ₹2,847. Scammers use urgency and fear to bypass your critical thinking."
                : "Excellent! You recognized the threat and refused to engage. This is exactly how you stay safe online."}
            </motion.p>

            {isScam && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.55 }}
                className="w-full rounded-lg border border-danger/20 bg-danger/5 p-3 text-left"
              >
                <p className="text-sm font-semibold text-danger mb-2">Why you got scammed:</p>
                <ul className="space-y-1 text-xs text-muted-foreground">
                  <li>- Urgency pressure</li>
                  <li>- Suspicious link</li>
                  <li>- Unknown sender</li>
                </ul>
                <p className="text-xs text-warning mt-3">Never trust urgent payment requests via SMS</p>
              </motion.div>
            )}

            {showBreakdown && isScam && (
              <motion.div
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full rounded-lg border border-border bg-secondary/30 p-3 text-left"
              >
                <p className="text-xs text-foreground font-medium mb-1">Breakdown</p>
                <p className="text-xs text-muted-foreground">The sender forced urgency and redirected payment to an unverified destination. Always cross-check from official apps or saved helpline numbers.</p>
              </motion.div>
            )}

            {/* Stats bar */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
              className={cn(
                "w-full flex items-center justify-around py-3 rounded-lg border",
                isScam ? "border-danger/20 bg-danger/5" : "border-safe/20 bg-safe/5"
              )}
            >
              <div className="text-center">
                <p className={cn("text-lg font-bold", isScam ? "text-danger" : "text-safe")}>
                  {isScam ? "₹2,847" : "₹0"}
                </p>
                <p className="text-[10px] text-muted-foreground">{isScam ? "Money Lost" : "Money Lost"}</p>
              </div>
              <div className="w-px h-8 bg-border" />
              <div className="text-center">
                <p className={cn("text-lg font-bold", isScam ? "text-danger" : "text-safe")}>
                  {isScam ? "HIGH" : "SAFE"}
                </p>
                <p className="text-[10px] text-muted-foreground">Risk Level</p>
              </div>
              <div className="w-px h-8 bg-border" />
              <div className="text-center">
                <p className={cn("text-lg font-bold", isScam ? "text-danger" : "text-safe")}>
                  {isScam ? "-15" : "+25"}
                </p>
                <p className="text-[10px] text-muted-foreground">Score</p>
              </div>
            </motion.div>

            {actionMessage && (
              <div className="w-full rounded-lg border border-cyber/30 bg-cyber/10 p-3 text-xs text-cyber">
                {actionMessage}
              </div>
            )}

            {isScam && (
              <div className="w-full grid grid-cols-2 gap-2">
                <button
                  onClick={() => setActionMessage("Report filed. Call 1930 cybercrime helpline immediately and freeze suspicious transfers.")}
                  className="py-2 rounded-lg border border-danger/30 bg-danger/10 text-danger text-sm hover:bg-danger/20 transition-all"
                >
                  Report Scam
                </button>
                <button
                  onClick={() => setActionMessage("Sender blocked. Further messages from this source will be muted and flagged.")}
                  className="py-2 rounded-lg border border-border bg-secondary/40 text-foreground text-sm hover:bg-secondary/70 transition-all"
                >
                  Block Sender
                </button>
              </div>
            )}

            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.9 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onClose}
              className={cn(
                "px-8 py-3 rounded-xl font-semibold transition-all duration-300",
                isScam
                  ? "bg-danger/20 text-danger hover:bg-danger/30 border border-danger/30"
                  : "bg-safe/20 text-safe hover:bg-safe/30 border border-safe/30"
              )}
            >
              {isScam ? "Continue" : "Continue"}
            </motion.button>

            {isScam && (
              <button
                onClick={() => setShowBreakdown((state) => !state)}
                className="text-xs text-cyber hover:text-cyber/80 transition-colors"
              >
                {showBreakdown ? "Hide Breakdown" : "See Breakdown"}
              </button>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default AlertOverlay;
