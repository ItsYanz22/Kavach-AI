import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, AlertTriangle, ShieldCheck, Loader2, WifiOff } from "lucide-react";
import CircularProgress from "@/components/CircularProgress";
import { detectScam } from "@/lib/api";

interface DetectionResult {
  isScam: boolean;
  score: number;        // 0 – 100
  reasons: string[];
}

const ScamDetector = () => {
  const [input, setInput] = useState("");
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [displayScore, setDisplayScore] = useState(0);

  // Animate score counter
  useEffect(() => {
    if (!result) {
      setDisplayScore(0);
      return;
    }
    let step = 0;
    const totalSteps = 24;
    const id = setInterval(() => {
      step += 1;
      const next = Math.min(result.score, Math.round((step / totalSteps) * result.score));
      setDisplayScore(next);
      if (step >= totalSteps) clearInterval(id);
    }, 30);
    return () => clearInterval(id);
  }, [result]);

  const analyze = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    setAnalyzing(true);
    setResult(null);
    setError(null);

    try {
      const res = await detectScam(trimmed);
      const d = res.data;

      const isScam = d.classification === "SCAM";
      const score = Math.round(d.confidence * 100);

      // Split the reason into distinct bullet points
      const reasons = d.reason
        .split("\n")
        .map((l: string) => l.trim())
        .filter((l: string) => l.length > 0);

      setResult({ isScam, score, reasons });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Unexpected error";
      setError(msg);
      console.error("Detection error:", err);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="p-6 md:p-8 max-w-3xl mx-auto space-y-8">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-2">
        <h1 className="text-3xl font-bold text-foreground">Scam Detector</h1>
        <p className="text-muted-foreground">Paste any SMS or email to check if it's a scam</p>
      </motion.div>

      {/* Input */}
      <div className="space-y-4">
        <textarea
          id="scam-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Paste SMS or email content here..."
          className="w-full h-40 p-4 rounded-xl bg-card border border-border text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-safe/50 font-mono text-sm"
        />
        <motion.button
          id="analyze-btn"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={analyze}
          disabled={!input.trim() || analyzing}
          className="w-full py-4 rounded-xl bg-safe/20 text-safe font-semibold border border-safe/30 hover:bg-safe/30 transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Search className="h-4 w-4" />
          {analyzing ? "Analyzing message..." : "Analyze"}
        </motion.button>
      </div>

      {/* Spinner */}
      {analyzing && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center gap-4 py-8"
        >
          <Loader2 className="h-8 w-8 text-safe animate-spin" />
          <p className="text-muted-foreground text-sm font-mono">Analyzing with Kavach AI...</p>
        </motion.div>
      )}

      {/* Error */}
      <AnimatePresence>
        {error && !analyzing && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="rounded-xl border border-danger/30 bg-danger/5 p-6 flex items-start gap-3"
          >
            <WifiOff className="h-5 w-5 text-danger mt-0.5 shrink-0" />
            <div>
              <h3 className="text-danger font-semibold">Connection Error</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Could not reach the backend. Make sure the server is running on port 8000.
              </p>
              <p className="text-xs text-muted-foreground mt-1 font-mono">{error}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Result */}
      <AnimatePresence>
        {result && !analyzing && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className={`rounded-xl border p-6 space-y-6 ${
              result.isScam
                ? "border-danger/30 bg-danger/5 glow-danger"
                : "border-safe/30 bg-safe/5 glow-safe"
            }`}
          >
            {/* Header row */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {result.isScam ? (
                  <AlertTriangle className="h-8 w-8 text-danger" />
                ) : (
                  <ShieldCheck className="h-8 w-8 text-safe" />
                )}
                <div>
                  <h3 className={`text-xl font-bold ${result.isScam ? "text-danger" : "text-safe"}`}>
                    {result.isScam ? "High Risk Scam" : "Looks Safe"}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {result.isScam
                      ? "This message contains multiple red flags"
                      : "No significant threats detected"}
                  </p>
                  <p className={`text-xs mt-1 ${result.isScam ? "text-danger" : "text-safe"}`}>
                    AI Confidence: {result.score}%
                  </p>
                </div>
              </div>
              <CircularProgress
                value={displayScore}
                size={80}
                strokeWidth={6}
                color={result.isScam ? "hsl(var(--danger))" : "hsl(var(--safe))"}
                label="Risk"
              />
            </div>

            {/* Safe message notice */}
            {!result.isScam && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-lg border border-safe/40 bg-safe/10 p-3"
              >
                <p className="text-safe font-semibold">Safe Message Pattern</p>
                <p className="text-xs text-muted-foreground mt-1">
                  No urgency, phishing link, or unknown-sender coercion detected.
                </p>
              </motion.div>
            )}

            {/* Findings */}
            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-foreground">AI Analysis:</h4>
              {result.reasons.map((r, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.06 }}
                  className="flex items-start gap-2 text-sm text-muted-foreground"
                >
                  <span className={`mt-0.5 ${result.isScam ? "text-danger" : "text-safe"}`}>•</span>
                  <span>{r}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ScamDetector;
