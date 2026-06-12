#!/usr/bin/env python3
"""
Jim - Умный ИИ-агент для пентеста
Сам анализирует цель и решает, какие утилиты запускать
Промпт загружается из system_prompt.txt
"""

import sys
import os
import subprocess
import json
import re
import shutil
from datetime import datetime

# ============================================================
# ОБРАБОТКА АРГУМЕНТОВ
# ============================================================

VERSION = "2.0.0"

def update_jim():
    print("🔄 Обновление Jim...")
    jim_dir = os.path.expanduser("~/.jim")
    repo_url = "https://github.com/Lolicks/hackagent.git"
    temp_dir = "/tmp/jim-update"
    
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        subprocess.run(["git", "clone", "--depth", "1", repo_url, temp_dir], check=True, capture_output=True)
        shutil.copy2(f"{temp_dir}/jim.py", f"{jim_dir}/jim.py")
        shutil.copy2(f"{temp_dir}/system_prompt.txt", f"{jim_dir}/")
        shutil.rmtree(temp_dir)
        print("✅ Обновление завершено!")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if len(sys.argv) > 1:
    if sys.argv[1] in ["-v", "--version"]:
        print(f"Jim v{VERSION}")
        sys.exit(0)
    elif sys.argv[1] in ["-h", "--help"]:
        print("""
Jim - Умный помощник для пентеста

Использование:
    jim              - Запустить агента
    jim -h           - Справка
    jim -u           - Обновить
""")
        sys.exit(0)
    elif sys.argv[1] in ["-u", "--update"]:
        sys.exit(0 if update_jim() else 1)

# ============================================================
# ЦВЕТА
# ============================================================

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'
    
    # Иконки
    ICON_AGENT = "🐍"
    ICON_USER = "👤"
    ICON_TOOL = "🔧"
    ICON_ANALYSIS = "🔍"
    ICON_DECISION = "🎯"
    ICON_REPORT = "📊"
    ICON_INFO = "ℹ️"
    ICON_SUCCESS = "✅"
    ICON_ERROR = "❌"
    ICON_WARNING = "⚠️"

# ============================================================
# ЗАГРУЗКА НАСТРОЕК
# ============================================================

def load_api_key():
    env_path = os.path.expanduser("~/.jim/.env")
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return None

