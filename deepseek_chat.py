#!/usr/bin/env python3
"""
DeepSeek Agent for Kali Linux - С анализом вывода утилит
"""

import openai
import subprocess
import json
import re
import os
import sys
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# ============================================================
# НАСТРОЙКИ
# ============================================================

MODEL_NAME = "deepseek/deepseek-v4-flash"
MAX_ITERATIONS = 15
TEMPERATURE = 0.3
USE_SEPARATE_WINDOWS = False  # False - вывод в консоль, чтобы агент видел результат

SYSTEM_PROMPT = """Ты - DeepSeek Agent для Kali Linux. Твоя задача - запускать утилиты и АНАЛИЗИРОВАТЬ их вывод.

## ВАЖНО: После каждого запуска утилиты ты ДОЛЖЕН проанализировать её вывод и дать отчёт!

## ФОРМАТ ОТВЕТА ПОСЛЕ SQLMAP:
═══════════════════════════════════════════════════════════════
📊 **ОТЧЁТ SQLMAP**
═══════════════════════════════════════════════════════════════

🔍 **СТАТУС:** [НАЙДЕНО / НЕ НАЙДЕНО]

🗄️ **БАЗЫ ДАННЫХ:**
- [список найденных БД]

📋 **ТАБЛИЦЫ (если найдены):**
- [список таблиц]

⚠️ **УЯЗВИМОСТИ:**
- [тип уязвимости]

📊 **ВЫВОД:** [краткое заключение]

═══════════════════════════════════════════════════════════════

Будь внимателен при анализе вывода!"""

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
    
    ICON_AGENT = "🤖"
    ICON_USER = "👤"
    ICON_TOOL = "🔧"
    ICON_SUCCESS = "✅"
    ICON_ERROR = "❌"
    ICON_WARNING = "⚠️"
    ICON_INFO = "ℹ️"
    ICON_DB = "🗄️"
    ICON_TABLE = "📋"
    ICON_VULN = "⚠️"

# ============================================================
# ЗАГРУЗКА КЛЮЧА
# ============================================================

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print(f"{Colors.ICON_ERROR} {Colors.RED}API ключ не найден в .env{Colors.END}")
    print(f"{Colors.ICON_INFO} Создайте файл .env с: OPENROUTER_API_KEY=sk-or-v1-ваш_ключ")
    sys.exit(1)

# ============================================================
# ЗАПУСК КОМАНД С ЧТЕНИЕМ ВЫВОДА
# ============================================================

