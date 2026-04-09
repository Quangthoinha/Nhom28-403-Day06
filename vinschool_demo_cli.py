import asyncio
from services.vinschool_agent import get_vinschool_agent

async def main():
    agent = get_vinschool_agent()
    print("="*60)
    print("      VINSCHOOL ONE - AI ASSISTANT DEMO")
    print("="*60)
    
    while True:
        print("\nCHỌN TÍNH NĂNG:")
        print("1. Vin-Assistant (Chat tra cứu thông tin)")
        print("2. Smart Daily Brief (Bản tin 1 phút)")
        print("3. Actionable Notifications (Rút gọn thông báo)")
        print("0. Thoát")
        
        choice = input("\nNhập lựa chọn của bạn: ")
        
        if choice == '1':
            user_msg = input("Bạn muốn hỏi gì? (Ví dụ: 'Tuần này con có bài tập nào chưa làm?'): ")
            print("\n⏳ Đang xử lý...")
            response = await agent.chat_with_tools(user_msg)
            print(f"\n[Vin-Assistant]: {response}")
            
        elif choice == '2':
            date = input("Nhập ngày cần xem bản tin (DD/MM/YYYY, ví dụ 30/03/2026): ")
            print("\n⏳ Đang tổng hợp bản tin...")
            brief = await agent.get_daily_brief(date)
            print(f"\n--- BẢN TIN NGÀY {date} ---")
            print(brief)
            
        elif choice == '3':
            print("\nDán nội dung thông báo dài vào đây (Gõ 'DONE' ở dòng cuối để kết thúc):")
            lines = []
            while True:
                line = input()
                if line.strip().upper() == 'DONE':
                    break
                lines.append(line)
            announcement = "\n".join(lines)
            
            print("\n⏳ Đang trích xuất thông tin quan trọng...")
            summary = await agent.extract_actionable_notif(announcement)
            print("\n--- THÔNG TIN RÚT GỌN ---")
            print(summary)
            
        elif choice == '0':
            print("Cảm ơn Quý phụ huynh đã sử dụng dịch vụ!")
            break
        else:
            print("Lựa chọn không hợp lệ.")

if __name__ == "__main__":
    asyncio.run(main())
