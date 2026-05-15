# Chatbot Scripts — EduAdvisorBot

Danh sách toàn bộ câu hỏi/dòng lệnh mà người dùng có thể nhắn cho chatbot. Mỗi intent có nhiều biến thể để chatbot hiểu được ngữ cảnh tự nhiên.

---

## 1. CHÀO HỎI (GREETING)

| # | Câu hỏi |
|---|---------|
| 1 | xin chào |
| 2 | chào bạn |
| 3 | chào bạn mình |
| 4 | chào |
| 5 | buổi sáng tốt lành |
| 6 | buổi chiều tốt lành |
| 7 | hello |
| 8 | hey |
| 9 | good morning |
| 10 | good afternoon |

---

## 2. TRỢ GIÚP (HELP)

| # | Câu hỏi |
|---|---------|
| 1 | help |
| 2 | gợi ý |
| 3 | trợ giúp |
| 4 | hướng dẫn |
| 5 | bạn là ai |
| 6 | bạn có thể làm gì |
| 7 | what can you do |
| 8 | who are you |
| 9 | how can you help |

---

## 3. HỎI ĐIỀU KIỆN HỌC MÔN (ASK_COURSE_ELIGIBILITY)

Bot kiểm tra xem sinh viên đủ điều kiện học môn đó không, dựa trên tiên quyết và môn học trước.

### Tiếng Việt — hỏi điều kiện

| # | Câu hỏi |
|---|---------|
| 1 | học IT017IU được không |
| 2 | học CS101 được không |
| 3 | học được môn IT017IU không |
| 4 | học được không IT017IU |
| 5 | được học IT017IU không |
| 6 | có được học IT017IU không |
| 7 | có thể học IT017IU không |
| 8 | muốn học IT017IU |
| 9 | muốn học môn OOP |
| 10 | tìm hiểu môn AI |
| 11 | học về AI |
| 12 | learn about AI |
| 13 | tell me about OOP |
| 14 | học oop được không |
| 15 | học môn OOP |
| 16 | mình học ngành CS khóa 22, học IT017IU được không |

### Tiếng Việt — hỏi theo tên môn (alias)

| # | Câu hỏi |
|---|---------|
| 1 | học machine learning được không |
| 2 | học học máy được không |
| 3 | học trí tuệ nhân tạo được không |
| 4 | học AI được không |
| 5 | học OOP được không |
| 6 | học lập trình hướng đối tượng được không |
| 7 | học lập trình java được không |
| 8 | học cấu trúc dữ liệu được không |
| 9 | học giải thuật được không |
| 10 | học thuật toán được không |
| 11 | học operating system được không |
| 12 | học hệ điều hành được không |
| 13 | học os được không |
| 14 | học web dev được không |
| 15 | học mạng máy tính được không |
| 16 | học database được không |
| 17 | học khai phá dữ liệu được không |
| 18 | học data mining được không |
| 19 | học deep learning được không |
| 20 | học blockchain được không |
| 21 | học iot được không |
| 22 | học mobile app được không |

### Tiếng Anh

| # | Câu hỏi |
|---|---------|
| 1 | eligibility IT017IU |
| 2 | eligible for CS101 |
| 3 | can take IT017IU |
| 4 | can i take CS101 |
| 5 | take this course |
| 6 | take it |

---

## 4. HỎI TIÊN QUYẾT (ASK_PREREQUISITE_ONLY)

Bot trả lời: phải PASS những môn nào mới được học môn này.

### Tiếng Việt — hỏi bằng mã môn

| # | Câu hỏi |
|---|---------|
| 1 | tiên quyết của IT017IU là gì |
| 2 | tiên quyết IT017IU |
| 3 | môn tiên quyết của IT017IU là gì |
| 4 | điều kiện tiên quyết IT017IU |
| 5 | phải học gì trước IT017IU |
| 6 | cần học trước IT017IU |
| 7 | cần pass gì trước IT017IU |
| 8 | phải pass IT017IU |
| 9 | bắt buộc IT017IU |

### Tiếng Việt — hỏi bằng tên môn

| # | Câu hỏi |
|---|---------|
| 1 | tiên quyết của OOP là gì |
| 2 | tiên quyết của machine learning |
| 3 | phải học gì trước AI |
| 4 | cần pass gì trước học máy |
| 5 | môn tiên quyết của trí tuệ nhân tạo |
| 6 | prerequisite của lập trình hướng đối tượng |
| 7 | phải học gì trước operating system |
| 8 | phải học gì trước cấu trúc dữ liệu |
| 9 | prerequisite của algorithms |
| 10 | cần pass gì trước software engineering |

