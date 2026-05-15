import React from "react";

const Message = ({ message }) => {
  const isUser = message.sender === "user";

  return (
    <div
      style={{
        marginBottom: "10px",
        textAlign: isUser ? "right" : "left",
      }}
    >
      <div
        style={{
          backgroundColor: isUser ? "#83a3d4b5" : "#87c1f0db",
          color: "black",
          padding: "10px 15px",
          borderRadius: "18px",
          display: "inline-block",
          maxWidth: "50%",
          wordWrap: "break-word",
          textAlign: "left",
          whiteSpace: "pre-wrap",
        }}>
        {message.text}
      </div>
    </div>
  );
};

export default Message;
