import json
import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

# Attempt to import rag_service, or use a placeholder if not found
try:
    from services.rag_service import get_rag_service
except ImportError:
    try:
        from .rag_service import get_rag_service
    except ImportError:
        get_rag_service = None

class VinschoolTools:
    def __init__(self, data_path: str = None):
        if data_path is None:
            # Get the path to rag_data.json relative to this file
            # Assuming structure: /services/vinschool_tools.py and /data/rag_data.json
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_path = os.path.join(base_dir, "data", "rag_data.json")
        else:
            self.data_path = data_path
            
        self.chunks = []
        self._rag_service = None
        self.tz = ZoneInfo("Asia/Ho_Chi_Minh")
        self.load_data()

    @property
    def rag_service(self):
        if self._rag_service is None and get_rag_service is not None:
            self._rag_service = get_rag_service()
        return self._rag_service

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)
        else:
            print(f"Error: Data file not found at {self.data_path}")

    def _filter_by_sheet(self, sheet_name: str) -> List[Dict]:
        return [c for c in self.chunks if c.get("metadata", {}).get("sheet") == sheet_name]

    def get_student_profile(self, student_name: str = "Nguyễn Hưng") -> str:
        """Lấy thông tin cơ bản của học sinh."""
        sheet_data = self._filter_by_sheet("Student Information")
        for item in sheet_data:
            if student_name.lower() in item["content"].lower():
                return item["content"]
        return f"Không tìm thấy thông tin cho học sinh {student_name}."

    def get_attendance(self, date_str: str, student_id: str = "VS108245") -> str:
        """
        Lấy thông tin điểm danh của học sinh trong một ngày cụ thể.
        date_str: Định dạng 'DD/MM/YYYY' (ví dụ: '30/03/2026')
        """
        sheet_data = self._filter_by_sheet("Điểm danh")
        daily_attendance = []
        current_date_found = False
        
        for item in sheet_data:
            content = item["content"]
            if date_str in content:
                daily_attendance.append(content)
                current_date_found = True
            elif current_date_found and "Ngày:" not in content:
                daily_attendance.append(content)
            elif current_date_found and "Ngày:" in content and date_str not in content:
                break
                
        if not daily_attendance:
            return f"Không có dữ liệu điểm danh cho ngày {date_str}."
        
        return "\n---\n".join(daily_attendance)

    def get_homework(self, status: str = "all", student_id: str = "VS108245") -> str:
        """
        Lấy danh sách bài tập. 
        status: 'all', 'Chưa làm', 'Đã làm', 'Đã hoàn thành'
        """
        sheet_data = self._filter_by_sheet("Bài tập")
        filtered = []
        for item in sheet_data:
            content = item["content"]
            if status == "all" or status.lower() in content.lower():
                filtered.append(content)
        
        if not filtered:
            return f"Không tìm thấy bài tập với trạng thái '{status}'."
            
        return "\n---\n".join(filtered)

    def get_menu(self, date_str: str) -> str:
        """
        Lấy thực đơn của nhà trường.
        date_str: Định dạng 'DD/MM/YYYY' (ví dụ: '16/03/2026')
        """
        sheet_data = self._filter_by_sheet("Thực đơn")
        menu_items = []
        found_date = False
        
        for item in sheet_data:
            content = item["content"]
            if date_str in content:
                found_date = True
                menu_items.append(content)
            elif found_date and "Ngày:" not in content:
                 menu_items.append(content)
            elif found_date and "Ngày:" in content:
                break
                
        if not menu_items:
            return f"Không có dữ liệu thực đơn cho ngày {date_str}."
            
        return "\n---\n".join(menu_items)

    def get_timetable(self, weekday: Optional[int] = None) -> str:
        """
        Lấy thời khoá biểu theo thứ trong tuần.
        weekday: 2..6 tương ứng Thứ 2..Thứ 6. Nếu không truyền sẽ dùng "hôm nay" theo múi giờ Việt Nam.
        """
        if weekday is None:
            # Python isoweekday(): Mon=1..Sun=7 → map Mon..Fri to 2..6 labels used in data
            iso = datetime.now(self.tz).isoweekday()
            weekday = iso + 1  # Mon(1)->2, Tue(2)->3, ..., Fri(5)->6

        if weekday not in (2, 3, 4, 5, 6):
            return "Vui lòng chọn thứ từ Thứ 2 đến Thứ 6 (weekday=2..6)."

        sheet_data = self._filter_by_sheet("Thời khoá biểu")
        if not sheet_data:
            return "Không tìm thấy dữ liệu thời khoá biểu."

        day_label = f"Thứ {weekday}"
        out: List[str] = []

        for item in sheet_data:
            content = item.get("content", "")
            # Extract period & time for context
            period = None
            time_range = None
            m1 = re.search(r"-\s*Tiết:\s*(.+)", content)
            if m1:
                period = m1.group(1).strip()
            m2 = re.search(r"-\s*Thời gian:\s*([0-9]{2}:[0-9]{2}\s*-\s*[0-9]{2}:[0-9]{2})", content)
            if m2:
                time_range = m2.group(1).strip()

            # Find the subject for the requested weekday inside this chunk
            # Content uses lines like "- Thứ 2: <môn>\n\n(Teacher)"
            subj_match = re.search(rf"-\s*{re.escape(day_label)}:\s*(.+)", content)
            if not subj_match:
                continue
            subject = subj_match.group(1).strip()

            header = []
            if period is not None:
                header.append(f"Tiết: {period}")
            if time_range is not None:
                header.append(f"Thời gian: {time_range}")

            if header:
                out.append(f"{' · '.join(header)}\n- {day_label}: {subject}")
            else:
                out.append(f"- {day_label}: {subject}")

        if not out:
            return f"Không có dữ liệu thời khoá biểu cho {day_label}."

        return "\n---\n".join(out)

    def get_tuition_info(self, student_id: str = "VS108245") -> str:
        """Lấy thông tin học phí và các khoản phí."""
        sheet_data = self._filter_by_sheet("Học phí")
        if not sheet_data:
            return "Không tìm thấy dữ liệu học phí."

        # Chuẩn hoá để AI có thể trả lời dễ đọc mà vẫn giữ nguyên số liệu.
        # Định dạng dữ liệu trong rag_data.json theo dạng:
        # "Dữ liệu từ bảng: Học phí\n- <tên khoản>\n- <đã nộp>\n- <tổng phải nộp>"
        entries: List[str] = []
        total_entry: str | None = None

        def _fmt_vnd_like_number(s: str) -> str:
            # Chỉ format khi là số nguyên dương dạng chữ số thuần.
            # Ví dụ: "85320000" -> "85.320.000"
            t = s.strip()
            if not t.isdigit():
                return s
            return f"{int(t):,}".replace(",", ".")

        for item in sheet_data:
            content = item.get("content", "")
            lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
            fields = [ln[2:].strip() for ln in lines if ln.startswith("- ")]
            if len(fields) < 3:
                # Fallback giữ nguyên content nếu cấu trúc không như kỳ vọng
                entries.append(content)
                continue

            name, paid, due = fields[0], _fmt_vnd_like_number(fields[1]), _fmt_vnd_like_number(fields[2])
            line = f"- **{name}**: {paid} / {due}"
            if name.strip().lower() == "tổng số tiền":
                total_entry = line
            else:
                entries.append(line)

        header = "Chào phụ huynh, dưới đây là **thông tin học phí** của con (định dạng: **Học kỳ 1 / Cả năm**):"
        body = "\n".join(entries)
        total = f"\n\n{total_entry}" if total_entry else ""
        return f"{header}\n\n{body}{total}"

    def get_teacher_comments(self, date_str: Optional[str] = None) -> str:
        """Lấy nhận xét của giáo viên."""
        sheet_data = self._filter_by_sheet("Nhận xét")
        if not date_str:
            return "\n---\n".join([item["content"] for item in sheet_data])
            
        filtered = [item["content"] for item in sheet_data if date_str in item["content"]]
        if not filtered:
            return f"Không có nhận xét nào trong ngày {date_str}."
        return "\n---\n".join(filtered)

    def get_grades(self, subject: Optional[str] = None) -> str:
        """
        Lấy kết quả học tập (điểm số) của học sinh.
        subject: Tên môn học (ví dụ: 'Tiếng Việt', 'CIE Maths')
        """
        sheet_data = self._filter_by_sheet("Kết quả học tập")
        if not sheet_data:
            return "Không tìm thấy dữ liệu kết quả học tập."
            
        results = []
        for item in sheet_data:
            content = item["content"]
            if not subject or subject.lower() in content.lower():
                results.append(content)
        
        if not results:
            if subject:
                return f"Không tìm thấy kết quả học tập cho môn '{subject}'."
            return "Không tìm thấy dữ liệu kết quả học tập."
            
        return "\n---\n".join(results)

    def get_latest_comments(self, limit: int = 3) -> str:
        """
        Lấy các nhận xét mới nhất của giáo viên.
        limit: Số lượng nhận xét mới nhất cần lấy.
        """
        sheet_data = self._filter_by_sheet("Nhận xét")
        if not sheet_data:
            return "Không tìm thấy dữ liệu nhận xét."
        
        # Sort items by date in the content string
        # Content format: "Dữ liệu từ bảng: Nhận xét\n- Ngày: YYYY-MM-DD ..."
        def get_date(item):
            match = re.search(r"Ngày: (\d{4}-\d{2}-\d{2})", item["content"])
            return match.group(1) if match else "0000-00-00"
            
        sorted_data = sorted(sheet_data, key=get_date, reverse=True)
        latest = [item["content"] for item in sorted_data[:limit]]
        
        return "\n---\n".join(latest)

    def get_notifications(self, limit: int = 5) -> str:
        """
        Lấy danh sách các thông báo mới nhất từ nhà trường.
        """
        sheet_data = self._filter_by_sheet("Thông báo")
        if not sheet_data:
            return "Hiện không có thông báo nào mới."
            
        # Limit the results
        latest = [item["content"] for item in sheet_data[:limit]]
        return "\n---\n".join(latest)

    def get_contact_info(self, name: str) -> str:
        """
        Lấy thông tin liên lạc (Email, Số điện thoại) của một người cụ thể (giáo viên hoặc phụ huynh).
        """
        # Note: double space in "Parent  Guardian Information" as seen in rag_data.json
        sheets = ["Teacher Information", "Parent  Guardian Information"]
        found_records = []
        
        for sheet_name in sheets:
            sheet_data = self._filter_by_sheet(sheet_name)
            for item in sheet_data:
                if name.lower() in item["content"].lower():
                    found_records.append(item["content"])
                    
        if not found_records:
            return f"Không tìm thấy thông tin liên lạc cho '{name}'."
            
        return "\n---\n".join(found_records)

    def general_search(self, query: str) -> str:
        """Tìm kiếm thông tin chung bằng RAG."""
        if self.rag_service:
            results = self.rag_service.query(query, top_k=3)
            if not results:
                return "Không tìm thấy thông tin liên quan."
                
            formatted_results = []
            for res in results:
                formatted_results.append(f"Nguồn: {res['metadata'].get('sheet', 'Chung')}\n{res['content']}")
                
            return "\n---\n".join(formatted_results)
        return "Hiện chưa hỗ trợ tìm kiếm nâng cao (RAG Service không khả dụng)."

# Global helper instance
_vinschool_tools = None

def get_vinschool_tools():
    global _vinschool_tools
    if _vinschool_tools is None:
        _vinschool_tools = VinschoolTools()
    return _vinschool_tools