### Tiếng Anh

| # | Câu hỏi |
|---|---------|
| 1 | prerequisite IT017IU |
| 2 | prerequisites of CS101 |
| 3 | must pass IT017IU |
| 4 | need to pass CS101 |
| 5 | cần pass trước OOP |
| 6 | phải pass machine learning |
| 7 | prerequisite for AI |
| 8 | what are the prerequisites for CS101 |

---

## 5. HỎI MÔN HỌC TRƯỚC (ASK_PREVIOUS_ONLY)

Bot trả lời: chỉ cần đã học qua (rớt vẫn được) những môn nào.

### Tiếng Việt

| # | Câu hỏi |
|---|---------|
| 1 | học trước IT017IU là môn gì |
| 2 | môn học trước IT017IU |
| 3 | cần học gì trước IT017IU |
| 4 | học trước môn IT017IU |
| 5 | đã học gì trước IT017IU |
| 6 | nối tiếp trước IT017IU |
| 7 | học trước môn OOP |
| 8 | môn học trước của AI |
| 9 | cần học gì trước machine learning |
| 10 | học trước operating system |
| 11 | previous của CS101 |
| 12 | previous IT017IU |
| 13 | prev IT017IU |
| 14 | đã học môn gì trước đó để học được OOP |

### Tiếng Anh

| # | Câu hỏi |
|---|---------|
| 1 | previous IT017IU |
| 2 | prev IT017IU |
| 3 | prerequisite for IT017IU |
| 4 | what courses should I take before IT017IU |

---

## 6. HỎI THÔNG TIN MÔN HỌC (ASK_COURSE_REQUIREMENTS)

Bot trả lời: môn này là gì, có tiên quyết gì, previous gì, co-requisite gì.

### Tiếng Việt

| # | Câu hỏi |
|---|---------|
| 1 | IT017IU là môn gì |
| 2 | thông tin IT017IU |
| 3 | giới thiệu môn IT017IU |
| 4 | cho mình biết thông tin IT017IU |
| 5 | IT017IU là gì |
| 6 | môn IT017IU là gì |
| 7 | tra IT017IU |
| 8 | tìm hiểu môn IT017IU |
| 9 | tư vấn môn IT017IU |
| 10 | OOP là môn gì |
| 11 | thông tin về machine learning |
| 12 | AI là gì |
| 13 | giới thiệu operating system |
| 14 | cho mình biết về cấu trúc dữ liệu |
| 15 | môn software engineering là gì |
| 16 | tìm hiểu môn deep learning |

### Tiếng Anh

| # | Câu hỏi |
|---|---------|
| 1 | what is IT017IU |
| 2 | what are CS101 |
| 3 | which is IT017IU |
| 4 | info IT017IU |
| 5 | information about IT017IU |
| 6 | what is OOP |
| 7 | what's about machine learning |

---

## 7. HỎI THỜI GIAN ĐĂNG KÝ (ASK_REGISTRATION_TIME)

### Tiếng Việt

| # | Câu hỏi |
|---|---------|
| 1 | khi nào đăng ký |
| 2 | thời gian đăng ký |
| 3 | đăng ký môn khi nào |
| 4 | mấy ngày đăng ký |
| 5 | khi nào mở đăng ký |
| 6 | lịch đăng ký |
| 7 | đăng ký học phần khi nào |
| 8 | thời điểm đăng ký |
| 9 | đăng ký môn FA25 |
| 10 | đăng ký mùa hè 2026 |
| 11 | registration |
| 12 | register |
| 13 | enrollment |

### Tiếng Anh

| # | Câu hỏi |
|---|---------|
| 1 | registration time |
| 2 | when can I register |
| 3 | when is registration |
| 4 | enrollment |

---

## 8. HỎI THỜI GIAN DROP MÔN (ASK_DROP_TIME)

### Tiếng Việt

| # | Câu hỏi |
|---|---------|
| 1 | khi nào drop được |
| 2 | khi nào hủy môn |
| 3 | thời gian drop môn |
| 4 | hiệu chỉnh môn khi nào |
| 5 | thời điểm drop |
| 6 | bao giờ drop được |
| 7 | drop IT017IU khi nào |
| 8 | hủy môn IT017IU |
| 9 | rút môn khi nào |
| 10 | thời gian hiệu chỉnh đăng ký |
| 11 | drop FA25 |
| 12 | drop mùa hè 2026 |
| 13 | drop IT017IU SP26 |

### Tiếng Anh

| # | Câu hỏi |
|---|---------|
| 1 | when can I drop |
| 2 | drop time |
| 3 | withdraw course |
| 4 | cancel course |
| 5 | drop IT017IU |
| 6 | withdraw IT017IU |
| 7 | cancel IT017IU |

