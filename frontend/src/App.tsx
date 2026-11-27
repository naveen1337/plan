import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./pages/Layout";
import { HomeScreen } from "./pages/home/home_screen";
import { ChatScreen } from "./pages/chat/chat_screen";
import { TasksScreen } from "./pages/tasks/tasks_screen";
import { NotesScreen } from "./pages/notes/notes_screen";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomeScreen />} />
          <Route path="/tasks" element={<TasksScreen />} />
          <Route path="/chat" element={<ChatScreen />} />
          <Route path="/notes" element={<NotesScreen />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
