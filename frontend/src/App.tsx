import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import AppLayout from "@/components/AppLayout";
import HomePage from "@/pages/HomePage";
import WarRoom from "@/pages/WarRoom";
import AnalysisPage from "@/pages/AnalysisPage";
import DefensePage from "@/pages/DefensePage";
import ScamDetector from "@/pages/ScamDetector";
import DashboardPage from "@/pages/DashboardPage";
import NotFound from "./pages/NotFound.tsx";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AppLayout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/war-room" element={<WarRoom />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/defense" element={<DefensePage />} />
            <Route path="/scam-detector" element={<ScamDetector />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </AppLayout>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
