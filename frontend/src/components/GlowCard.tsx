import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface GlowCardProps {
  children: React.ReactNode;
  className?: string;
  glowColor?: "danger" | "safe" | "warning" | "cyber";
  onClick?: () => void;
  delay?: number;
}

const GlowCard = ({ children, className, glowColor, onClick, delay = 0 }: GlowCardProps) => {
  const glowClass = glowColor ? `glow-${glowColor}` : "";
  const hoverGlowClass = glowColor === "danger" ? "glow-danger-hover" : glowColor === "safe" ? "glow-safe-hover" : "";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
      onClick={onClick}
      className={cn(
        "rounded-xl border border-border bg-card p-6 transition-all duration-300 cursor-pointer",
        glowClass,
        hoverGlowClass,
        className
      )}
    >
      {children}
    </motion.div>
  );
};

export default GlowCard;
