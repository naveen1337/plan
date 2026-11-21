import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./pages/Layout";
import { Home } from "./pages/Home";
import { ChatScreen } from "./pages/chat/chat_screen";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<ChatScreen />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
