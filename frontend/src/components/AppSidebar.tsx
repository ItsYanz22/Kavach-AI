import { Home, Swords, Search, LayoutDashboard, Shield, BookOpen, LogOut, LogIn } from "lucide-react";
import { NavLink } from "@/components/NavLink";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/auth/AuthContext";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";

export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  const location = useLocation();
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const items = [
    { title: "Home", url: "/", icon: Home },
    { title: "War Room", url: "/war-room", icon: Swords },
    { title: "Scam Detector", url: "/scam-detector", icon: Search },
    { title: "Learning", url: "/learning", icon: BookOpen },
    { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  ];

  return (
    <Sidebar collapsible="icon" className="border-r border-border">
      <SidebarContent className="pt-4">
        <div className={`flex items-center gap-2 px-4 mb-8 ${collapsed ? "justify-center" : ""}`}>
          <Shield className="h-7 w-7 text-safe shrink-0" />
          {!collapsed && (
            <span className="text-lg font-bold text-foreground tracking-tight">
              Kavach <span className="text-safe">AI</span>
            </span>
          )}
        </div>

        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.url}
                      end={item.url === "/"}
                      className="hover:bg-muted/50 transition-colors"
                      activeClassName="bg-safe/10 text-safe border-r-2 border-safe"
                    >
                      <item.icon className="mr-3 h-4 w-4 shrink-0" />
                      {!collapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <div className="mt-auto pb-4 px-2">
          {isAuthenticated ? (
            <SidebarMenuButton 
              onClick={() => {
                logout();
                navigate("/");
              }}
              className="text-muted-foreground hover:text-danger transition-colors w-full"
            >
              <LogOut className="mr-3 h-4 w-4 shrink-0" />
              {!collapsed && <span>Logout</span>}
            </SidebarMenuButton>
          ) : (
            <SidebarMenuButton 
              onClick={() => navigate("/login")}
              className="text-muted-foreground hover:text-safe transition-colors w-full"
            >
              <LogIn className="mr-3 h-4 w-4 shrink-0" />
              {!collapsed && <span>Login / Sign up</span>}
            </SidebarMenuButton>
          )}
        </div>
      </SidebarContent>
    </Sidebar>
  );
}
