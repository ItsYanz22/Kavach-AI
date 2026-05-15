import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Check, CheckCheck } from "lucide-react";

interface ChatBubbleProps {
  message: string;
  sender: "received" | "sent";
  time?: string;
  senderName?: string;
  delay?: number;
  status?: "sent" | "delivered" | "read";
}

const ChatBubble = ({ message, sender, time, senderName, delay = 0, status = "delivered" }: ChatBubbleProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.35, delay, type: "spring", damping: 20 }}
      className={cn("flex", sender === "sent" ? "justify-end" : "justify-start")}
    >
      <div className={cn("relative max-w-[75%]", sender === "sent" ? "items-end" : "items-start")}>
        {/* Bubble tail */}
        <div
          className={cn(
            "absolute top-0 w-3 h-3",
            sender === "received"
              ? "left-[-6px] wa-tail-left"
              : "right-[-6px] wa-tail-right"
          )}
        />
        <div
          className={cn(
            "relative rounded-lg px-3 py-1.5 shadow-md",
            sender === "received"
              ? "wa-bubble-received rounded-tl-none"
              : "wa-bubble-sent rounded-tr-none"
          )}
        >
          {senderName && (
            <p className="text-xs font-medium text-cyber mb-0.5">{senderName}</p>
          )}
          <p className="text-[13.5px] leading-[19px] text-foreground whitespace-pre-wrap">{message}</p>
          <div className="flex items-center justify-end gap-1 mt-0.5 -mb-0.5">
            {time && (
              <span className="text-[11px] text-muted-foreground/70">{time}</span>
            )}
            {sender === "sent" && (
              <CheckCheck className={cn(
                "h-[14px] w-[14px]",
                status === "read" ? "text-cyber" : "text-muted-foreground/50"
              )} />
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatBubble;
