import os
import sys
import argparse
import time
import pyperclip
from dotenv import load_dotenv
import pyautogui  # 用于模拟键盘输入，直接输出到光标位置
import openai  # 导入OpenAI库
import keyboard  # 用于监听快捷键

# 加载环境变量
load_dotenv()

# 设置OpenAI API密钥
openai_api_key = ""
if not openai_api_key:
    print("错误: 未找到OpenAI API密钥。请设置OPENAI_API_KEY环境变量。")
    sys.exit(1)

# 创建OpenAI客户端
client = openai.OpenAI(api_key=openai_api_key)

def correct_text(text, model="gpt-4o"):
    """使用OpenAI API修正文本语法"""
    try:
        # 可用模型列表
        available_models = [
            "gpt-4o",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo"
        ]
        
        # 默认使用gpt-3.5-turbo
        default_model = "gpt-3.5-turbo"
        
        # 如果指定的模型不在可用列表中，使用默认模型
        if model not in available_models:
            print(f"警告: 指定的模型 '{model}' 不可用，使用默认模型 '{default_model}'")
            model = default_model
        
        # 创建提示
        system_prompt = "你是一位专业的语法修正助手，只返回修正后的文本，不添加任何解释。"
        user_prompt = "请修正以下文本的语法，但保持原意和风格。只返回修正后的文本，不要加任何解释或注释:\n\n" + text
        
        # 发送请求到OpenAI API
        response = client.chat.completions.create(
            model=model,
            temperature=0.3,  # 低温度使输出更可预测
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # 获取回复内容
        corrected_text = response.choices[0].message.content.strip()
        
        return corrected_text
    
    except Exception as e:
        print(f"错误: 与OpenAI API通信时出现问题: {e}")
        # 提供更详细的错误信息
        if hasattr(e, 'status_code'):
            print(f"状态码: {e.status_code}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"响应: {e.response.text}")
        return None

def type_text_at_cursor(text):
    """将文本直接输出到当前光标位置"""
    
    # 直接模拟键盘输入文本（较慢但安全的方法）
    pyautogui.write(text)

def process_selected_text(model="gpt-4o"):
    """处理当前选中的文本并替换"""
    print("快捷键触发，开始处理选中文本...")
    
    # 复制当前选中的文本 (Command+C)
    pyautogui.hotkey('command', 'c')
    # 等待片刻，确保复制操作完成
    time.sleep(0.2)
    
    # 获取剪贴板内容
    selected_text = pyperclip.paste()
    if not selected_text:
        print("未选中文本或剪贴板为空")
        return
    
    print(f"获取到选中文本 ({len(selected_text)} 字符)，正在处理...")
    corrected_text = correct_text(selected_text, model)
    
    if corrected_text:
        # 将修正后的文本存入剪贴板
        pyperclip.copy(corrected_text)
        
        # 粘贴修正后的文本 (Command+V)
        pyautogui.hotkey('command', 'v')
        print("文本已修正并替换原文本")
    else:
        print("无法完成文本修正")

def start_hotkey_listener(model="gpt-4o"):
    """启动快捷键监听器"""
    print(f"启动快捷键监听 - Command+U 将触发文本语法修正 (使用模型: {model})")
    
    # 注册 Command+U 快捷键
    keyboard.add_hotkey('command+u', lambda: process_selected_text(model))
    
    # 持续监听快捷键直到程序终止
    print("快捷键监听已启动。按 Ctrl+C 终止程序。")
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("\n程序已终止")

def main():
    parser = argparse.ArgumentParser(description='使用OpenAI API修正文本语法')
    parser.add_argument('--text', help='要修正的文本')
    parser.add_argument('--model', default='gpt-4o', help='要使用的OpenAI模型(默认: gpt-4o)')
    parser.add_argument('--clipboard', action='store_true', help='从剪贴板读取文本')
    parser.add_argument('--cursor', action='store_true', help='直接在光标位置输出结果')
    parser.add_argument('--hotkey', action='store_true', help='启动快捷键监听模式 (Command+U)')
    
    args = parser.parse_args()
    
    # 启动快捷键监听模式
    if args.hotkey:
        start_hotkey_listener(args.model)
        return
    
    # 从剪贴板或命令行参数获取文本
    if args.clipboard:
        text = pyperclip.paste()
        if not text:
            print("错误: 剪贴板为空")
            return
    elif args.text:
        text = args.text
    else:
        print("错误: 请提供文本(使用--text参数)或使用--clipboard从剪贴板读取")
        return
    
    print("正在处理文本...")
    corrected_text = correct_text(text, args.model)
    
    if corrected_text:
        # 输出结果
        if args.cursor:
            # 直接在光标位置输出
            type_text_at_cursor(corrected_text)
            # print("文本已输出到光标位置")
        elif args.clipboard:
            pyperclip.copy(corrected_text)
            # print("已修正的文本已复制到剪贴板")
        else:
            print("\n修正后的文本:")
            print("="*50)
            print(corrected_text)
            print("="*50)

if __name__ == "__main__":
    main()
