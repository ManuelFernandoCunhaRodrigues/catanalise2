import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";

export function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <AppSidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <header className="h-14 flex items-center border-b bg-card px-4 shrink-0">
            <SidebarTrigger className="mr-4" />
            <span className="text-sm font-medium text-muted-foreground">
              Deserdeck RH — Análise de Certidões de Acervo Técnico
            </span>
          </header>
          <main className="flex-1 p-4 md:p-6 overflow-auto bg-background">{children}</main>
        </div>
      </div>
    </SidebarProvider>
  );
}
