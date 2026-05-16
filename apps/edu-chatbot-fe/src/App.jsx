import { useEffect, useState } from "react";
import Header from "./components/Header";
import InputBox from "./components/InputBox";
import MessageList from "./components/MessageList";
import { sendMessageToBot } from "./services/api";

const BOT_WELCOME_TEXT = `Xin chào! Mình là EduAdvisor, trợ lý học vụ ảo của bạn đây. Mình có thể hỗ trợ bạn các vấn đề:
- Tư vấn thời gian (đăng ký/hủy môn)
- Tra cứu môn tiên quyết và môn bắt buộc
- Giải đáp thông tin về chương trình đào tạo
Vui lòng cung cấp mã số sinh viên hoặc khóa của bạn để chúng ta bắt đầu nhé.`;

const createWelcomeMessage = () => ({
  id: 1,
  sender: "bot",
  text: BOT_WELCOME_TEXT,
});

const getOrCreateSessionId = () => {
  const stored = localStorage.getItem("eduadvisor_session_id");
  if (stored) return stored;

  const next = `session-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  localStorage.setItem("eduadvisor_session_id", next);
  return next;
};

function App() {
  const [sessionId, setSessionId] = useState(() => getOrCreateSessionId());
  const [studentId, setStudentId] = useState(() => localStorage.getItem("eduadvisor_student_id") || "");
  const [messages, setMessages] = useState([createWelcomeMessage()]);

  useEffect(() => {
    localStorage.setItem("eduadvisor_session_id", sessionId);
  }, [sessionId]);

  useEffect(() => {
    if (studentId) {
      localStorage.setItem("eduadvisor_student_id", studentId);
    } else {
      localStorage.removeItem("eduadvisor_student_id");
    }
  }, [studentId]);

  const handleNewUserMessage = async (newText) => {
    // Prevent sending empty messages
    if (!newText?.trim()) return;

    const newUserMessage = {
      id: Date.now(),
      sender: "user",
      text: newText,
    };
    setMessages((prev) => [...prev, newUserMessage]);

    try {
      const response = await sendMessageToBot(newText, {
        sessionId,
        studentId,
      });

      const nextStudentId = response?.slots?.student_id || studentId;
      if (nextStudentId && nextStudentId !== studentId) {
        setStudentId(nextStudentId);
      }

      const botMsg = {
        id: Date.now() + 1,
        sender: "bot",
        text: response?.reply || response?.message || "Xin lỗi, mình không nhận được phản hồi rõ ràng từ hệ thống.",
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      console.error("Lỗi khi gửi tin nhắn:", error);
      const errorMsg = {
        id: Date.now() + 1,
        sender: "bot",
        text: "Đã xảy ra lỗi. Vui lòng thử lại.",
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  const handleClearChat = () => {
    const confirmClear = window.confirm(
      "Bạn có chắc muốn xóa lịch sử chat không? Hành động này sẽ tạo session mới.",
    );

    if (confirmClear) {
      const nextSessionId = `session-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
      localStorage.setItem("eduadvisor_session_id", nextSessionId);
      localStorage.removeItem("eduadvisor_student_id");
      setSessionId(nextSessionId);
      setStudentId("");
      setMessages([createWelcomeMessage()]);
    }
  };

  const headerSubtitle = "Chatbot hỗ trợ tư vấn môn học, môn tiên quyết, thời gian drop môn";

  return (
    <div
      style={{
        maxWidth: "2000px",
        margin: "20px auto",
        border: "none",
        borderRadius: "8px",
        padding: "20px",
        background: "linear-gradient(135deg, #E0EAFC 0%, #CFDEF3 100%)",
        height: "870px",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Header subtitle={headerSubtitle} />

      <MessageList messages={messages} />

      <InputBox
        onSendMessage={handleNewUserMessage}
        onClearChat={handleClearChat}
      />
    </div>
  );
}

export default App;
