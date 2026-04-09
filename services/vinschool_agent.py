from google import genai
from google.genai import types
from services.vinschool_tools import get_vinschool_tools
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "our-audio-472409-e5")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize the Gen AI Client for Vertex AI using API Key (no gcloud needed)
client = genai.Client(
    vertexai=False,
    api_key=API_KEY
)

# Tool declarations for Gemini (New SDK Format)
get_student_profile_declaration = types.FunctionDeclaration(
    name="get_student_profile",
    description="Lấy thông tin cơ bản của học sinh (tên, lớp, trường, mã học sinh).",
    parameters={
        "type": "OBJECT",
        "properties": {
            "student_name": {
                "type": "STRING",
                "description": "Tên học sinh cần tra cứu."
            }
        }
    }
)

get_attendance_declaration = types.FunctionDeclaration(
    name="get_attendance",
    description="Lấy thông tin điểm danh chi tiết của học sinh theo ngày.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "date_str": {
                "type": "STRING",
                "description": "Ngày cần tra cứu định dạng DD/MM/YYYY (ví dụ: 30/03/2026)."
            }
        },
        "required": ["date_str"]
    }
)

get_homework_declaration = types.FunctionDeclaration(
    name="get_homework",
    description="Lấy danh sách bài tập, hạn nộp và trạng thái hoàn thành.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "status": {
                "type": "STRING",
                "description": "Lọc theo trạng thái: 'all', 'Chưa làm', 'Đã làm'."
            }
        }
    }
)

get_menu_declaration = types.FunctionDeclaration(
    name="get_menu",
    description="Lấy thực đơn (bữa trưa và bữa phụ) của nhà trường theo ngày.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "date_str": {
                "type": "STRING",
                "description": "Ngày cần tra cứu định dạng DD/MM/YYYY (ví dụ: 16/03/2026)."
            }
        },
        "required": ["date_str"]
    }
)

get_tuition_info_declaration = types.FunctionDeclaration(
    name="get_tuition_info",
    description="Lấy thông tin chi tiết về học phí, số dư và hạn thanh toán.",
    parameters={"type": "OBJECT", "properties": {}}
)

general_search_declaration = types.FunctionDeclaration(
    name="general_search",
    description="Tìm kiếm thông tin chung về quy định, FAQ hoặc thông báo của nhà trường.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "Câu hỏi tra cứu."
            }
        },
        "required": ["query"]
    }
)

get_grades_declaration = types.FunctionDeclaration(
    name="get_grades",
    description="Lấy kết quả học tập (điểm số) của học sinh. Có thể tra cứu cho một môn cụ thể hoặc tất cả các môn.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "subject": {"type": "STRING", "description": "Tên môn học cần tra cứu (ví dụ: 'Toán', 'Tiếng Việt'). Để trống nếu muốn lấy tất cả."}
        }
    }
)

get_latest_comments_declaration = types.FunctionDeclaration(
    name="get_latest_comments",
    description="Lấy danh sách các nhận xét mới nhất từ giáo viên.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "limit": {"type": "INTEGER", "description": "Số lượng nhận xét mới nhất cần lấy (mặc định là 3)."}
        }
    }
)

get_notifications_declaration = types.FunctionDeclaration(
    name="get_notifications",
    description="Lấy danh sách các thông báo mới nhất từ nhà trường (khảo sát, sự kiện, học vụ, y tế,...).",
    parameters={
        "type": "OBJECT",
        "properties": {
            "limit": {"type": "INTEGER", "description": "Số lượng thông báo mới nhất cần lấy (mặc định là 5)."}
        }
    }
)

get_contact_info_declaration = types.FunctionDeclaration(
    name="get_contact_info",
    description="Lấy thông tin liên lạc (Email, Số điện thoại) của giáo viên hoặc phụ huynh theo tên.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "name": {"type": "STRING", "description": "Tên người cần tra cứu thông tin liên lạc."}
        },
        "required": ["name"]
    }
)

vinschool_tool = types.Tool(
    function_declarations=[
        get_student_profile_declaration,
        get_attendance_declaration,
        get_homework_declaration,
        get_menu_declaration,
        get_tuition_info_declaration,
        general_search_declaration,
        get_grades_declaration,
        get_latest_comments_declaration,
        get_notifications_declaration,
        get_contact_info_declaration
    ]
)

