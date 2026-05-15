const API_URL = "http://localhost:8000/api/v1/chat/message";

export const sendMessageToBot = async (userMessage, { sessionId, studentId } = {}) => {
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: userMessage,
        session_id: sessionId || null,
        student_id: studentId || null,
      }),
    });

    if (!response.ok) {
      throw new Error(`Lỗi HTTP! Trạng thái: ${response.status}`);
    }

    const data = await response.json();

    console.log("Phản hồi từ Backend:", {
      intent: data.intent,
      confidence: data.confidence,
      slots: data.slots,
    });

    return data;
  } catch (error) {
    console.error("Lỗi khi kết nối đến backend FastAPI:", error);
    return {
      reply: "Hệ thống đang gặp sự cố kết nối. Vui lòng kiểm tra xem backend đã chạy chưa nhé!",
      message: "Hệ thống đang gặp sự cố kết nối. Vui lòng kiểm tra xem backend đã chạy chưa nhé!",
      intent: "ERROR",
      confidence: 0,
      slots: {},
      missing_slots: [],
      follow_up_question: null,
      data: null,
    };
  }
};
