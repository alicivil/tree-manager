import os
from datetime import datetime
import re

def generate_tree(root_dir, prefix=""):
    """ایجاد نمایش درختی از پوشه"""
    tree_str = ""
    entries = sorted(os.listdir(root_dir))
    entries = [e for e in entries if not e.startswith('.')]
    
    for index, entry in enumerate(entries):
        full_path = os.path.join(root_dir, entry)
        connector = "├── " if index < len(entries) - 1 else "└── "
        
        if os.path.isdir(full_path):
            tree_str += f"{prefix}{connector}{entry}/\n"
            tree_str += generate_tree(
                full_path,
                prefix + "│   " if index < len(entries) - 1 else prefix + "    "
            )
        else:
            tree_str += f"{prefix}{connector}{entry}\n"
            
    return tree_str

def clean_path_for_filename(path):
    """تبدیل مسیر به نام فایل مناسب و خوانا"""
    # گرفتن نام آخرین پوشه از مسیر
    folder_name = os.path.basename(path.rstrip(os.sep))
    
    # اگر مسیر ریشه باشد (مثل C:\ یا D:\)
    if not folder_name:
        folder_name = os.path.splitdrive(path)[0].rstrip(':') or 'root'
    
    # حذف کاراکترهای غیرمجاز در نام فایل
    folder_name = re.sub(r'[\\/:"*?<>|]', '_', folder_name)
    
    return folder_name

def save_tree_to_file(tree, base_path):
    """ذخیره ساختار درختی در فایل با نام هوشمند"""
    # مسیر فعلی که اسکریپت در آن قرار دارد
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # ایجاد پوشه save در کنار اسکریپت
    save_dir = os.path.join(current_dir, "save")
    os.makedirs(save_dir, exist_ok=True)
    
    # ایجاد نام فایل ترکیبی از نام پوشه و تاریخ
    clean_name = clean_path_for_filename(base_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tree_{clean_name}_{timestamp}.txt"
    
    # مسیر کامل فایل در پوشه save
    file_path = os.path.join(save_dir, filename)
    
    # اضافه کردن اطلاعات مفید به ابتدای فایل
    header = f"""{'='*50}
گزارش ساختار درختی
مسیر: {base_path}
تاریخ ایجاد: {datetime.now().strftime("%Y/%m/%d %H:%M:%S")}
{'='*50}

"""
    
    # ذخیره درخت در فایل
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(header + tree)
    
    return file_path

def create_structure(base_path, structure):
    """ایجاد ساختار پوشه"""
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, 'w') as f:
                f.write(content)

def parse_tree_file(tree_content):
    """تبدیل محتوای فایل tree به دیکشنری ساختار"""
    structure = {}
    current_path = []
    
    # حذف هدر فایل (هر چیزی قبل از اولین خط درختی)
    lines = tree_content.splitlines()
    for i, line in enumerate(lines):
        if '──' in line:
            lines = lines[i:]
            break
    
    for line in lines:
        if not line.strip() or '=' in line or 'مسیر:' in line or 'تاریخ:' in line:
            continue
            
        # حذف کاراکترهای درختی و فضای خالی
        clean_line = line.replace('├──', '').replace('└──', '').replace('│', '').strip()
        # محاسبه عمق بر اساس تعداد فضای خالی
        depth = (len(line) - len(line.lstrip())) // 4
        
        # تنظیم current_path برای عمق فعلی
        current_path = current_path[:depth]
        
        is_dir = clean_line.endswith('/')
        name = clean_line.rstrip('/')
        
        if not name:  # اگر خط خالی بود
            continue
            
        # ایجاد مسیر در ساختار
        current_dict = structure
        for path_part in current_path:
            current_dict = current_dict[path_part]
            
        if is_dir:
            current_dict[name] = {}
            current_path.append(name)
        else:
            current_dict[name] = ""
            
    return structure

def main():
    print("\n=== مدیریت پوشه‌ها ===")
    print("1. نمایش و ذخیره ساختار درختی")
    print("2. ایجاد ساختار پوشه از فایل tree")
    print("3. خروج")
    
    while True:
        choice = input("\nلطفاً گزینه مورد نظر را انتخاب کنید (1-3): ").strip()
        
        if not choice.isdigit() or choice not in ['1', '2', '3']:
            print("خطا: لطفاً یک عدد بین 1 تا 3 وارد کنید!")
            continue
            
        if choice == "3":
            print("خدانگهدار!")
            break
            
        if choice == "2":
            target_path = input("لطفاً مسیر پوشه هدف را وارد کنید: ").strip()
            if not os.path.exists(target_path):
                create = input("این مسیر وجود ندارد. آیا ایجاد شود؟ (y/n): ").strip().lower()
                if create != 'y':
                    continue
                os.makedirs(target_path)
                
            tree_file = input("لطفاً مسیر فایل tree را وارد کنید: ").strip()
            if not os.path.exists(tree_file):
                print("خطا: فایل tree یافت نشد!")
                continue
                
            try:
                # خواندن محتوای فایل tree
                with open(tree_file, 'r', encoding='utf-8') as f:
                    tree_content = f.read()
                
                # تبدیل tree به ساختار
                structure = parse_tree_file(tree_content)
                
                if not structure:
                    print("خطا: ساختار درختی معتبری در فایل یافت نشد!")
                    continue
                
                # ایجاد ساختار
                create_structure(target_path, structure)
                print("\nساختار با موفقیت ایجاد شد!")
                
                # نمایش ساختار ایجاد شده
                print("\nساختار ایجاد شده:")
                print(generate_tree(target_path))
                
                print("\nعملیات با موفقیت به پایان رسید.")
                print("برنامه در حال خروج...")
                break  # خروج از حلقه اصلی
                
            except Exception as e:
                print(f"خطا در ایجاد ساختار: {str(e)}")
                continue

if __name__ == "__main__":
    main() 
