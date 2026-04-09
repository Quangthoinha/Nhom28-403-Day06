import csv
import json
import os

csv_path = r"d:\Vínchool_agent_and_tools\data\AI20K_VinSchoolOne_Mockdata - Thông báo.csv"
json_path = r"d:\Vínchool_agent_and_tools\data\rag_data.json"

if not os.path.exists(csv_path):
    print(f"Error: CSV not found at {csv_path}")
    exit(1)

new_chunks = []
with open(csv_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        content = f"Dữ liệu từ bảng: Thông báo\n"
        content += f"- Loại thông báo: {row['Loại thông báo']}\n"
        content += f"- Tiêu đề: {row['Tiêu đề']}\n"
        content += f"- Nội dung tóm tắt: {row['Nội dung tóm tắt']}\n"
        content += f"- Đối tượng nhận: {row['Đối tượng nhận']}\n"
        content += f"- Ngày sự kiện: {row['Ngày sự kiện']}\n"
        content += f"- Hạn chót (Deadline): {row['Hạn chót (Deadline)']}\n"
        content += f"- Trạng thái: {row['Trạng thái hiển thị nút']}"
        
        chunk = {
            "id": f"Thông báo_{i}",
            "content": content,
            "metadata": {
                "sheet": "Thông báo",
                "row": i
            }
        }
        new_chunks.append(chunk)

if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    
    # Remove old notifications to prevent duplicates if re-running
    existing_data = [c for c in existing_data if c.get("metadata", {}).get("sheet") != "Thông báo"]
    existing_data.extend(new_chunks)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    print(f"Successfully added {len(new_chunks)} notification chunks to {json_path}")
else:
    print(f"Error: {json_path} not found")