def load_system_prompt():
    # Сначала ищем в локальной папке (для разработки)
    if os.path.exists("system_prompt.txt"):
        with open("system_prompt.txt", 'r', encoding='utf-8') as f:
            return f.read()
    # Потом в ~/.jim
    prompt_path = os.path.expanduser("~/.jim/system_prompt.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    return """Ты - Jim, умный помощник для пентеста. Будь полезным."""

API_KEY = load_api_key()
SYSTEM_PROMPT = load_system_prompt()

# ============================================================
# ЗАПУСК УТИЛИТ
# ============================================================

def run_command(cmd: str, timeout: int = 300):
    """Запускает команду и возвращает вывод"""
    print(f"{Colors.DIM}{'─' * 70}{Colors.END}")
    
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        output_lines = []
        for line in iter(process.stdout.readline, ''):
            if line:
                output_lines.append(line.rstrip())
                # Подсветка важного
                if 'vulnerable' in line.lower() or 'injectable' in line.lower():
                    print(f"{Colors.GREEN}{line.rstrip()}{Colors.END}")
                elif 'open' in line.lower() and 'tcp' in line.lower():
                    print(f"{Colors.GREEN}{line.rstrip()}{Colors.END}")
                elif 'error' in line.lower():
                    print(f"{Colors.RED}{line.rstrip()}{Colors.END}")
                elif 'database' in line.lower() or 'found' in line.lower():
                    print(f"{Colors.CYAN}{line.rstrip()}{Colors.END}")
                else:
                    print(line.rstrip())
        
        process.wait(timeout=timeout)
        return {"success": process.returncode == 0, "output": "\n".join(output_lines)}
    except subprocess.TimeoutExpired:
        process.terminate()
        return {"success": False, "output": "", "error": "Timeout"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

def run_nmap(target: str, flags: str = "-sV --open"):
    return run_command(f"nmap {flags} {target}", timeout=300)

def run_sqlmap(url: str, flags: str = "--batch --dbs --level=1"):
    return run_command(f"sqlmap -u '{url}' {flags}", timeout=600)

def run_gobuster(url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt"):
    return run_command(f"gobuster dir -u {url} -w {wordlist}", timeout=300)

def run_nikto(target: str):
    return run_command(f"nikto -h {target}", timeout=600)

def run_whatweb(target: str):
    return run_command(f"whatweb {target}", timeout=120)

# ============================================================
# АНАЛИЗ ВЫВОДА
# ============================================================

def analyze_output(tool: str, output: str):
    """Анализирует вывод утилиты и возвращает структурированный результат"""
    
    analysis = {"found": False, "summary": "", "details": []}
    
    if tool == "nmap":
        open_ports = re.findall(r'(\d+)/tcp\s+open\s+(\w+)', output)
        if open_ports:
            analysis["found"] = True
            analysis["summary"] = f"Найдено {len(open_ports)} открытых портов"
            for port, service in open_ports[:10]:
                analysis["details"].append(f"Порт {port}: {service}")
        else:
            analysis["summary"] = "Открытых портов не найдено"
    
    elif tool == "sqlmap":
        if "vulnerable" in output.lower() or "injectable" in output.lower():
            analysis["found"] = True
            analysis["summary"] = "Обнаружена SQL-инъекция!"
            if "boolean" in output.lower():
                analysis["details"].append("Тип: Boolean-based Blind")
            if "union" in output.lower():
                analysis["details"].append("Тип: Union-based")
            if "time" in output.lower():
                analysis["details"].append("Тип: Time-based")
            # Ищем базы данных
            dbs = re.findall(r'\[\*\*\]\s+(\w+)', output)
            if dbs:
                analysis["details"].append(f"Базы данных: {', '.join(dbs[:5])}")
        else:
            analysis["summary"] = "SQL-инъекция не обнаружена"
    
    elif tool == "gobuster":
        dirs = re.findall(r'/(\S+)\s+\(Status:\s+(\d+)\)', output)
        interesting = [d for d in dirs if d[1] in ["200", "301", "302"]]
        if interesting:
            analysis["found"] = True
            analysis["summary"] = f"Найдено {len(interesting)} интересных директорий"
            for path, status in interesting[:10]:
                analysis["details"].append(f"/{path} (Status: {status})")
        else:
            analysis["summary"] = "Интересных директорий не найдено"
    
    elif tool == "nikto":
        vulns = re.findall(r'\+ (.*?):', output)
        real_vulns = [v for v in vulns if any(x in v.lower() for x in ['vulnerable', 'cve', 'xss', 'sql'])]
        if real_vulns:
            analysis["found"] = True
            analysis["summary"] = f"Найдено {len(real_vulns)} потенциальных уязвимостей"
            for v in real_vulns[:5]:
                analysis["details"].append(v[:80])
        else:
            analysis["summary"] = "Уязвимостей не обнаружено"
    
    elif tool == "whatweb":
        techs = re.findall(r'\[(.*?)\]', output)
        if techs:
            analysis["found"] = True
            analysis["summary"] = "Определены технологии"
            for t in techs[:10]:
                if 'http' not in t.lower() and len(t) < 50:
                    analysis["details"].append(t)
        else:
            analysis["summary"] = "Технологии не определены"
    
    return analysis

# ============================================================
# ИНСТРУМЕНТЫ ДЛЯ API
# ============================================================

TOOLS = [
    {"type": "function", "function": {
        "name": "run_nmap",
        "description": "Сканирование портов. Используй первым при тестировании IP/домена",
        "parameters": {"type": "object", "properties": {"target": {"type": "string"}, "flags": {"type": "string", "default": "-sV --open"}}, "required": ["target"]}
    }},
    {"type": "function", "function": {
        "name": "run_sqlmap",
        "description": "Поиск SQL-инъекций. Используй ТОЛЬКО если в URL есть параметры (?id=1)",
        "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "flags": {"type": "string", "default": "--batch --dbs --level=1"}}, "required": ["url"]}
    }},
    {"type": "function", "function": {
        "name": "run_gobuster",
        "description": "Поиск директорий. Используй если нужно найти скрытые пути",
        "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "wordlist": {"type": "string", "default": "/usr/share/wordlists/dirb/common.txt"}}, "required": ["url"]}
    }},
    {"type": "function", "function": {
        "name": "run_nikto",
        "description": "Поиск веб-уязвимостей. Используй для общего сканирования сайта",
        "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}
    }},
    {"type": "function", "function": {
        "name": "run_whatweb",
        "description": "Определение технологий. Используй чтобы узнать CMS, сервер, фреймворки",
        "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}
    }},
    {"type": "function", "function": {
        "name": "analyze_output",
        "description": "Анализирует вывод утилиты и извлекает важную информацию",
        "parameters": {"type": "object", "properties": {"tool": {"type": "string"}, "output": {"type": "string"}}, "required": ["tool", "output"]}
    }}
]

def execute_tool(tool_name: str, params: dict) -> str:
    """Выполняет инструмент и возвращает результат"""
    
    if tool_name == "run_nmap":
        result = run_nmap(params["target"], params.get("flags", "-sV --open"))
        analysis = analyze_output("nmap", result["output"])
        return json.dumps({"success": result["success"], "output": result["output"][:3000], "analysis": analysis}, ensure_ascii=False)
    
    elif tool_name == "run_sqlmap":
        result = run_sqlmap(params["url"], params.get("flags", "--batch --dbs --level=1"))
        analysis = analyze_output("sqlmap", result["output"])
        return json.dumps({"success": result["success"], "output": result["output"][:3000], "analysis": analysis}, ensure_ascii=False)
    
    elif tool_name == "run_gobuster":
        result = run_gobuster(params["url"], params.get("wordlist", "/usr/share/wordlists/dirb/common.txt"))
        analysis = analyze_output("gobuster", result["output"])
        return json.dumps({"success": result["success"], "output": result["output"][:3000], "analysis": analysis}, ensure_ascii=False)
    
    elif tool_name == "run_nikto":
        result = run_nikto(params["target"])
        analysis = analyze_output("nikto", result["output"])
        return json.dumps({"success": result["success"], "output": result["output"][:3000], "analysis": analysis}, ensure_ascii=False)
    
    elif tool_name == "run_whatweb":
        result = run_whatweb(params["target"])
        analysis = analyze_output("whatweb", result["output"])
        return json.dumps({"success": result["success"], "output": result["output"][:3000], "analysis": analysis}, ensure_ascii=False)
    
    elif tool_name == "analyze_output":
        analysis = analyze_output(params["tool"], params["output"])
        return json.dumps(analysis, ensure_ascii=False)
    
    return json.dumps({"error": f"Неизвестный инструмент: {tool_name}"})

# ============================================================
# КЛАСС АГЕНТА
# ============================================================

class JimAgent:
    def __init__(self):
        if not API_KEY:
            print(f"{Colors.ICON_ERROR} {Colors.RED}API ключ не найден!{Colors.END}")
            print(f"{Colors.ICON_INFO} Запустите установку: ./install.sh{Colors.END}")
            sys.exit(1)
        
        import openai
        self.client = openai.OpenAI(
            api_key=API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    def process(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-v4-flash",
                messages=self.messages,
                tools=TOOLS,
                tool_choice="auto",
                stream=False,
                temperature=0.3
            )
            
            assistant = response.choices[0].message
            self.messages.append(assistant)
            
            iteration = 0
            while assistant.tool_calls and iteration < 10:
                for tool_call in assistant.tool_calls:
                    tool_name = tool_call.function.name
                    params = json.loads(tool_call.function.arguments)
                    
                    print(f"\n{Colors.ICON_TOOL} {Colors.PURPLE}Jim запускает:{Colors.END} {Colors.BOLD}{tool_name}{Colors.END}")
                    result = execute_tool(tool_name, params)
                    
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                
                response = self.client.chat.completions.create(
                    model="deepseek/deepseek-v4-flash",
                    messages=self.messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    stream=False,
                    temperature=0.3
                )
                
                assistant = response.choices[0].message
                self.messages.append(assistant)
                iteration += 1
            
            return assistant.content or "Готово!"
        except Exception as e:
            return f"Ошибка: {e}"
    
    def clear(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# ============================================================
# ЗАПУСК
# ============================================================

def print_banner():
    os.system('clear')
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                           ║")
    print("║                         🐍 JIM - УМНЫЙ АГЕНТ 🐍                            ║")
    print("║                   Анализирую → Решаю → Выполняю → Отчитываюсь             ║")
    print("║                                                                           ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")

def main():
    print_banner()
    print(f"{Colors.ICON_AGENT} {Colors.GREEN}Jim готов!{Colors.END}")
    print(f"{Colors.ICON_INFO} Промпт загружен{Colors.END}")
    print(f"{Colors.DIM}{'─' * 70}{Colors.END}")
    
    agent = JimAgent()
    
    while True:
        try:
            user_input = input(f"\n{Colors.BOLD}{Colors.GREEN}┌─[{Colors.ICON_USER}]{Colors.END} ").strip()
            
            if user_input.lower() in ['/exit', 'exit', 'quit']:
                print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}До свидания!{Colors.END}\n")
                break
            
            if user_input.lower() == '/clear':
                agent.clear()
                os.system('clear')
                print_banner()
                continue
            
            if not user_input:
                continue
            
            print(f"\n{Colors.ICON_ANALYSIS} {Colors.BLUE}Анализирую цель и принимаю решение...{Colors.END}")
            response = agent.process(user_input)
            
            if response:
                print(f"\n{Colors.BOLD}{Colors.GREEN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
                print(f"{Colors.BOLD}{Colors.GREEN}│ {Colors.ICON_AGENT} ОТВЕТ:{Colors.END}")
                print(f"{Colors.BOLD}{Colors.GREEN}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
                for line in response.split('\n'):
                    if line.strip():
                        print(f"{Colors.DIM}│{Colors.END} {line}")
                print(f"{Colors.BOLD}{Colors.GREEN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.ICON_WARNING} {Colors.YELLOW}Прервано{Colors.END}")
            continue

if __name__ == "__main__":
    main()