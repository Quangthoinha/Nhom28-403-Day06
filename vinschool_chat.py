import asyncio
import sys
import os

# Add the current directory to sys.path so that we can import from services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.vinschool_agent import get_vinschool_agent

async def start_chat():
    # Initialize Agent
    try:
        agent = get_vinschool_agent()
    except Exception as e:
        print(f"❌ Không thể khởi tạo Agent: {e}")
        return
    
    print("\n" + "="*50)
    print("   HỆ THỐNG TRỢ LÝ ẢO VINSCHOOL - CHAT TERMINAL")
    print("="*50)
    print("(Gõ 'exit', 'quit' hoặc 'thoát' để dừng cuộc trò chuyện)\n")

    while True:
        try:
            # Get user input
            user_input = input("👤 Bạn: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit', 'thoát', 'tạm biệt']:
                print("\n👋 Vin-Assistant: Tạm biệt Quý phụ huynh! Chúc một ngày tốt lành.")
                break

            print("⏳ Đang xử lý...\r", end="")
            
            # Call Agent to process input
            response = await agent.chat_with_tools(user_input)
            
            # Display response
            print("-" * 30)
            print(f"🤖 Vin-Assistant: \n{response}")
            print("-" * 30 + "\n")

        except KeyboardInterrupt:
            print("\n👋 Tạm biệt!")
            break
        except Exception as e:
            print(f"\n❌ Có lỗi xảy ra trong quá trình xử lý: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(start_chat())
    except (EOFError, KeyboardInterrupt):
        pass
