# AI Product Canvas — Vinschool One "Smart Hub"

**Hackathon Draft · Track: VinUni-VinSchool · April 2026**

---

## Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được? | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào? | Cost bao nhiêu/request? Latency bao lâu? Risk chính là gì? |
| **Trả lời** | Phụ huynh VinSchool bận rộn mất nhiều phút điều hướng qua nhiều tab để tìm thông tin (bài tập, học phí, thực đơn…) hoặc bỏ sót thông báo dài toàn chữ → AI "đưa data tìm phụ huynh" qua giao diện hội thoại Chat/Voice và thẻ tóm tắt trực quan, đạt Time-to-Information < 10 giây thay vì phải click 4+ lần | AI lấy nhầm dữ liệu (hỏi Toán trả về bài Khoa học, lộn data hai con) → user phát hiện ngay vì mọi câu trả lời đính kèm deep-link về màn hình gốc (Grounding); user xác minh 1 click; AI tuyệt đối không tự sinh số liệu tài chính/điểm số — chỉ hiển thị Hard-coded UI | Chi phí rất thấp — chủ yếu NLP phân loại intent + call internal API; LLM chỉ dùng để tóm tắt text ngắn (Smart Brief, Actionable Notifications); latency < 1s cho truy vấn tra cứu; risk chính: hallucination số liệu tài chính → khắc phục bằng cách cấm AI generate tài chính |

---

## Automation hay augmentation?

☐ Automation — AI làm thay, user không can thiệp  
☑ Augmentation — AI gợi ý, user quyết định cuối cùng

**Justify:** Augmentation — AI gợi ý câu trả lời và tóm tắt, phụ huynh quyết định đọc thêm qua deep-link. Với tài chính/điểm số AI không generate — chỉ route user đến đúng màn hình dữ liệu cứng. Cost of reject = 0 (phụ huynh chỉ cần bỏ qua gợi ý).


## Learning signal

| # | Câu hỏi | Trả lời |
|---|---------|---------|
| 1 | User correction đi vào đâu? | Khi user bỏ qua kết quả AI, click "Đọc toàn văn" hoặc tắt Smart Brief → ghi implicit feedback log → dùng để cải thiện NLP intent model và synonym mapping |
| 2 | Product thu signal gì để biết tốt lên hay tệ đi? | Implicit: Search Success Rate (% query trả về đúng data), Notification Open Rate, Time-to-Information. Explicit: nút "AI hiểu sai" / thumbs down. Correction: user bỏ qua output AI và tự điều hướng thủ công |
| 3 | Data thuộc loại nào? ☑ User-specific · ☑ Domain-specific · ☐ Real-time · ☐ Human-judgment · ☐ Khác: ___ | User-specific (StudentID riêng cho từng con) + Domain-specific (từ điển đồng nghĩa Vinschool: "tiền ăn trưa" = "Phí dịch vụ bán trú", "Toán tiếng Anh" = "CIE Maths") |

**Có marginal value không?** Có — model chung không biết từ điển nội bộ Vinschool (CIE Maths, Phí bán trú…) và không có mapping StudentID cụ thể của từng gia đình. Data này không ai khác thu được ngoài Vinschool.
