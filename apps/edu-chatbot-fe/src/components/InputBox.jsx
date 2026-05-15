import React, { useState } from "react";

const InputBox = ({ onSendMessage, onClearChat }) => {
  const [input, setInput] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (input.trim() === "") return;

    await onSendMessage(input);
    setInput("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        gap: "10px",
        padding: "20px",
        background: "rgba(255,255,255,0.65)",
        borderRadius: "14px",
        boxShadow: "0 10px 30px rgba(15, 23, 42, 0.08)",
      }}
    >
      <input
        type="text"
        value={input}
        placeholder="Nhập câu hỏi của bạn..."
        style={{
          width: "80%",
          padding: "12px 14px",
          borderRadius: "10px",
          border: "1px solid #cbd5e1",
          outline: "none",
          fontSize: "15px",
        }}
        onChange={(e) => {
          setInput(e.target.value);
        }}
      />

      <button
        type="submit"
        style={{
          width: "90px",
          background: "#4f46e5",
          color: "#fff",
          border: "none",
          padding: "12px",
          marginLeft: "5px",
          borderRadius: "10px",
          textAlign: "center",
          cursor: "pointer",
        }}
      >
        Gửi
      </button>

      <button
        type="button"
        onClick={onClearChat}
        style={{
          width: "90px",
          background: "#64748b",
          color: "#fff",
          border: "none",
          padding: "12px",
          marginLeft: "5px",
          borderRadius: "10px",
          textAlign: "center",
          cursor: "pointer",
        }}
      >
        Reset
      </button>
    </form>
  );
};

export default InputBox;
