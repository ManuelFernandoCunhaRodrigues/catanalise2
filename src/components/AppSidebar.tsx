import { LayoutDashboard, Upload, Search, History, Settings, Presentation } from "lucide-react";
import { NavLink } from "@/components/NavLink";
import { BRAND_ICON_URL, IS_PUBLIC_DEMO } from "@/lib/runtime-config";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  useSidebar,
} from "@/components/ui/sidebar";

const menuItems = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard },
  { title: "Upload de CAT", url: "/upload", icon: Upload },
  { title: "Analise", url: "/analise", icon: Search },
  { title: "Modo Demo", url: "/demo", icon: Presentation },
  { title: "Historico", url: "/historico", icon: History },
  { title: "Configuracoes", url: "/configuracoes", icon: Settings },
];

const visibleMenuItems = IS_PUBLIC_DEMO ? [{ title: "Modo Demo", url: "/", icon: Presentation }] : menuItems;

export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";

  return (
    <Sidebar collapsible="icon" className="border-r-0">
      <SidebarHeader className="p-4">
        <div className="flex flex-col items-center justify-center">
          <div className="flex items-center gap-2">
            <img src={BRAND_ICON_URL} alt="Deserdeck RH Icon" className="h-12 w-12 object-contain" />
            {!collapsed && <span className="text-lg font-bold text-sidebar-foreground">Deserdeck RH</span>}
          </div>
          {!collapsed && <p className="mt-0.5 text-[10px] text-sidebar-muted">Analise Inteligente</p>}
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="text-sidebar-muted text-xs uppercase tracking-wider">
            {!collapsed && "Menu"}
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {visibleMenuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.url}
                      end={item.url === "/"}
                      className="text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors"
                      activeClassName="bg-sidebar-accent text-sidebar-primary font-medium"
                    >
                      <item.icon className="mr-2 h-4 w-4" />
                      {!collapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
