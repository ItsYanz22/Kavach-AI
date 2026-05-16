import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCcw, Home } from "lucide-react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 text-center">
          <div className="max-w-md w-full space-y-6 p-8 rounded-2xl border border-danger/30 bg-card/50 backdrop-blur-xl shadow-2xl glow-danger">
            <div className="mx-auto w-16 h-16 rounded-full bg-danger/10 flex items-center justify-center mb-4">
              <AlertTriangle className="h-8 w-8 text-danger" />
            </div>
            
            <div className="space-y-2">
              <h1 className="text-2xl font-bold text-foreground">Critical Error</h1>
              <p className="text-muted-foreground text-sm">
                The Kavach AI interface encountered a runtime failure.
              </p>
              <div className="mt-4 p-3 rounded-lg bg-black/40 border border-border text-left overflow-auto max-h-32">
                <code className="text-xs text-danger font-mono">
                  {this.state.error?.message || "Unknown runtime error"}
                </code>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-4">
              <button
                onClick={() => window.location.reload()}
                className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-danger/20 text-danger border border-danger/30 hover:bg-danger/30 transition-all font-semibold text-sm"
              >
                <RefreshCcw className="h-4 w-4" />
                Reload App
              </button>
              <button
                onClick={() => window.location.href = "/"}
                className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-secondary text-foreground border border-border hover:bg-secondary/80 transition-all font-semibold text-sm"
              >
                <Home className="h-4 w-4" />
                Go Home
              </button>
            </div>
            
            <p className="text-[10px] text-muted-foreground pt-4">
              Session ID: {crypto.randomUUID?.() || Date.now()}
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
