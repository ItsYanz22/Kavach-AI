import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Shield, AlertTriangle, Eye, CheckCircle, RefreshCw } from "lucide-react";
import CircularProgress from "@/components/CircularProgress";
import GlowCard from "@/components/GlowCard";
import { fetchHistory, type HistoryEntry } from "@/lib/api";

const CountUpNumber = ({ value, className }: { value: number; className?: string }) => {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    let frame = 0;
    const totalFrames = 25;
    const id = setInterval(() => {
      frame += 1;
      setDisplay(Math.round((frame / totalFrames) * value));
      if (frame >= totalFrames) clearInterval(id);
    }, 30);
    return () => clearInterval(id);
  }, [value]);
  return <p className={className}>{display}</p>;
};

const DashboardPage = () => {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [mentorScore, setMentorScore] = useState<number | null>(null);
  const [mentorAlerts, setMentorAlerts] = useState<any[]>([]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const res = await fetchHistory();
      setHistory(res.data.history);
      
      const backendUrl = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
      const hRes = await fetch(`${backendUrl}/health-score`);
      if (hRes.ok) {
        const hData = await hRes.json();
        const mData = hData.data || hData;
        if (mData.score !== undefined) setMentorScore(mData.score);
        if (mData.alerts) setMentorAlerts(mData.alerts);
      }
    } catch {
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const scamCount = history.filter((h) => h.classification === "SCAM").length;
  const safeCount = history.filter((h) => h.classification === "SAFE").length;
  const totalCount = history.length;
  const score = mentorScore !== null ? mentorScore : (totalCount > 0 ? Math.round((safeCount / totalCount) * 100) : 100);

  const fallbackAlerts = history.slice(0, 4).map((h) => ({
    time: new Date(h.timestamp).toLocaleString(),
    text: `${h.classification} – ${h.message.slice(0, 50)}…`,
    type: h.classification === "SCAM" ? ("danger" as const) : ("safe" as const),
  }));
  const alerts = mentorAlerts.length > 0 ? mentorAlerts : fallbackAlerts;

  return (
    <div className="p-6 md:p-8 max-w-6xl mx-auto space-y-8">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-2">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
            <p className="text-muted-foreground">Your security overview and activity log</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05, rotate: 90 }}
            whileTap={{ scale: 0.95 }}
            onClick={loadHistory}
            className="p-2 rounded-lg border border-border hover:bg-secondary transition-colors"
          >
            <RefreshCw className={`h-4 w-4 text-muted-foreground ${loading ? "animate-spin" : ""}`} />
          </motion.button>
        </div>
        <p className="text-xs text-cyber">Live data from Kavach AI backend</p>
      </motion.div>

      {/* Top Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GlowCard glowColor="safe" delay={0.1}>
          <div className="flex flex-col items-center gap-4">
            <h3 className="text-sm font-medium text-muted-foreground">Security Score</h3>
            <CircularProgress value={score} color="hsl(var(--safe))" />
          </div>
        </GlowCard>

        <GlowCard glowColor="cyber" delay={0.2}>
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-muted-foreground">Stats</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="text-center p-3 rounded-lg bg-secondary/30">
                <CountUpNumber value={totalCount} className="text-2xl font-bold text-foreground" />
                <p className="text-xs text-muted-foreground">Scans</p>
              </div>
              <div className="text-center p-3 rounded-lg bg-secondary/30">
                <CountUpNumber value={scamCount} className="text-2xl font-bold text-danger" />
                <p className="text-xs text-muted-foreground">Threats</p>
              </div>
              <div className="text-center p-3 rounded-lg bg-secondary/30">
                <CountUpNumber value={safeCount} className="text-2xl font-bold text-safe" />
                <p className="text-xs text-muted-foreground">Safe</p>
              </div>
              <div className="text-center p-3 rounded-lg bg-secondary/30">
                <CountUpNumber value={totalCount} className="text-2xl font-bold text-warning" />
                <p className="text-xs text-muted-foreground">Total</p>
              </div>
            </div>
          </div>
        </GlowCard>

        <GlowCard glowColor="warning" delay={0.3}>
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-muted-foreground">Recent Alerts</h3>
            <div className="space-y-2">
              {alerts.length === 0 && (
                <p className="text-xs text-muted-foreground">No detections yet. Try the Scam Detector!</p>
              )}
              {alerts.map((a, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 + i * 0.1 }}
                  className="flex items-start gap-2 text-xs"
                >
                  <div
                    className={`mt-1 w-2 h-2 rounded-full shrink-0 ${
                      a.type === "danger" ? "bg-danger" : "bg-safe"
                    }`}
                  />
                  <div>
                    <p className="text-foreground">{a.text}</p>
                    <p className="text-muted-foreground">{a.time}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </GlowCard>
      </div>

      {/* Detection History Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="rounded-xl border border-border bg-card overflow-hidden"
      >
        <div className="p-4 border-b border-border">
          <h3 className="font-semibold text-foreground flex items-center gap-2">
            <Eye className="h-4 w-4 text-muted-foreground" />
            Scam Detection History
          </h3>
        </div>
        <div className="divide-y divide-border">
          {history.length === 0 && (
            <div className="p-8 text-center text-muted-foreground text-sm">
              {loading ? "Loading..." : "No detections recorded yet. Use the Scam Detector to get started."}
            </div>
          )}
          {history.map((h, i) => (
            <motion.div
              key={h.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 + i * 0.05 }}
              whileHover={{ scale: 1.01, x: 4 }}
              className={`p-4 flex items-center justify-between transition-all duration-200 ${
                h.classification === "SCAM"
                  ? "hover:bg-danger/10 hover:shadow-[0_0_20px_hsla(0,84%,60%,0.18)]"
                  : "hover:bg-safe/10 hover:shadow-[0_0_20px_hsla(142,71%,45%,0.18)]"
              }`}
            >
              <div className="flex items-center gap-3">
                {h.classification === "SCAM" ? (
                  <AlertTriangle className="h-4 w-4 text-danger" />
                ) : (
                  <CheckCircle className="h-4 w-4 text-safe" />
                )}
                <span className="text-sm text-foreground font-mono truncate max-w-xs">
                  {h.message}
                </span>
              </div>
              <div className="flex items-center gap-4">
                <span
                  className={`text-xs font-medium px-2 py-1 rounded-full ${
                    h.classification === "SCAM"
                      ? "bg-danger/20 text-danger"
                      : "bg-safe/20 text-safe"
                  }`}
                >
                  {h.classification}
                </span>
                <span className="text-xs text-muted-foreground w-12 text-right">
                  {Math.round(h.confidence > 1 ? h.confidence : h.confidence * 100)}%
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default DashboardPage;