def run_command_with_output(command: str, timeout: int = 600) -> dict:
    """
    Запускает команду и ВОЗВРАЩАЕТ её вывод для анализа
    """
    print(f"\n{Colors.ICON_TOOL} {Colors.CYAN}Запуск:{Colors.END} {Colors.BOLD}{command}{Colors.END}")
    print(f"{Colors.DIM}{'─' * 70}{Colors.END}")
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Объединяем stdout и stderr
            text=True,
            bufsize=1,
            universal_newlines=True,
            executable='/bin/bash' if sys.platform != 'win32' else None
        )
        
        output_lines = []
        
        # Читаем вывод в реальном времени
        for line in iter(process.stdout.readline, ''):
            if line:
                output_lines.append(line.rstrip())
                # Показываем вывод пользователю
                if 'sqlmap' in command.lower():
                    # Подсветка для sqlmap
                    if 'vulnerable' in line.lower() or 'injectable' in line.lower():
                        print(f"{Colors.GREEN}{line.rstrip()}{Colors.END}")
                    elif 'error' in line.lower() or 'failed' in line.lower():
                        print(f"{Colors.RED}{line.rstrip()}{Colors.END}")
                    elif 'database' in line.lower() or 'table' in line.lower():
                        print(f"{Colors.CYAN}{line.rstrip()}{Colors.END}")
                    else:
                        print(f"{Colors.DIM}{line.rstrip()}{Colors.END}")
                else:
                    print(line.rstrip())
        
        process.wait(timeout=timeout)
        
        return {
            "success": process.returncode == 0,
            "output": "\n".join(output_lines),
            "return_code": process.returncode
        }
        
    except subprocess.TimeoutExpired:
        process.terminate()
        return {"success": False, "output": "\n".join(output_lines), "error": "Timeout"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

# ============================================================
# АНАЛИЗ ВЫВОДА SQLMAP
# ============================================================

def analyze_sqlmap_output(output: str) -> dict:
    """
    ДЕТАЛЬНЫЙ анализ вывода sqlmap
    Извлекает: найденные БД, таблицы, уязвимости, текущего пользователя
    """
    
    analysis = {
        "vulnerable": False,
        "vulnerability_type": [],
        "databases": [],
        "tables": [],
        "current_user": None,
        "current_database": None,
        "technique": [],
        "payloads": [],
        "summary": ""
    }
    
    output_lower = output.lower()
    
    # 1. Проверка на наличие уязвимости
    if "vulnerable" in output_lower or "injectable" in output_lower:
        analysis["vulnerable"] = True
        
        # Определяем тип уязвимости
        if "boolean-based blind" in output_lower:
            analysis["vulnerability_type"].append("Boolean-based Blind SQLi")
        if "time-based blind" in output_lower:
            analysis["vulnerability_type"].append("Time-based Blind SQLi")
        if "error-based" in output_lower:
            analysis["vulnerability_type"].append("Error-based SQLi")
        if "union" in output_lower:
            analysis["vulnerability_type"].append("Union-based SQLi")
        if "stacked queries" in output_lower:
            analysis["vulnerability_type"].append("Stacked Queries")
    
    # 2. Поиск баз данных (разные форматы вывода sqlmap)
    # Формат: [*] database_name
    db_pattern1 = r'\[\*\*\]\s+(\w+)'
    dbs1 = re.findall(db_pattern1, output)
    
    # Формат: [[ ]] database_name
    db_pattern2 = r'\[\[\s*\]\]\s+(\w+)'
    dbs2 = re.findall(db_pattern2, output)
    
    # Формат: | database_name |
    db_pattern3 = r'\|\s+(\w+)\s+\|'
    dbs3 = re.findall(db_pattern3, output)
    
    all_dbs = list(set(dbs1 + dbs2 + dbs3))
    # Фильтруем системные БД
    system_dbs = ['information_schema', 'mysql', 'performance_schema', 'sys']
    analysis["databases"] = [db for db in all_dbs if db not in system_dbs]
    
    # 3. Поиск таблиц
    table_pattern = r'\|\s+(\w+)\s+\|'
    all_tables = re.findall(table_pattern, output)
    # Фильтруем дубликаты
    analysis["tables"] = list(set(all_tables))[:50]
    
    # 4. Поиск текущего пользователя
    user_patterns = [
        r'current user:\s*[\'"]?(\w+)[\'"]?',
        r'\[current user:\s*(\w+)\]',
        r'user:\s*(\w+)'
    ]
    for pattern in user_patterns:
        match = re.search(pattern, output_lower)
        if match:
            analysis["current_user"] = match.group(1)
            break
    
    # 5. Поиск текущей БД
    db_patterns = [
        r'current database:\s*[\'"]?(\w+)[\'"]?',
        r'\[current database:\s*(\w+)\]',
        r'database:\s*(\w+)'
    ]
    for pattern in db_patterns:
        match = re.search(pattern, output_lower)
        if match:
            analysis["current_database"] = match.group(1)
            break
    
    # 6. Поиск использованных техник
    techniques = {
        "B": "Boolean-based blind",
        "T": "Time-based blind",
        "E": "Error-based",
        "U": "Union query",
        "S": "Stacked queries"
    }
    tech_pattern = r'technique:\s*([BTEUS]+)'
    tech_match = re.search(tech_pattern, output)
    if tech_match:
        for tech in tech_match.group(1):
            if tech in techniques:
                analysis["technique"].append(techniques[tech])
    
    # 7. Поиск примеров payload'ов
    payload_pattern = r'Payload:\s*(.+?)(?:\n|$)'
    payloads = re.findall(payload_pattern, output, re.IGNORECASE)
    analysis["payloads"] = payloads[:5]  # Показываем максимум 5
    
    # 8. Формируем краткое резюме
    if analysis["vulnerable"]:
        analysis["summary"] = f"🔴 ОБНАРУЖЕНА SQL-ИНЪЕКЦИЯ! Тип: {', '.join(analysis['vulnerability_type'])}"
        if analysis["databases"]:
            analysis["summary"] += f" | Найдено БД: {len(analysis['databases'])}"
        if analysis["tables"]:
            analysis["summary"] += f" | Найдено таблиц: {len(analysis['tables'])}"
    else:
        analysis["summary"] = "🟢 SQL-инъекция НЕ обнаружена"
    
    return analysis

def print_sqlmap_report(analysis: dict):
    """Красиво выводит отчёт по sqlmap"""
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}📊 ОТЧЁТ SQLMAP{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════════════════{Colors.END}")
    
    # Статус
    if analysis["vulnerable"]:
        print(f"\n{Colors.ICON_VULN} {Colors.RED}{Colors.BOLD}СТАТУС: SQL-ИНЪЕКЦИЯ НАЙДЕНА!{Colors.END}")
    else:
        print(f"\n{Colors.ICON_SUCCESS} {Colors.GREEN}{Colors.BOLD}СТАТУС: SQL-инъекция не найдена{Colors.END}")
    
    # Типы уязвимостей
    if analysis["vulnerability_type"]:
        print(f"\n{Colors.ICON_VULN} {Colors.YELLOW}ТИПЫ УЯЗВИМОСТЕЙ:{Colors.END}")
        for vuln in analysis["vulnerability_type"]:
            print(f"   • {vuln}")
    
    # Базы данных
    if analysis["databases"]:
        print(f"\n{Colors.ICON_DB} {Colors.GREEN}НАЙДЕННЫЕ БАЗЫ ДАННЫХ:{Colors.END}")
        for db in analysis["databases"][:20]:
            print(f"   • {db}")
        if len(analysis["databases"]) > 20:
            print(f"   • ... и ещё {len(analysis['databases']) - 20} БД")
    else:
        if analysis["vulnerable"]:
            print(f"\n{Colors.ICON_INFO} {Colors.YELLOW}БАЗЫ ДАННЫХ: не удалось извлечь (попробуйте --dbs){Colors.END}")
        else:
            print(f"\n{Colors.ICON_INFO} БАЗЫ ДАННЫХ: не найдены (уязвимость отсутствует)")
    
    # Таблицы
    if analysis["tables"]:
        print(f"\n{Colors.ICON_TABLE} {Colors.GREEN}НАЙДЕННЫЕ ТАБЛИЦЫ (первые 20):{Colors.END}")
        for table in analysis["tables"][:20]:
            print(f"   • {table}")
    
    # Информация о пользователе/БД
    if analysis["current_user"]:
        print(f"\n{Colors.ICON_INFO} {Colors.CYAN}ТЕКУЩИЙ ПОЛЬЗОВАТЕЛЬ БД:{Colors.END} {analysis['current_user']}")
    if analysis["current_database"]:
        print(f"{Colors.ICON_INFO} {Colors.CYAN}ТЕКУЩАЯ БАЗА ДАННЫХ:{Colors.END} {analysis['current_database']}")
    
    # Использованные техники
    if analysis["technique"]:
        print(f"\n{Colors.ICON_TOOL} {Colors.CYAN}ИСПОЛЬЗОВАННЫЕ ТЕХНИКИ:{Colors.END}")
        for tech in analysis["technique"]:
            print(f"   • {tech}")
    
    # Примеры payload'ов
    if analysis["payloads"]:
        print(f"\n{Colors.ICON_INFO} {Colors.DIM}ПРИМЕРЫ PAYLOAD'ОВ:{Colors.END}")
        for payload in analysis["payloads"][:3]:
            print(f"   {Colors.DIM}→ {payload[:80]}{Colors.END}")
    
    # Итог
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.BOLD}📊 {analysis['summary']}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════════════════{Colors.END}\n")

