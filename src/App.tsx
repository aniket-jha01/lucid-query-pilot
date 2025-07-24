
import { useState, useCallback } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import SchemaUpload from "./pages/SchemaUpload";
import Dashboard from "./pages/Dashboard";
import NotFound from "./pages/NotFound";
import { fetchActiveSchema } from "@/api/query";

const queryClient = new QueryClient();

const App = () => {
  // State to trigger schema status refresh
  const [schemaRefreshKey, setSchemaRefreshKey] = useState(0);

  // Callback to refresh schema status
  const refreshSchemaStatus = useCallback(() => {
    setSchemaRefreshKey((k) => k + 1);
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/schema-upload" element={<SchemaUpload onSchemaUploaded={refreshSchemaStatus} />} />
            <Route path="/dashboard" element={<Dashboard key={schemaRefreshKey} />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
