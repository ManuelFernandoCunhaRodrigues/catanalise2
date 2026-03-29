import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";

export function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full">
        <AppSidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <header className="flex h-14 shrink-0 items-center border-b bg-card px-4">
            <SidebarTrigger className="mr-4" />
            <span className="text-sm font-medium text-muted-foreground">
              Deserdeck RH | Analise de Certidoes de Acervo Tecnico
            </span>
          </header>
          <main className="flex-1 overflow-auto bg-background p-4 md:p-6">{children}</main>
        </div>
      </div>
    </SidebarProvider>
  );
}