# ============================================================
# ДРУГИЕ УТИЛИТЫ
# ============================================================

def run_sqlmap_with_analysis(url: str, flags: str = "--batch --dbs") -> dict:
    """
    Запускает sqlmap и ВОЗВРАЩАЕТ анализ результата
    """
    command = f"sqlmap -u '{url}' {flags}"
    result = run_command_with_output(command, timeout=1200)
    
    if result["success"] and result["output"]:
        # Анализируем вывод
        analysis = analyze_sqlmap_output(result["output"])
        # Выводим красивый отчёт
        print_sqlmap_report(analysis)
        
        return {
            "success": True,
            "output": result["output"],
            "analysis": analysis
        }
    else:
        return {
            "success": False,
            "output": result.get("output", ""),
            "error": result.get("error", "Не удалось выполнить sqlmap"),
            "analysis": None
        }

def run_nmap(target: str, flags: str = "-sV") -> dict:
    command = f"nmap {flags} {target}"
    return run_command_with_output(command, timeout=600)

def run_gobuster(url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt") -> dict:
    command = f"gobuster dir -u {url} -w {wordlist}"
    return run_command_with_output(command, timeout=600)

# ============================================================
# ИНСТРУМЕНТЫ ДЛЯ API
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_sqlmap",
            "description": "Запускает sqlmap, АНАЛИЗИРУЕТ вывод и возвращает отчёт с найденными БД, таблицами, уязвимостями",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Целевой URL с параметром"},
                    "flags": {"type": "string", "description": "Дополнительные флаги", "default": "--batch --dbs"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_nmap",
            "description": "Запускает nmap сканирование",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {"type": "string"},
                    "flags": {"type": "string", "default": "-sV"}
                },
                "required": ["target"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_gobuster",
            "description": "Запускает gobuster для поиска директорий",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "wordlist": {"type": "string", "default": "/usr/share/wordlists/dirb/common.txt"}
                },
                "required": ["url"]
            }
        }
    }
]

