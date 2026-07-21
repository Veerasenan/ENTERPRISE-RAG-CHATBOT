import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";

export default function ChatPage() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-content">
        <ChatWindow />
      </div>
    </div>
  );
}
