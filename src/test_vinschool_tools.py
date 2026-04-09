from services.vinschool_tools import get_vinschool_tools
import asyncio

async def test_tools():
    tools = get_vinschool_tools()
    
    print("=== Testing Student Profile ===")
    print(tools.get_student_profile("Nguyễn Hưng"))
    
    print("\n=== Testing Attendance (30/03/2026) ===")
    print(tools.get_attendance("30/03/2026"))
    
    print("\n=== Testing Homework (Chưa làm) ===")
    print(tools.get_homework(status="Chưa làm"))
    
    print("\n=== Testing Menu (16/03/2026) ===")
    print(tools.get_menu("16/03/2026"))
    
    print("\n=== Testing Tuition ===")
    print(tools.get_tuition_info())
    
    print("\n=== Testing Teacher Comments ===")
    print(tools.get_teacher_comments())
    
    # print("\n=== Testing General Search ===")
    # print(tools.general_search("Quy định đồng phục"))

if __name__ == "__main__":
    asyncio.run(test_tools())