def execute_tool(tool_name: str, parameters: dict) -> str:
    try:
        if tool_name == "run_sqlmap":
            result = run_sqlmap_with_analysis(
                parameters["url"],
                parameters.get("flags", "--batch --dbs")
            )
            return json.dumps({
                "success": result["success"],
                "summary": result.get("analysis", {}).get("summary", ""),
                "vulnerable": result.get("analysis", {}).get("vulnerable", False),
                "databases": result.get("analysis", {}).get("databases", []),
                "tables": result.get("analysis", {}).get("tables", [])[:20]
            }, ensure_ascii=False, indent=2)
        
        elif tool_name == "run_nmap":
            result = run_nmap(parameters["target"], parameters.get("flags", "-sV"))
            return json.dumps({"success": result["success"], "output": result["output"][:2000]}, ensure_ascii=False)
        
        elif tool_name == "run_gobuster":
            result = run_gobuster(parameters["url"], parameters.get("wordlist", "/usr/share/wordlists/dirb/common.txt"))
            return json.dumps({"success": result["success"], "output": result["output"][:2000]}, ensure_ascii=False)
        
        return f"Неизвестный инструмент: {tool_name}"
    except Exception as e:
        return json.dumps({"error": str(e), "success": False})

# ============================================================
# ОСНОВНОЙ КЛАСС АГЕНТА
# ============================================================

class DeepSeekAgent:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    def process(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=self.messages,
                tools=TOOLS,
                tool_choice="auto",
                stream=False,
                temperature=TEMPERATURE
            )
            
            assistant_message = response.choices[0].message
            self.messages.append(assistant_message)
            
            iteration = 0
            while assistant_message.tool_calls and iteration < MAX_ITERATIONS:
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    parameters = json.loads(tool_call.function.arguments)
                    print(f"\n{Colors.ICON_TOOL} {Colors.PURPLE}Запуск:{Colors.END} {Colors.BOLD}{tool_name}{Colors.END}")
                    result = execute_tool(tool_name, parameters)
                    
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                
                response = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=self.messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    stream=False,
                    temperature=TEMPERATURE
                )
                
                assistant_message = response.choices[0].message
                self.messages.append(assistant_message)
                iteration += 1
            
            return assistant_message.content or "Готово!"
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    def clear(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# ============================================================
# ЗАПУСК
# ============================================================

def print_banner():
    os.system('clear' if sys.platform != 'win32' else 'cls')
    print(f"""{Colors.BOLD}{Colors.CYAN}
╔═══════════════════════════════════════════════════════════════════════════╗
║                    🤖 DEEPSEEK AGENT - АНАЛИЗАТОР 🤖                       ║
║                    📊 Автоматический анализ вывода утилит 📊               ║
╚═══════════════════════════════════════════════════════════════════════════╝{Colors.END}
    """)
    print(f"{Colors.ICON_INFO} Агент анализирует вывод sqlmap и показывает:")
    print(f"   • Найдены ли SQL-инъекции")
    print(f"   • Какие базы данных обнаружены")
    print(f"   • Какие таблицы найдены")
    print(f"   • Типы уязвимостей")
    print()

def main():
    print_banner()
    agent = DeepSeekAgent()
    
    print(f"{Colors.ICON_AGENT} {Colors.GREEN}Агент запущен!{Colors.END}")
    print(f"{Colors.ICON_INFO} Просто скажите: {Colors.YELLOW}запусти sqlmap на http://testphp.vulnweb.com/artists.php?artist=1{Colors.END}")
    print(f"{Colors.ICON_INFO} Для выхода введите: exit\n")
    
    while True:
        try:
            user_input = input(f"{Colors.BOLD}{Colors.GREEN}┌─[{Colors.ICON_USER}]{Colors.END} ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}До свидания!{Colors.END}\n")
                break
            
            if user_input.lower() == '/clear':
                agent.clear()
                os.system('clear' if sys.platform != 'win32' else 'cls')
                print_banner()
                continue
            
            if not user_input:
                continue
            
            print(f"\n{Colors.ICON_AGENT} {Colors.BLUE}Обработка...{Colors.END}")
            response = agent.process(user_input)
            
            print(f"\n{Colors.BOLD}{Colors.GREEN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
            print(f"{Colors.BOLD}{Colors.GREEN}│ {Colors.ICON_AGENT} ОТВЕТ:{Colors.END}")
            print(f"{Colors.BOLD}{Colors.GREEN}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
            for line in response.split('\n'):
                if line.strip():
                    print(f"{Colors.DIM}│{Colors.END} {line}")
            print(f"{Colors.BOLD}{Colors.GREEN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.ICON_WARNING} {Colors.YELLOW}Прервано{Colors.END}")
            continue

if __name__ == "__main__":
    main()