import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle, Shield, Phone, Ban, Send, Check, Loader2, AlertTriangle } from "lucide-react";
import { recommendAction, type ActionStep } from "@/lib/api";

const IconMap: Record<string, React.ElementType> = {
  Ban,
  Phone,
  Shield,
  CheckCircle,
  AlertTriangle
};

const defaultSteps = [
  { icon: "Ban", text: "Do not click unknown links", detail: "Never open URLs from unknown senders" },
  { icon: "Phone", text: "Verify with official source", detail: "Call the company directly using their official number" },
  { icon: "Shield", text: "Report to 1930 Cyber Helpline", detail: "India's national cyber crime helpline" },
  { icon: "Ban", text: "Block sender immediately", detail: "Prevent further contact from this number" },
];

const DefensePage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const textToAnalyze = location.state?.text || "";

  const [steps, setSteps] = useState<ActionStep[]>([]);
  const [loading, setLoading] = useState(true);
  const [checked, setChecked] = useState<boolean[]>([]);
  const [simulated, setSimulated] = useState(false);

  useEffect(() => {
    const fetchActions = async () => {
      try {
        if (!textToAnalyze) {
          setSteps(defaultSteps);
          setChecked(new Array(defaultSteps.length).fill(false));
          setLoading(false);
          return;
        }
        setLoading(true);
        const res = await recommendAction(textToAnalyze);
        const fetchedSteps = res.data.actions || defaultSteps;
        setSteps(fetchedSteps);
        setChecked(new Array(fetchedSteps.length).fill(false));
      } catch (err) {
        console.error(err);
        setSteps(defaultSteps);
        setChecked(new Array(defaultSteps.length).fill(false));
      } finally {
        setLoading(false);
      }
    };
    fetchActions();
  }, [textToAnalyze]);

  const allChecked = steps.length > 0 && checked.length === steps.length && checked.every(Boolean);

  const toggle = (i: number) => {
    setChecked((prev) => {
      const next = [...prev];
      next[i] = !next[i];
      return next;
    });
  };

  return (
    <div className="p-6 md:p-8 max-w-2xl mx-auto space-y-8">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-2">
        <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-foreground">🛡️ Safe Response</h1>
            <button
              onClick={() => navigate("/war-room")}
              className="text-muted-foreground hover:text-foreground text-sm transition-colors"
            >
              ← Back to War Room
            </button>
        </div>
        <p className="text-muted-foreground">Follow these steps to protect yourself from the scam</p>
      </motion.div>

      {loading ? (
        <div className="flex flex-col items-center justify-center p-20 gap-4">
          <Loader2 className="h-10 w-10 text-safe animate-spin" />
          <p className="text-safe text-sm animate-pulse">Generating personalized defense strategy...</p>
        </div>
      ) : (
        <div className="space-y-3">
          {steps.map((step, i) => {
            const Icon = IconMap[step.icon] || Shield;
            return (
              <motion.button
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                onClick={() => toggle(i)}
                className={`w-full flex items-center gap-4 p-4 rounded-xl border transition-all duration-300 text-left ${
                  checked[i]
                    ? "border-safe/30 bg-safe/5 glow-safe"
                    : "border-border bg-card hover:border-muted-foreground/30"
                }`}
              >
                <div className={`w-6 h-6 rounded-md border-2 flex items-center justify-center transition-all ${
                  checked[i] ? "border-safe bg-safe" : "border-muted-foreground/40"
                }`}>
                  {checked[i] && <Check className="h-4 w-4 text-safe-foreground" />}
                </div>
                <Icon className={`h-5 w-5 shrink-0 ${checked[i] ? "text-safe" : "text-muted-foreground"}`} />
                <div>
                  <p className={`font-medium text-sm ${checked[i] ? "text-safe" : "text-foreground"}`}>{step.text}</p>
                  <p className="text-xs text-muted-foreground">{step.detail}</p>
                </div>
              </motion.button>
            );
          })}
        </div>
      )}

      {!loading && (
        <motion.button
          whileHover={{ scale: allChecked ? 1.02 : 1 }}
          whileTap={{ scale: allChecked ? 0.98 : 1 }}
          onClick={() => allChecked && setSimulated(true)}
          disabled={!allChecked}
          className={`w-full py-4 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all duration-300 ${
            allChecked
              ? "bg-safe/20 text-safe border border-safe/30 hover:bg-safe/30 cursor-pointer"
              : "bg-secondary text-muted-foreground border border-border cursor-not-allowed"
          }`}
        >
          <Send className="h-4 w-4" />
          Simulate Safe Action
        </motion.button>
      )}

      <AnimatePresence>
        {simulated && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="rounded-xl border border-safe/30 bg-safe/5 p-8 text-center space-y-4 glow-safe"
          >
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.5, repeat: 2 }}
            >
              <CheckCircle className="h-16 w-16 text-safe mx-auto" />
            </motion.div>
            <h2 className="text-2xl font-bold text-safe text-glow-safe">✅ You Avoided the Scam!</h2>
            <p className="text-muted-foreground text-sm max-w-md mx-auto">
              Excellent work! By following these steps, you've protected yourself and your data. Stay vigilant!
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DefensePage;
