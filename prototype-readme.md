# Prototype — Vinschool One "Smart Hub"

## Mô tả
Prototype mô phỏng 3 tính năng cốt lõi của Smart Hub:  
1. **Vin-Assistant** — giao diện chat/voice search ngôn ngữ tự nhiên (hỏi bài tập, học phí, thực đơn…).  
2. **Smart Daily Brief** — bản tin tóm tắt push lúc 19h với 3 thẻ trực quan.  
3. **Actionable Notifications** — rút gọn thông báo dài thành bullet points + nút hành động.  

Tập trung demo flow Happy Path + Low-confidence + Failure + Correction cho Vin-Assistant và Smart Daily Brief. Tất cả câu trả lời đều kèm deep-link giả lập và grounding về màn hình gốc.

## Level: Mock prototype
- UI build bằng Claude Artifacts / Cursor (HTML + Tailwind + JS)  
- 2 flow chính chạy thật:  
  - Chat Vin-Assistant dùng Gemini 2.0 Flash / Grok (intent classification + synonym mapping)  
  - Smart Daily Brief simulation (có sẵn data mẫu StudentID)  
- Voice input demo dùng Web Speech API


## Tools
- **UI/Frontend**: Claude Artifacts + htlm + css  
- **AI/NLP**: Google Gemini 2.0 Flash qua API sử dụng kĩ thuật RAG để truy xuất thông tin rồi tạo intent detection, summarization và synonym handling  
- **Prompt**: System prompt + few-shot examples với synonym dictionary VinSchool (tiền ăn trưa → phí bán trú, Toán tiếng Anh → CIE Maths, tiền hụi → học phí…)  
- **Data mock**: JSON chứa sample data của 2 học sinh (Hưng lớp 5) với StudentID

## Phân công
| Thành viên | Phần | Output |
|-----------|------|--------|
| Quang | RAG + prompt engineering, backend | spec/spec-final.md phần 1, 4 |
| Huy | User stories 4 paths + prompt test + demo script|spec-final.md phần 2, demo-slide.pdf|
| Bảo | Eval metrics + ROI + demo slides | spec/spec-final.md phần 3, 5, demo/slides.pdf |
| Long | UI/UX prototype + demo script + integration Gemini | prototype/|

