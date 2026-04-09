from services.vinschool_agent import get_vinschool_agent
import asyncio

async def test_agent():
    agent = get_vinschool_agent()
    
    print("=== Test 1: Intent Check (Tuần này con có bài tập nào chưa làm?) ===")
    response = await agent.chat_with_tools("Tuần này con có bài tập nào chưa làm?")
    print(f"AI: {response}")
    
    print("\n=== Test 2: Multi-data Query (Hôm nay con ăn gì và có đi học đúng giờ không?) ===")
    # Note: Using 30/03/2026 for attendance and 16/03/2026 for menu as per mock data
    response = await agent.chat_with_tools("Hôm nay là 30/03/2026, con có đi học đúng giờ không? Và thực đơn hôm nay có gì?")
    print(f"AI: {response}")
    
    print("\n=== Test 3: Daily Brief (30/03/2026) ===")
    brief = await agent.get_daily_brief("30/03/2026")
    print(f"Daily Brief:\n{brief}")
    
    print("\n=== Test 4: Actionable Notification ===")
    long_text = """
    THÔNG BÁO VỀ VIỆC ĐĂNG KÝ THAM GIA HOẠT ĐỘNG NGOẠI KHÓA HÈ 2026
    Kính gửi Quý Phụ huynh, 
    Nhằm tạo sân chơi bổ ích cho học sinh, nhà trường tổ chức trại hè 'Vinschool Summer Camp'.
    Thời gian diễn ra: Từ 15/06 đến 30/06.
    Phụ huynh vui lòng đăng ký và hoàn thành học phí trước ngày 30/04/2026.
    Quý vị có thể đăng ký trực tiếp tại mục 'Hoạt động ngoại khóa' trên App Vinschool One.
    Mọi thắc mắc xin liên hệ phòng Tuyển sinh. Trân trọng.
    """
    notif = await agent.extract_actionable_notif(long_text)
    print(f"Summary:\n{notif}")

if __name__ == "__main__":
    asyncio.run(test_agent())
