import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, Link, Clock, Building, Info, ShieldAlert, Loader2 } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { useEffect, useState } from "react";
import { explainMessage, type ExplainResult } from "@/lib/api";

const IconMap: Record<string, React.ElementType> = {
  AlertTriangle,
  Link,
  Clock,
  Building,
  Info,
  ShieldAlert
};

const defaultText = "⚡ URGENT: Your electricity connection will be DISCONNECTED in 30 minutes due to unpaid bill of ₹2,847. Pay immediately: bit.ly/pay-electric-now";

const getColorClasses = (color: string) => {
  if (color === "danger") return { text: "text-danger", bg: "bg-danger/20", border: "border-danger", hoverBg: "hover:bg-danger/30", borderLight: "border-danger/30", bgLight: "bg-danger/5" };
  if (color === "warning") return { text: "text-warning", bg: "bg-warning/20", border: "border-warning", hoverBg: "hover:bg-warning/30", borderLight: "border-warning/30", bgLight: "bg-warning/5" };
  return { text: "text-cyber", bg: "bg-cyber/20", border: "border-cyber", hoverBg: "hover:bg-cyber/30", borderLight: "border-cyber/30", bgLight: "bg-cyber/5" };
};

const AnalysisPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const textToAnalyze = location.state?.text || defaultText;

  const [loading, setLoading] = useState(true);
  const [analysis, setAnalysis] = useState<ExplainResult | null>(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const res = await explainMessage(textToAnalyze);
        setAnalysis(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalysis();
  }, [textToAnalyze]);

  return (
    <div className="p-6 md:p-8 max-w-6xl mx-auto space-y-8">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-2">
        <h1 className="text-3xl font-bold text-foreground">🔍 Forensic Analysis</h1>
        <p className="text-muted-foreground">Breakdown of the scam message with threat indicators</p>
      </motion.div>

      {loading ? (
        <div className="flex flex-col items-center justify-center p-20 gap-4">
          <Loader2 className="h-10 w-10 text-cyber animate-spin" />
          <p className="text-cyber text-sm animate-pulse">Running advanced forensic heuristics...</p>
        </div>
      ) : !analysis ? (
        <div className="flex flex-col items-center justify-center p-20 gap-4">
          <ShieldAlert className="h-10 w-10 text-danger" />
          <p className="text-danger text-sm">Failed to run analysis. Please try again.</p>
          <button
            onClick={() => navigate("/war-room")}
            className="px-4 py-2 rounded-lg bg-secondary text-muted-foreground mt-4"
          >
            ← Back to War Room
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Message Analysis */}
          <div className="lg:col-span-2 space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-xl border border-border bg-card p-6 space-y-4"
            >
              <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-danger" />
                Message Content
              </h2>
              <div className="bg-secondary/30 rounded-lg p-4 font-mono text-sm leading-relaxed space-y-2 whitespace-pre-wrap">
                <p className="text-foreground">
                  {analysis.message_parts.map((part, i) => {
                    if (part.highlight_index === null || !analysis.highlights[part.highlight_index]) {
                      return <span key={i}>{part.text}</span>;
                    }
                    
                    const hl = analysis.highlights[part.highlight_index];
                    const cls = getColorClasses(hl.color);
                    
                    return (
                      <Tooltip key={i}>
                        <TooltipTrigger asChild>
                          <span 
                            className={`${cls.bg} ${cls.text} px-1 rounded border-b-2 ${cls.border} cursor-help transition-colors ${cls.hoverBg}`}
                          >
                            {part.text}
                          </span>
                        </TooltipTrigger>
                        <TooltipContent className="max-w-xs bg-card border-border p-3">
                          <p className="text-sm font-semibold mb-1 text-foreground">{hl.label}</p>
                          <p className="text-xs text-muted-foreground">{hl.tooltip}</p>
                        </TooltipContent>
                      </Tooltip>
                    );
                  })}
                </p>
              </div>
            </motion.div>

            {/* Threat Indicators */}
            <div className="space-y-3">
              {analysis.highlights.map((h, i) => {
                const Icon = IconMap[h.icon] || AlertTriangle;
                const cls = getColorClasses(h.color);
                
                return (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 + i * 0.15 }}
                    className={`rounded-lg border p-4 flex items-start gap-4 ${cls.borderLight} ${cls.bgLight}`}
                  >
                    <div className={`p-2 rounded-lg ${cls.bg}`}>
                      <Icon className={`h-5 w-5 ${cls.text}`} />
                    </div>
                    <div>
                      <p className="font-semibold text-foreground text-sm">{h.label}</p>
                      <p className="text-xs text-muted-foreground mt-1">{h.tooltip}</p>
                      <code className="text-xs font-mono mt-2 inline-block px-2 py-0.5 rounded bg-secondary/50 text-muted-foreground">
                        "{h.text}"
                      </code>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>

          {/* Side Panel */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="space-y-6"
          >
            <div className="rounded-xl border border-danger/30 bg-danger/5 p-6 space-y-4 glow-danger">
              <h3 className="text-lg font-bold text-danger flex items-center gap-2">
                <Info className="h-5 w-5" />
                Why This Is a Scam
              </h3>
              <ul className="space-y-3 text-sm text-muted-foreground">
                {analysis.reasons.map((r, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-danger mt-0.5">•</span>
                    {r}
                  </li>
                ))}
              </ul>
            </div>

            <button
              onClick={() => navigate("/defense")}
              className="w-full py-3 rounded-lg bg-safe/20 text-safe font-medium border border-safe/30 hover:bg-safe/30 transition-all duration-300"
            >
              View Safe Response →
            </button>

            <button
              onClick={() => navigate("/war-room")}
              className="w-full py-3 rounded-lg bg-secondary text-muted-foreground font-medium border border-border hover:bg-secondary/80 transition-all duration-300"
            >
              ← Back to War Room
            </button>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default AnalysisPage;