class VinschoolAgent:
    def __init__(self, model_name: str = "gemini-2.5-flash-lite"):
        self.model_name = model_name
        self.tools = get_vinschool_tools()
        self.system_instruction = (
            "Bạn là Vin-Assistant, trợ lý ảo thông minh cho phụ huynh VinSchool. "
            "Nhiệm vụ của bạn là giúp phụ huynh tra cứu thông tin nhanh chóng và chính xác. "
            "QUY TẮC CỐT LÕI: "
            "1. Luôn sử dụng tool để lấy dữ liệu trước khi trả lời. "
            "2. Đối với Học phí và Bài tập: Trả lời ngắn gọn, trung thực, tuyệt đối không bịa đặt số liệu. "
            "3. Nếu không tìm thấy dữ liệu, hãy báo rõ và gợi ý phụ huynh kiểm tra lại thông tin. "
            "4. Giọng điệu: Lễ phép, thân thiện, chuyên nghiệp. "
            "5. Luôn ưu tiên tóm tắt ý chính thành bullet points cho dễ đọc."
        )
        
        # Start chat with config
        self.chat = client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                tools=[vinschool_tool]
            )
        )

    async def chat_with_tools(self, user_input: str):
        response = self.chat.send_message(user_input)
        
        # Multi-turn tool call handling
        max_turns = 10
        turn = 0
        
        while turn < max_turns:
            # Check if there's a function call
            if not response.candidates[0].content.parts[0].function_call:
                break
                
            function_call = response.candidates[0].content.parts[0].function_call
            name = function_call.name
            args = function_call.args
            
            # Execute the tool
            result = ""
            if name == "get_student_profile":
                result = self.tools.get_student_profile(**args)
            elif name == "get_attendance":
                result = self.tools.get_attendance(**args)
            elif name == "get_homework":
                result = self.tools.get_homework(**args)
            elif name == "get_menu":
                result = self.tools.get_menu(**args)
            elif name == "get_tuition_info":
                result = self.tools.get_tuition_info(**args)
            elif name == "general_search":
                result = self.tools.general_search(**args)
            elif name == "get_grades":
                result = self.tools.get_grades(**args)
            elif name == "get_latest_comments":
                result = self.tools.get_latest_comments(**args)
            elif name == "get_notifications":
                result = self.tools.get_notifications(**args)
            elif name == "get_contact_info":
                result = self.tools.get_contact_info(**args)
            
            # Send result back to AI
            response = self.chat.send_message(
                types.Part.from_function_response(
                    name=name,
                    response={"content": result}
                )
            )
            turn += 1
            
        return response.text

    async def get_daily_brief(self, date_str: str) -> str:
        """Thực hiện Feature 2: Smart Daily Brief."""
        # Gom dữ liệu từ nhiều tool
        attendance = self.tools.get_attendance(date_str)
        menu = self.tools.get_menu(date_str)
        comments = self.tools.get_teacher_comments(date_str)
        
        prompt = (
            f"Hãy tạo một 'Bản tin 1 Phút Mỗi Sáng' cho phụ huynh vào ngày {date_str} dựa trên dữ liệu sau:\n"
            f"ĐIỂM DANH:\n{attendance}\n"
            f"THỰC ĐƠN:\n{menu}\n"
            f"NHẬN XÉT GIÁO VIÊN:\n{comments}\n\n"
            "YÊU CẦU: Tóm tắt 3 sự kiện/thông tin nổi bật nhất thành các dòng cực ngắn gọn. "
            "Nếu có bất thường (đi muộn, không ăn hết suất), hãy highlight. "
            "Nếu ngày học suôn sẻ, hãy dùng giọng điệu tích cực."
        )
        
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text

    async def extract_actionable_notif(self, announcement_text: str) -> str:
        """Thực hiện Feature 3: Actionable Notifications."""
        prompt = (
            "Bạn là chuyên gia tóm tắt thông báo học đường. Hãy trích xuất thông tin từ văn bản sau thành 3 ý chính:\n"
            "1. Sự kiện gì?\n"
            "2. Hạn chót bao giờ?\n"
            "3. Hành động cần làm (nút bấm/đăng ký ở đâu)?\n\n"
            f"VĂN BẢN: {announcement_text}\n\n"
            "Định dạng trả về: Bullet points ngắn gọn."
        )
        
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text

# Singleton implementation
_vinschool_agent = None

def get_vinschool_agent():
    global _vinschool_agent
    if _vinschool_agent is None:
        _vinschool_agent = VinschoolAgent()
    return _vinschool_agent