---

## 9. HỎI NỀN TẢNG ĐĂNG KÝ (ASK_REGISTRATION_PLATFORM)

### Tiếng Việt

| # | Câu hỏi |
|---|---------|
| 1 | đăng ký ở đâu |
| 2 | đăng ký ở website nào |
| 3 | nền tảng đăng ký |
| 4 | cổng đăng ký |
| 5 | đăng ký trên web gì |
| 6 | register platform |
| 7 | đăng ký ở cổng nào |
| 8 | đăng ký chỗ nào |

---

## 10. CUNG CẤP THÔNG TIN CÁ NHÂN (ONBOARDING)

Bot cần biết ngành + khóa (hoặc MSSV) trước khi trả lời.

### Cung cấp MSSV đầy đủ (tự suy ra ngành + khóa)

| # | Câu nhập |
|---|---------|
| 1 | ITCSIU22001 |
| 2 | ITCEIU24001 |
| 3 | ITDSIU23109 |
| 4 | ITNEIU22101 |
| 5 | mssv ITCSIU22001 |
| 6 | mình là ITCSIU22001 |
| 7 | cho mình biết ngành CS khóa 22 |

### Cung cấp ngành + khóa riêng

| # | Câu nhập |
|---|---------|
| 1 | mình học ngành CS khóa 22 |
| 2 | mình học CS K22 |
| 3 | ngành NE khóa 21 |
| 4 | mình là ngành DS k23 |
| 5 | học ngành CE k24 |
| 6 | CS K23 |
| 7 | NE K21 |
| 8 | DS K22 |
| 9 | IT-CE K24 |
| 10 | computer science K22 |
| 11 | network engineering K21 |
| 12 | data science K23 |
| 13 | ngành cs khóa 23 |
| 14 | ngành ne khóa 22 |
| 15 | ngành ds khóa 24 |

---

## 11. NGỮ CẢNH HÓA (SESSION MEMORY)

Bot nhớ môn đã hỏi trước đó, user có thể hỏi tiếp không cần nhắc lại mã.

| # | Câu hỏi |
|---|---------|
| 1 | môn này có học được không |
| 2 | môn đó tiên quyết là gì |
| 3 | hủy môn này được không |
| 4 | học được không |
| 5 | tiên quyết là gì |
| 6 | môn này là gì |
| 7 | nó là môn gì |
| 8 | drop môn đó |

---

## 12. NGÔN NGỮ KHÁC (LANGUAGE DRIFT)

Bot không hỗ trợ, sẽ yêu cầu hỏi lại bằng tiếng Việt.

| # | Câu hỏi | Ghi chú |
|---|---------|---------|
| 1 | what is the prerequisite | Tiếng Anh thuần — bị chặn |
| 2 | when can I register | Tiếng Anh thuần — bị chặn |
| 3 | drop course | Tiếng Anh thuần — bị chặn |

---

## 13. KHÔNG HỖ TRỢ (UNKNOWN)

Những câu ngoài phạm vi sẽ nhận reply mặc định.

---

## TÓM TẮT THEO INTENT

| Intent | Mô tả | Ví dụ tiêu biểu |
|--------|-------|----------------|
| `GREETING` | Lời chào | "xin chào", "hello" |
| `HELP` | Yêu cầu trợ giúp | "help", "bạn là ai" |
| `ASK_COURSE_ELIGIBILITY` | Hỏi đủ điều kiện học môn | "học IT017IU được không" |
| `ASK_PREREQUISITE_ONLY` | Hỏi tiên quyết (phải PASS) | "tiên quyết IT017IU" |
| `ASK_PREVIOUS_ONLY` | Hỏi môn học trước (chỉ cần đã học) | "học trước IT017IU" |
| `ASK_COURSE_REQUIREMENTS` | Hỏi thông tin chung | "IT017IU là môn gì" |
| `ASK_REGISTRATION_TIME` | Hỏi thời gian đăng ký | "khi nào đăng ký" |
| `ASK_DROP_TIME` | Hỏi thời gian drop môn | "khi nào drop được" |
| `ASK_REGISTRATION_PLATFORM` | Hỏi nền tảng đăng ký | "đăng ký ở đâu" |
| `ONBOARDING` | Yêu cầu cung cấp danh tính | "mình học CS K22" |
| `IDENTITY_ACKNOWLEDGED` | Xác nhận thông tin cá nhân | "ITCSIU22001" |
| `LANGUAGE_DRIFT` | Ngôn ngữ không hỗ trợ | Tiếng Anh/Trung thuần |
