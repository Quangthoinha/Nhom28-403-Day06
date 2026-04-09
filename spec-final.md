# SPEC — Vinschool One "Smart Hub"

**Nhóm:** E403 — Nhóm 28
**Track:** VinUni-VinSchool
**Problem statement:** Phụ huynh VinSchool mất quá nhiều thời gian tìm thông tin trong app vì dữ liệu bị phân mảnh thành hàng chục tab; AI tổng hợp và trả lời trực tiếp bằng giao diện hội thoại, thay vì bắt phụ huynh tự điều hướng.

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

## 2. User Stories — 4 paths

### Feature 1: Vin-Assistant (Giao diện tìm kiếm hội thoại)

**Trigger:** Phụ huynh gõ hoặc nói câu hỏi vào thanh search trên màn hình chính → AI nhận diện intent, gọi API nội bộ, trả về câu trả lời tóm tắt + deep-link.

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | Phụ huynh gõ "Tuần này Hưng có bài tập chưa làm không?" → AI nhận diện Intent [Check_Homework], Entity [Current_Week, Student=Hưng] → hiện 3 bullet points ngắn gọn + nút "Mở bài tập". Phụ huynh bấm xác nhận, xong trong < 10 giây. |
| **Low-confidence** — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | Phụ huynh hỏi "Hôm nay có gì đặc biệt không?" → query quá mơ hồ, AI không chắc intent → hiện 3 gợi ý chủ đề: "Xem thực đơn hôm nay / Kiểm tra TKB / Xem thông báo mới" với confidence thấp được hiển thị bằng màu xám và label "Ý bạn muốn hỏi về:". Phụ huynh chọn 1. |
| **Failure** — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | Phụ huynh hỏi "Tiền hụi tháng này" (tiếng lóng) → AI không nhận diện được → **không đoán mò**, hiện thông báo "Tôi chưa hiểu câu hỏi này. Bạn muốn hỏi về: Học phí / Phí bán trú / Phí ngoại khóa?" → phụ huynh chọn hoặc gõ lại. |
| **Correction** — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | Phụ huynh bấm "Không phải thứ tôi cần" → ghi log [query gốc + intent AI đoán + action phụ huynh thực sự làm] → dùng để cập nhật synonym mapping và intent classifier hàng tuần. |

---

### Feature 2: Smart Daily Brief (Bản tin 1 phút lúc 19h)

**Trigger:** Hệ thống tự động chạy lúc 19h00 mỗi ngày → LLM tổng hợp các sự kiện trong ngày của con thành 1 push notification tóm tắt → phụ huynh tap mở xem thẻ trực quan.

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | Phụ huynh nhận Push: *"Tóm tắt thứ 4 của Hưng: Vắng 1 tiết ESL, ăn hết suất, cô Kim Anh khen bài Văn."* → tap vào → hiện 3 thẻ trực quan (Điểm danh / Thực đơn / Nhận xét) → phụ huynh nắm tình hình trong < 30 giây. |
| **Low-confidence** — AI không chắc | System báo "không chắc" bằng cách nào? | Nhà trường nhập nhận xét mơ hồ: "Con có tiến bộ" → LLM không tự thêm chi tiết không có trong data → hiện nguyên văn nhận xét của giáo viên, không tóm tắt lại, kèm label "Nhận xét gốc từ cô giáo". |
| **Failure** — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | LLM highlight "bất thường" nhưng thực ra là data nhập sai từ hệ thống (VD: điểm danh vắng do lỗi nhập liệu) → phụ huynh thấy thông tin vắng mặt → nhấn vào thẻ → deep-link dẫn về màn hình điểm danh gốc để phụ huynh tự kiểm tra và liên hệ giáo viên nếu cần. |
| **Correction** — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | Phụ huynh bấm "Tóm tắt không chính xác" → ghi log session + câu tóm tắt bị từ chối → dùng để review prompt LLM, không dùng để retrain model (vì nguồn lỗi có thể là data đầu vào sai, không phải model). |

