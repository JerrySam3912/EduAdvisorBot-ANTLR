const Header = ({ subtitle }) => {
  return (
    <header
      style={{
        padding: "16px 20px",
        borderRadius: "14px",
        background: "rgba(255,255,255,0.75)",
        backdropFilter: "blur(10px)",
        boxShadow: "0 10px 30px rgba(15, 23, 42, 0.08)",
        marginBottom: "16px",
      }}
    >
      <h1 style={{ margin: 0, fontSize: "28px", color: "#1f2937", display: "flex", alignItems: "center", gap: "10px" }}>
        <span role="img" aria-label="book">📚</span>
        EduAdvisor Bot
      </h1>
      <p style={{ margin: "6px 0 0", color: "#4b5563" }}>
        {subtitle || "Trợ lý học vụ ảo cho tư vấn môn học, đăng ký và điều kiện học"}
      </p>
    </header>
  );
};

export default Header;
