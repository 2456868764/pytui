# 诊断脚本 - 找出为什么没有反应

import sys
import select
import termios
import tty

print("=== 输入诊断工具 ===")
print("请按任意键，程序会显示收到的字节...")
print("按 Ctrl+C 退出")
print()

# 保存原始终端设置
fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)

try:
    # 设置为 raw 模式
    tty.setraw(fd)
    
    while True:
        # 检查是否有输入
        ready = select.select([sys.stdin], [], [], 0.1)[0]
        
        if ready:
            # 读取所有可用字节
            chunk = b""
            while True:
                try:
                    part = sys.stdin.buffer.read(1)
                    if not part:
                        break
                    chunk += part
                    
                    # 检查是否还有更多
                    ready2 = select.select([sys.stdin], [], [], 0)[0]
                    if not ready2:
                        break
                except (BlockingIOError, InterruptedError):
                    break
            
            if chunk:
                # 显示收到的字节
                print(f"\r\n收到 {len(chunk)} 字节: {chunk!r}", end="")
                
                # 尝试解码
                try:
                    decoded = chunk.decode('utf-8')
                    print(f" → 解码: {decoded!r}", end="")
                except:
                    print(f" → 解码失败", end="")
                
                print()
                sys.stdout.flush()
                
                # 检查是否是 Ctrl+C
                if chunk == b'\x03':
                    break
                    
finally:
    # 恢复终端设置
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    print("\n\n程序退出")