---

### Feature 3: Actionable Notifications (Rút gọn thông báo dài)

**Trigger:** Nhà trường gửi thông báo văn bản dài (> 200 chữ) → AI tự động extract 3 bullet points: Sự kiện gì / Hạn chót bao giờ / Hành động cần làm → phụ huynh nhận bản rút gọn, vẫn có nút "Đọc toàn văn bản".

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | Thông báo 500 chữ về nộp tiền ngoại khóa → AI extract: "**Sự kiện:** Cắm trại Đà Lạt K5. **Hạn đăng ký:** 15/04/2026. **Hành động:** [Nút Đăng ký & Nộp phí]." → Phụ huynh bấm nút, hoàn thành trong < 30 giây. |
| **Low-confidence** — AI không chắc | System báo bằng cách nào? | Thông báo chứa nhiều deadline cho nhiều khối lớp khác nhau → AI không chắc bullet nào áp dụng cho con phụ huynh → **chỉ highlight phần liên quan đến khối lớp của con** (dựa vào StudentID) và ghi chú "Thông báo này có nhiều phần — đây là phần áp dụng cho con bạn." |
| **Failure** — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | AI extract sai deadline (nhầm ngày tháng trong văn bản phức tạp) → **Với thông tin tài chính và ngày tháng: AI không được tự generate, phải trích nguyên văn từ văn bản gốc** (copy exact string, không paraphrase). Luôn giữ nút "Đọc toàn văn bản" để phụ huynh tự xác minh. |
| **Correction** — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | Phụ huynh bấm "Thông tin không đúng" → ghi log loại văn bản + điểm extract bị từ chối → dùng để cải thiện extraction prompt, ưu tiên các loại văn bản hay bị lỗi. |

---

## 3. Eval Metrics + Threshold

**Optimize precision hay recall?**

Câu trả lời phụ thuộc vào từng feature:

- **Vin-Assistant → Recall-first:** Bỏ sót câu hỏi của phụ huynh (AI trả lời "Tôi không hiểu") tệ hơn trả lời hơi rộng (phụ huynh tự lọc). Nếu AI từ chối quá nhiều → phụ huynh quay lại hỏi Zalo giáo viên → mất toàn bộ giá trị sản phẩm.
- **Actionable Notifications (tài chính, ngày tháng) → Precision-first:** Trích xuất sai số tiền hoặc deadline → phụ huynh nộp sai / trễ hạn → thiệt hại thực tế. Bỏ sót (hiện thông báo đầy đủ) tốt hơn extract sai.

**Nếu sai ngược lại thì sao?**
- Nếu chọn Precision cho Vin-Assistant: AI từ chối quá nhiều câu hỏi hợp lệ → phụ huynh bỏ dùng.
- Nếu chọn Recall cho Notifications tài chính: AI extract sai số tiền → phụ huynh mất tiền hoặc bỏ lỡ deadline quan trọng.

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| **Search Success Rate** — tỷ lệ câu hỏi Vin-Assistant được trả về đúng data (recall) | ≥ 85% | < 70% trong 1 tuần → NLP model không hiểu ngôn ngữ tự nhiên phụ huynh; dừng rollout, review synonym mapping |
| **Time-to-Information** — thời gian từ lúc mở app đến khi phụ huynh có thông tin cần thiết | < 10 giây | Phụ huynh phải click > 4 lần → AI không giảm được friction; review UX flow |
| **Smart Brief Open Rate** — tỷ lệ phụ huynh mở push notification Smart Daily Brief | ≥ 60% | Phụ huynh tắt push notification của app → nội dung tóm tắt không có giá trị; review prompt tóm tắt và thời điểm gửi |

---

