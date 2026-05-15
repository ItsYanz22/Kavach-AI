import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Shield, Swords, Search, Activity, ShieldCheck } from "lucide-react";
import GlowCard from "@/components/GlowCard";
import CircularProgress from "@/components/CircularProgress";

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="p-6 md:p-8 max-w-6xl mx-auto space-y-8">
      {/* Hero */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-3"
      >
        <div className="flex items-center justify-center gap-3">
          <Shield className="h-10 w-10 text-safe" />
          <h1 className="text-4xl md:text-5xl font-bold text-foreground">
            Kavach <span className="text-safe text-glow-safe">AI</span>
          </h1>
        </div>
        <p className="text-lg text-muted-foreground font-mono tracking-wider">
          Learn. Detect. Defend.
        </p>
        <p className="text-sm text-cyber">Experience scams safely before they happen in real life.</p>
      </motion.div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* War Room */}
        <GlowCard glowColor="danger" delay={0.1} onClick={() => navigate("/war-room")}>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-lg bg-danger/10">
                <Swords className="h-6 w-6 text-danger" />
              </div>
              <h2 className="text-xl font-semibold text-foreground">Enter War Room</h2>
            </div>
            <p className="text-muted-foreground text-sm">
              Experience realistic scam simulations and test your defenses against cyber threats.
            </p>
            <button className="w-full py-3 rounded-lg bg-danger/20 text-danger font-medium border border-danger/30 hover:bg-danger/30 hover-glow-button transition-all duration-300">
              Start Simulation
            </button>
          </div>
        </GlowCard>

        {/* Scam Detector */}
        <GlowCard glowColor="cyber" delay={0.2} onClick={() => navigate("/scam-detector")}>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-lg bg-cyber/10">
                <Search className="h-6 w-6 text-cyber" />
              </div>
              <h2 className="text-xl font-semibold text-foreground">Scan Message</h2>
            </div>
            <p className="text-muted-foreground text-sm">
              Paste any SMS or email to instantly check if it's a scam.
            </p>
            <button className="w-full py-3 rounded-lg bg-cyber/20 text-cyber font-medium border border-cyber/30 hover:bg-cyber/30 hover-glow-button transition-all duration-300">
              Check Scam
            </button>
          </div>
        </GlowCard>

        {/* Live Protection */}
        <GlowCard glowColor="safe" delay={0.3}>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-lg bg-safe/10">
                <ShieldCheck className="h-6 w-6 text-safe" />
              </div>
              <h2 className="text-xl font-semibold text-foreground">Live Protection Status</h2>
            </div>
            <div className="flex items-center gap-3">
              <motion.div
                animate={{ scale: [1, 1.3, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-4 h-4 rounded-full bg-safe"
                style={{ boxShadow: "0 0 12px hsl(var(--safe))" }}
              />
              <span className="text-safe font-semibold text-lg">Protected</span>
            </div>
            <p className="text-muted-foreground text-sm">
              All systems active. No threats detected in the last 24 hours.
            </p>
          </div>
        </GlowCard>

        {/* Security Score */}
        <GlowCard glowColor="warning" delay={0.4}>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-lg bg-warning/10">
                <Activity className="h-6 w-6 text-warning" />
              </div>
              <h2 className="text-xl font-semibold text-foreground">Security Score</h2>
            </div>
            <div className="flex justify-center py-2">
              <CircularProgress value={78} color="hsl(var(--warning))" label="Your Safety Level" />
            </div>
          </div>
        </GlowCard>
      </div>
    </div>
  );
};

export default HomePage;
