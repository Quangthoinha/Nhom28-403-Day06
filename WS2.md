# Worksheet 2: AI System Cost Estimation (VinschoolOne "Smart Hub")

Dựa trên bản đặc tả **VinschoolOne "Smart Hub"** (tương tác với ~500 phụ huynh/trường), dưới đây là bảng bóc tách chi phí hệ thống (Cost Breakdown) từ góc độ AI Engineer, không chỉ dừng lại ở tiền API/Tokens.

---

## Phần 1: Ước lượng Traffic & Token (Context: MVP 1 trường - 500 phụ huynh)

### 1. Phễu người dùng và Requests
- **Số user tích cực/ngày:** ~ 380 phụ huynh (theo kịch bản Realistic - 75% adoption). Để an toàn khi tính cost, ta ước lượng tối đa nền tảng có **500 daily active users**.
- **Số AI requests/ngày:**
  1. *Smart Daily Brief (19h00):* 1 request x 500 học sinh = 500 requests.
  2. *Actionable Notifications:* Giả sử 1 thông báo/ngày = 500 requests.
  3. *Vin-Assistant (Chat):* Giả sử 50% user hỏi 2 câu/ngày = 500 requests.
  - **=> Tổng số:** ~1,500 LLM/NLP requests/ngày.
- **Peak traffic (Lưu lượng đỉnh điểm):** 
  - Khung 19h00 (Khi hệ thống chạy Job tóm tắt Smart Brief gửi đi hàng loạt). Chạy đồng loạt 500 requests trong vòng 5-10 phút.
  - **=> Tốc độ yêu cầu (RPS):** Khoảng 1 - 2 RPS (Dễ dàng xử lý).

### 2. Ước lượng Tokens (dùng Gemini 1.5/2.0 Flash hoặc GPT-4o-mini)
- **Vin-Assistant:** Câu hỏi ngắn lấy Intent (Input: 100 tokens, Output: 10 tokens) => ~110 tokens/req. 
  - 500 req x 110 = 55K tokens.
- **Smart Brief:** Đưa data điểm danh sơ bộ vào prompt (Input: 300 tokens, Output: 80 tokens) => ~380 tokens/req. 
  - 500 req x 380 = 190K tokens.
- **Actionable Notifications:** Đọc thông báo văn bản dài (Input: 600 tokens, Output: 100 tokens) => ~700 tokens/req.
  - 500 req x 700 = 350K tokens.
- **=> Tổng cộng (Daily):** ~600K Input tokens & ~100K Output tokens.
- **=> Cost Token/Tháng:** Rất rẻ. Khoảng 18 triệu Input + 3 triệu Output tokens. Tốn **< 2 USD/tháng** (~50.000 VNĐ).

---

## Phần 2: Liệt kê các lớp chi phí (Cost Layers) ở mức MVP

Để run AI ở production, Token cost là thứ rẻ nhất. Dưới đây là các lớp cost khác:

| Lớp Cost | Mục đích sử dụng trong Smart Hub | Ước lượng ($/tháng) |
| :--- | :--- | :--- |
| **Token API (LLM)** | Chi phí gọi model AI (Gemini/OpenAI) qua API cho Chat, Tóm tắt. | ~$2 - $5 |
| **Compute** | Server chạy backend (Node/Python) gọi API trường; Background Worker tạo Smart Brief lúc 19h. | ~$15 - $20 |
| **Storage & Database** | Lưu trữ Log chat và User correction (chọn intent sửa) để đánh giá system. | ~$10 - $15 |
| **Logging & Monitoring** | Sentry (báo văng app), LangSmith/Langfuse (để debug AI tracing xem API trả lời mất bao lâu, bị hallucinate không). | ~$0 - $20 (có Free tier) |
| **Human Review (Data)** | Nhân viên/Giáo viên gom nhóm các Error/Query fail (phụ huynh gõ tiếng lóng) mỗi tuần để sửa prompt/từ đồng nghĩa. | ~2 - 4 hours/tuần (Cost nhân sự) |
| **Maintenance** | API từ hệ thống điểm danh Vinschool bị đổi định dạng, Dev phải fix code. | ~2 - 5 hours/tháng (Cost Dev) |
| **Tổng ước tính Cost (Tech)**| **Dự kiến khoảng $30 - $60 / tháng** cho cơ sở hạ tầng (Khớp với KPI "chi phí rất thấp" được nêu trong Spec). | 