## 4. Top 3 Failure Modes

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | **Vocabulary Gap:** Phụ huynh dùng từ đời thường ("tiền ăn trưa", "Toán tiếng Anh", "tiền hụi") khác với thuật ngữ hệ thống ("phí dịch vụ bán trú", "CIE Mathematics") → NLP không map được intent. | AI báo "Không tìm thấy thông tin" với câu hỏi hợp lệ → **phụ huynh không biết mình đang bị miss** → quay lại hỏi Zalo giáo viên, mất tin tưởng vào app. Đây là failure âm thầm, nguy hiểm nhất. | Xây dựng **Synonym Dictionary** chuyên biệt cho ngữ cảnh VinSchool trước khi deploy (tiền ăn → phí bán trú; Toán Anh → CIE Maths...). Thu thập thêm từ đồng nghĩa liên tục từ correction log của phụ huynh. |
| 2 | **Hallucination tài chính:** Phụ huynh hỏi "Tôi phải đóng bao nhiêu tiền?" → LLM paraphrase số tiền từ văn bản → nhầm từ 110.520.000đ thành 110.000đ hoặc 110.5 triệu. | Phụ huynh đóng thiếu/sai số tiền → phát sinh tranh cãi với nhà trường. Đây là lỗi có hậu quả tài chính thực tế, **phụ huynh không thể tự phát hiện** nếu không đọc kỹ văn bản gốc. | AI **tuyệt đối không dùng LLM text generation** cho câu hỏi về Tài chính, Điểm số, Ngày tháng. Với các mục này, AI chỉ định danh intent rồi hiển thị **hard-coded UI / bảng biểu lấy thẳng từ database** — không qua bước summarize. |
| 3 | **Privacy cross-contamination:** Gia đình có 2 con (Hưng lớp 5, em gái lớp 2) → phụ huynh đang xem profile Hưng nhưng AI trả lời nhầm data thực đơn / điểm danh của em. | Phụ huynh nhận thông tin sai con → đưa ra quyết định sai (VD: nhắc sai con mang đồ thể dục). Nếu xảy ra nhiều lần → phụ huynh mất tin tưởng hoàn toàn vào tính năng AI. | **Contextual grounding bắt buộc:** mọi prompt gửi đến LLM/NLP đều phải đính kèm `[StudentID]` đang được select trên Header của app. Filter data ở tầng API trước khi đưa vào model, không để model tự chọn student. |

---

## 5. ROI 3 kịch bản

**Baseline assumptions:**
- Mỗi trường VinSchool có ~500 phụ huynh dùng app thường xuyên.
- Mỗi giáo viên nhận trung bình 10 tin nhắn Zalo/ngày từ phụ huynh hỏi thông tin app đã có.
- Chi phí cơ hội 1 giờ giáo viên: ~150.000đ/giờ.
- Cost inference: chủ yếu NLP intent classification + internal API, LLM chỉ dùng cho Smart Brief summarization (~500 tokens/phụ huynh/ngày).

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | 200 phụ huynh dùng Vin-Assistant (40% adoption), giảm 20% tin nhắn Zalo cho giáo viên. Smart Brief open rate 45%. | 380 phụ huynh dùng thường xuyên (75% adoption), giảm 40% tin nhắn Zalo. Smart Brief open rate 65%. Phụ huynh tiết kiệm 5 phút/ngày tìm kiếm. | 480 phụ huynh dùng hàng ngày (95% adoption), giảm 60% tin nhắn Zalo. Smart Brief open rate 75%. App trở thành default habit buổi tối của phụ huynh. |
| **Cost** | ~500.000đ/tháng (API inference cho NLP + LLM summarization, ~$20/tháng) | ~1.500.000đ/tháng (scale theo số query + Smart Brief) | ~3.000.000đ/tháng (thêm voice processing, cá nhân hóa cao hơn) |
| **Benefit** | Giảm 2 giờ Zalo/giáo viên/tuần × 30 giáo viên = 60 giờ/tuần → 900.000đ/tuần (~3.6 triệu/tháng) | Giảm 4 giờ/giáo viên/tuần × 30 GV = 120 giờ/tuần → 7.2 triệu/tháng + tăng NPS app | Giảm 6 giờ/GV/tuần = 10.8 triệu/tháng + data phụ huynh engagement có giá trị cho chiến lược retention của VinSchool |
| **Net** | +3.1 triệu/tháng | +5.7 triệu/tháng | +7.8 triệu/tháng |

