import { Outlet, useNavigate } from "react-router-dom";
import { Navbar } from "../components/nav-bars/react/navbar";
import { NodeSidebar } from "../components/side-bars/react/node-sidebar";
import type { NodeCategory, NodeItem } from "../components/side-bars/react/node-sidebar";

const APP_PRODUCT_NAME = "Plan and Execution";

function ProjectInfoIcon({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true" className={className}>
      <path d="M16 2a14 14 0 1 0 14 14A14 14 0 0 0 16 2Zm0 26a12 12 0 1 1 12-12 12 12 0 0 1-12 12Z" />
      <path d="M15 14h2v9h-2zm1-5a1.5 1.5 0 1 0 1.5 1.5A1.5 1.5 0 0 0 16 9Z" />
    </svg>
  );
}

function TasksIcon({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true" className={className}>
      <path d="M14 21.414 9 16.413 10.413 15 14 18.586 21.585 11 23 12.415 14 21.414z" />
      <path d="M25 5H7a2 2 0 0 0-2 2v18a2 2 0 0 0 2 2h18a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2Zm0 20H7V7h18Z" />
    </svg>
  );
}

function ChatIcon({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true" className={className}>
      <path d="M17.74 30 16 29l4-7h6a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h9v2H6a4 4 0 0 1-4-4V8a4 4 0 0 1 4-4h20a4 4 0 0 1 4 4v12a4 4 0 0 1-4 4h-4.84Z" />
      <path d="M8 10h16v2H8zm0 6h10v2H8z" />
    </svg>
  );
}

function NotesIcon({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true" className={className}>
      <path d="M25.7 9.3l-7-7A1 1 0 0 0 18 2H8a2 2 0 0 0-2 2v24a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V10a1 1 0 0 0-.3-.7ZM18 4.4l5.6 5.6H18ZM24 28H8V4h8v6a2 2 0 0 0 2 2h6Z" />
      <path d="M10 22h12v2H10zm0-6h12v2H10z" />
    </svg>
  );
}

const NAV_ITEMS: NodeCategory[] = [
  {
    id: "navigation",
    label: "Navigation",
    items: [
      { id: "/", label: "Project info", icon: <ProjectInfoIcon /> },
      { id: "/tasks", label: "Tasks", icon: <TasksIcon /> },
      { id: "/chat", label: "Chat", icon: <ChatIcon /> },
      { id: "/notes", label: "Notes", icon: <NotesIcon /> },
    ],
  },
];

export function Layout() {
  const navigate = useNavigate();

  const handleNodeSelect = (node: NodeItem) => {
    navigate(node.id);
  };

  return (
    <div className="flex h-screen flex-col bg-bg text-light">
      <Navbar productName={APP_PRODUCT_NAME} />
      <div className="flex min-h-0 flex-1">
        <NodeSidebar
          categories={NAV_ITEMS}
          theme="gray-90"
          density="md"
          behavior="fixed"
          tabStyle="line"
          footerLabel="Plan and Execution"
          onNodeSelect={handleNodeSelect}
          className="h-full"
        />
        <main className="min-w-0 flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