---

## Phần 3: Trả lời 3 câu hỏi cốt lõi của Worksheet

### 1. Cost driver lớn nhất của hệ thống là gì?
- Ở **quy mô MVP (500 users):** Cost driver lớn nhất của đội không đến từ tiền Cloud hay API. Nó đến từ **Human Cost (Review & Cập nhật dữ liệu lóng - Synonym Dictionary)** và chi phí Maintain để kết nối với cơ sở hạ tầng ERP Vinschool hiện tại không bị gãy.
- **Mức độ công nghệ:** Chi phí duy trì hạ tầng Backend Application (Server + Database để lưu log implicit feedback) lớn hơn hẳn chi phí của LLM inference ($20 vs $2). 

### 2. Hidden cost nào dễ bị quên nhất?
- **Chi phí Tracing và LLM Observability:** Lỗi của AI không giống phần mềm thường, khi AI nói chuyện "ảo giác" hoặc classify sai nhóm thông báo, bạn cần xem lại log của Context Input. Các hệ thống lưu trữ vector hay text log như Langfuse/LangSmith rất nhanh cạn Free Tier nếu lưu nguyên văn bản đầu vào do kích thước data lớn dần qua từng ngày.
- **Chi phí Retry và Queue (Lúc 19h00):** Khi làm Job Smart Brief, việc bắn gọi 500 API đến Google/OpenAI trong 1-2 phút rất dễ dính **Rate Limiting (429 Too Many Requests)**. Đội sẽ phải lập trình Queue worker và Exponential Retry (kéo dài cost chạy Cloud Functions/Workers).

### 3. Đội có chỗ nào đang ước lượng quá lạc quan không?
- **Quá lạc quan về khâu thu thập "Synonym list" và sửa đổi (Correction log):** Đặc tả ghi "dùng để cập nhật classifier hàng tuần", nhưng việc đánh giá (eval) hàng trăm truy vấn thất bại thủ công để viết quy tắc đồng nghĩa mới sẽ ngốn kha khá thời gian (Human-in-the-loop cost). Giáo viên hoặc IT School Admin sẽ phải bỏ giờ làm ra để chấm log thay vì AI tự auto.
- **Lạc quan về sự ổn định của Context Data:** Đội tự tin 100% "không dùng AI sinh tài chính", nhưng API xuất text của trường về các thông báo khoản phí có thể chứa văn bản phức tạp mà hệ thống trích xuất (Extraction Notification) dễ bắt lầm dấu phẩy hay số không. Chi phí rủi ro/đền bù niềm tin khi AI trích xuất sai 1 thông báo nộp tiền học phạt là rất lớn so với ước lượng.

---

## Phần 4: Nhìn xa (Scale 5x - 10x Users cho toàn bộ hệ thống lớp học / trường)

Khi quy mô mở rộng từ 500 lên **2,500 - 5,000 phụ huynh** (5x - 10x):
1. **Phần tăng phi tuyến tính và nguy hiểm nhất: Peak Compute & Queue Hạ tầng Backend.**
   - Khi có 5,000 học sinh, đúng **19h00 mỗi ngày**, hệ thống phải gửi đi 5,000 request tóm tắt. Nếu mỗi request mất 3 giây chạy AI, bạn không thể tóm tắt tuần tự (mất hơn 4-5 tiếng).
   - Hạ tầng buộc phải Scale Out bằng Concurrent Workers (chạy song song 50-100 instance ảo). Server load và chi phí duy trì hàng chờ (Message Queue như SQS/RabbitMQ hay Kafka) sẽ tăng rất mạnh vào các khung giờ vàng này.
2. **Chi phí Token:** Tăng tuyến tính (10x lên khoảng $20 - $50/tháng, dù tăng 10 lần nhưng giá tuyệt đối vẫn chấp nhận được và dễ thanh minh bằng tiền ROI bù lại).
3. **Chi phí Review Human In The Loop:** Tăng dần nhưng sẽ chững lại nhờ Data Flywheel đắp đủ dày. Cộng đồng phụ huynh ở 10 trường dùng từ ngữ và tiếng lóng phần lớn sẽ giống nhau, độ bao phủ (coverage) sẽ bão hoà dần.