**Kill criteria:**
- Search Success Rate < 70% sau 4 tuần vận hành (NLP không hiểu phụ huynh → toàn bộ giá trị sụp đổ).
- Smart Brief open rate < 40% sau 2 tháng (phụ huynh tắt notification → feature không tiếp cận được người dùng).
- Phụ huynh report thông tin sai > 5 case/tuần (trust break → không thể phục hồi nếu để kéo dài).
- Cost vượt benefit 2 tháng liên tục ở kịch bản Realistic.

---

## 6. Mini AI Spec (1 trang)

### Vinschool One "Smart Hub" — Tóm tắt AI Spec

**Giải gì, cho ai:**
Vinschool One hiện chứa đủ dữ liệu nhưng bị phân mảnh thành hàng chục tab — phụ huynh bận rộn không có thời gian điều hướng thủ công mỗi ngày. Smart Hub biến app từ "kho dữ liệu thụ động" thành "trợ lý chủ động": phụ huynh hỏi bằng ngôn ngữ tự nhiên, AI trả lời ngay; thay vì phụ huynh đi tìm data, data tự tìm phụ huynh qua bản tin tóm tắt hàng ngày và thông báo đã được xử lý gọn.

**Auto hay Aug:**
Augmentation xuyên suốt. AI không tự động thực hiện hành động thay phụ huynh — AI chỉ rút ngắn thời gian tìm và đọc thông tin, quyết định cuối cùng (đăng ký, liên hệ giáo viên, nộp tiền) vẫn thuộc về phụ huynh. Mọi câu trả lời đều kèm deep-link về nguồn gốc data.

**Quality — Precision vs Recall:**
- Vin-Assistant: **Recall-first** — không bỏ sót câu hỏi hợp lệ của phụ huynh, thà gợi ý chủ đề gần đúng còn hơn từ chối.
- Actionable Notifications (tài chính, ngày tháng): **Precision-first** — không paraphrase số tiền hay deadline, chỉ trích nguyên văn từ nguồn.
- Smart Daily Brief: cân bằng — LLM chỉ tóm tắt thông tin phi tài chính (nhận xét, thực đơn, điểm danh), không được suy diễn thêm.

**Risk chính:**
1. Vocabulary gap — phụ huynh dùng từ khác hệ thống; giải quyết bằng synonym dictionary chuyên biệt VinSchool.
2. Hallucination tài chính — hard rule: không dùng LLM để generate câu trả lời về tiền hoặc điểm số.
3. Privacy cross-contamination — StudentID bắt buộc trong mọi API call, không để model tự chọn.

**Data flywheel:**
Mỗi lần phụ huynh tương tác với Vin-Assistant (đặc biệt các lần correction — gõ lại, chọn chủ đề khác, bấm "Không đúng") đều cung cấp data để mở rộng synonym mapping và cải thiện intent classifier. Càng nhiều phụ huynh dùng → AI càng hiểu tiếng Việt đời thường của phụ huynh VinSchool → Search Success Rate tăng → nhiều phụ huynh dùng hơn. Đây là flywheel nhỏ nhưng có moat thực tế vì data này là unique với VinSchool, không public model nào có.

**Điều kiện thành công tối thiểu:**
- Synonym dictionary phải cover ít nhất 30 cụm từ phổ biến nhất trước khi launch.
- Tất cả câu trả lời liên quan tài chính phải đi qua hard-coded UI, không qua LLM.
- StudentID context phải được enforce ở tầng middleware, không phụ thuộc vào prompt.
