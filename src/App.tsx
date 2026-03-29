import { Suspense, lazy } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, HashRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppLayout } from "@/components/AppLayout";
import { IS_PUBLIC_DEMO, USE_HASH_ROUTER } from "@/lib/runtime-config";

const Dashboard = lazy(() => import("./pages/Dashboard"));
const UploadCAT = lazy(() => import("./pages/UploadCAT"));
const Analise = lazy(() => import("./pages/Analise"));
const Historico = lazy(() => import("./pages/Historico"));
const Configuracoes = lazy(() => import("./pages/Configuracoes"));
const Demo = lazy(() => import("./pages/Demo"));
const NotFound = lazy(() => import("./pages/NotFound"));

const queryClient = new QueryClient();
const Router = USE_HASH_ROUTER ? HashRouter : BrowserRouter;

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <Router>
        <AppLayout>
          <Suspense fallback={<RouteFallback />}>
            <Routes>
              <Route path="/" element={IS_PUBLIC_DEMO ? <Demo /> : <Dashboard />} />
              <Route path="/upload" element={<UploadCAT />} />
              <Route path="/analise" element={<Analise />} />
              <Route path="/demo" element={<Demo />} />
              <Route path="/historico" element={<Historico />} />
              <Route path="/configuracoes" element={<Configuracoes />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </AppLayout>
      </Router>
    </TooltipProvider>
  </QueryClientProvider>
);

function RouteFallback() {
  return (
    <div className="flex min-h-[40vh] items-center justify-center rounded-lg border border-dashed text-sm text-muted-foreground">
      Carregando tela...
    </div>
  );
}

export default App;
