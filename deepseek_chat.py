#!/usr/bin/env python3
"""
DeepSeek Agent for Kali Linux - Анализ вывода ВСЕХ утилит
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

## ФОРМАТ ОТВЕТА ПОСЛЕ ЛЮБОЙ УТИЛИТЫ:
═══════════════════════════════════════════════════════════════
📊 **ОТЧЁТ [НАЗВАНИЕ УТИЛИТЫ]**
═══════════════════════════════════════════════════════════════

🔍 **СТАТУС:** [УСПЕШНО / ОШИБКА]

📋 **НАЙДЕННАЯ ИНФОРМАЦИЯ:**
- [список найденных данных]

⚠️ **УЯЗВИМОСТИ (если есть):**
- [список]

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
    ICON_PORT = "🔌"
    ICON_DIR = "📁"
    ICON_VULN = "⚠️"

# ============================================================
# ЗАГРУЗКА КЛЮЧА
# ============================================================

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print(f"{Colors.ICON_ERROR} {Colors.RED}API ключ не найден в .env{Colors.END}")
    sys.exit(1)

# ============================================================
# ЗАПУСК КОМАНД С ЧТЕНИЕМ ВЫВОДА
# ============================================================

def run_command_with_output(command: str, timeout: int = 600, show_output: bool = True) -> dict:
    """
    Запускает команду и ВОЗВРАЩАЕТ её вывод для анализа
    """
    if show_output:
        print(f"\n{Colors.ICON_TOOL} {Colors.CYAN}Запуск:{Colors.END} {Colors.BOLD}{command}{Colors.END}")
        print(f"{Colors.DIM}{'─' * 70}{Colors.END}")
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
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
                if show_output:
                    # Подсветка вывода в зависимости от команды
                    if 'sqlmap' in command.lower():
                        if 'vulnerable' in line.lower() or 'injectable' in line.lower():
                            print(f"{Colors.GREEN}{line.rstrip()}{Colors.END}")
                        elif 'database' in line.lower() or 'table' in line.lower():
                            print(f"{Colors.CYAN}{line.rstrip()}{Colors.END}")
                        elif 'error' in line.lower():
                            print(f"{Colors.RED}{line.rstrip()}{Colors.END}")
                        else:
                            print(f"{Colors.DIM}{line.rstrip()}{Colors.END}")
                    elif 'nmap' in command.lower():
                        if 'open' in line.lower():
                            print(f"{Colors.GREEN}{line.rstrip()}{Colors.END}")
                        elif 'closed' in line.lower() or 'filtered' in line.lower():
                            print(f"{Colors.YELLOW}{line.rstrip()}{Colors.END}")
                        else:
                            print(line.rstrip())
                    elif 'gobuster' in command.lower():
                        if 'status:200' in line.lower() or 'status:301' in line.lower():
                            print(f"{Colors.GREEN}{line.rstrip()}{Colors.END}")
                        elif 'status:403' in line.lower() or 'status:401' in line.lower():
                            print(f"{Colors.YELLOW}{line.rstrip()}{Colors.END}")
                        else:
                            print(line.rstrip())
                    elif 'nikto' in command.lower():
                        if 'vulnerable' in line.lower() or 'cve' in line.lower():
                            print(f"{Colors.RED}{line.rstrip()}{Colors.END}")
                        elif 'info' in line.lower():
                            print(f"{Colors.CYAN}{line.rstrip()}{Colors.END}")
                        else:
                            print(line.rstrip())
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
# АНАЛИЗ ВЫВОДА ВСЕХ УТИЛИТ
# ============================================================

def analyze_sqlmap_output(output: str) -> dict:
    """Анализирует вывод sqlmap"""
    analysis = {
        "tool": "sqlmap",
        "vulnerable": False,
        "vulnerability_type": [],
        "databases": [],
        "tables": [],
        "current_user": None,
        "summary": ""
    }
    
    output_lower = output.lower()
    
    if "vulnerable" in output_lower or "injectable" in output_lower:
        analysis["vulnerable"] = True
        if "boolean-based blind" in output_lower:
            analysis["vulnerability_type"].append("Boolean-based Blind SQLi")
        if "time-based blind" in output_lower:
            analysis["vulnerability_type"].append("Time-based Blind SQLi")
        if "error-based" in output_lower:
            analysis["vulnerability_type"].append("Error-based SQLi")
        if "union" in output_lower:
            analysis["vulnerability_type"].append("Union-based SQLi")
    
    # Поиск баз данных
    db_pattern1 = r'\[\*\*\]\s+(\w+)'
    db_pattern2 = r'\[\[\s*\]\]\s+(\w+)'
    db_pattern3 = r'\|\s+(\w+)\s+\|'
    all_dbs = list(set(re.findall(db_pattern1, output) + re.findall(db_pattern2, output) + re.findall(db_pattern3, output)))
    system_dbs = ['information_schema', 'mysql', 'performance_schema', 'sys']
    analysis["databases"] = [db for db in all_dbs if db not in system_dbs]
    
    # Поиск таблиц
    table_pattern = r'\|\s+(\w+)\s+\|'
    analysis["tables"] = list(set(re.findall(table_pattern, output)))[:30]
    
    # Поиск пользователя
    user_match = re.search(r'current user:\s*[\'"]?(\w+)[\'"]?', output_lower)
    if user_match:
        analysis["current_user"] = user_match.group(1)
    
    if analysis["vulnerable"]:
        analysis["summary"] = f"🔴 SQL-инъекция найдена! Типы: {', '.join(analysis['vulnerability_type'])}. БД: {len(analysis['databases'])}"
    else:
        analysis["summary"] = "🟢 SQL-инъекция не обнаружена"
    
    return analysis

def analyze_nmap_output(output: str) -> dict:
    """Анализирует вывод nmap"""
    analysis = {
        "tool": "nmap",
        "open_ports": [],
        "closed_ports": [],
        "filtered_ports": [],
        "os_guess": None,
        "host_status": "unknown",
        "summary": ""
    }
    
    # Парсим открытые порты
    port_pattern = r'(\d+)/tcp\s+open\s+(\w+)'
    for match in re.finditer(port_pattern, output):
        analysis["open_ports"].append({"port": match.group(1), "service": match.group(2)})
    
    # Парсим закрытые порты
    closed_pattern = r'(\d+)/tcp\s+closed\s+(\w+)'
    for match in re.finditer(closed_pattern, output):
        analysis["closed_ports"].append({"port": match.group(1), "service": match.group(2)})
    
    # Парсим filtered порты
    filtered_pattern = r'(\d+)/tcp\s+filtered\s+(\w+)'
    for match in re.finditer(filtered_pattern, output):
        analysis["filtered_ports"].append({"port": match.group(1), "service": match.group(2)})
    
    # Определяем статус хоста
    if "Host is up" in output:
        analysis["host_status"] = "up"
    elif "Host seems down" in output:
        analysis["host_status"] = "down"
    
    # Угадываем ОС
    os_pattern = r'OS guess:\s*(.+?)(?:\n|$)'
    os_match = re.search(os_pattern, output)
    if os_match:
        analysis["os_guess"] = os_match.group(1).strip()
    
    analysis["summary"] = f"Найдено {len(analysis['open_ports'])} открытых портов"
    return analysis

def analyze_gobuster_output(output: str) -> dict:
    """Анализирует вывод gobuster"""
    analysis = {
        "tool": "gobuster",
        "directories": [],
        "status_codes": {},
        "summary": ""
    }
    
    dir_pattern = r'/(\S+)\s+\(Status:\s+(\d+)\)'
    for match in re.finditer(dir_pattern, output):
        path = match.group(1)
        status = match.group(2)
        analysis["directories"].append({"path": path, "status": status})
        
        if status in analysis["status_codes"]:
            analysis["status_codes"][status] += 1
        else:
            analysis["status_codes"][status] = 1
    
    # Анализируем интересные находки
    interesting = []
    for d in analysis["directories"]:
        if d["status"] in ["200", "301", "302"]:
            interesting.append(d["path"])
    
    if interesting:
        analysis["summary"] = f"Найдено {len(analysis['directories'])} директорий. Интересные: {', '.join(interesting[:5])}"
    else:
        analysis["summary"] = f"Найдено {len(analysis['directories'])} директорий"
    
    return analysis

def analyze_nikto_output(output: str) -> dict:
    """Анализирует вывод nikto"""
    analysis = {
        "tool": "nikto",
        "vulnerabilities": [],
        "server_info": None,
        "interesting_paths": [],
        "summary": ""
    }
    
    # Ищем уязвимости
    vuln_pattern = r'\+ (.+?):\s*(.+?)(?:\n|$)'
    for match in re.finditer(vuln_pattern, output):
        title = match.group(1)
        detail = match.group(2)
        if any(keyword in title.lower() for keyword in ['vulnerable', 'cve', 'xss', 'sql', 'rce', 'injection']):
            analysis["vulnerabilities"].append({"type": title, "detail": detail[:100]})
        elif any(keyword in title.lower() for keyword in ['directory', 'file', 'path']):
            analysis["interesting_paths"].append(title)
    
    # Ищем информацию о сервере
    server_pattern = r'\+ Server:\s*(.+?)(?:\n|$)'
    server_match = re.search(server_pattern, output, re.IGNORECASE)
    if server_match:
        analysis["server_info"] = server_match.group(1).strip()
    
    analysis["summary"] = f"Найдено {len(analysis['vulnerabilities'])} уязвимостей, {len(analysis['interesting_paths'])} интересных путей"
    return analysis

def analyze_whatweb_output(output: str) -> dict:
    """Анализирует вывод whatweb"""
    analysis = {
        "tool": "whatweb",
        "technologies": [],
        "server": None,
        "cms": None,
        "summary": ""
    }
    
    # Извлекаем технологии
    tech_pattern = r'\[(.*?)\]'
    techs = re.findall(tech_pattern, output)
    for tech in techs:
        if 'http' not in tech.lower():
            analysis["technologies"].append(tech)
    
    # Ищем CMS
    cms_list = ['wordpress', 'joomla', 'drupal', 'magento', 'shopify', 'wix']
    for tech in analysis["technologies"]:
        if tech.lower() in cms_list:
            analysis["cms"] = tech
    
    # Ищем сервер
    server_pattern = r'Apache|Nginx|IIS|Lighttpd'
    server_match = re.search(server_pattern, output, re.IGNORECASE)
    if server_match:
        analysis["server"] = server_match.group(0)
    
    analysis["summary"] = f"Технологии: {', '.join(analysis['technologies'][:10])}"
    return analysis

def analyze_custom_output(tool_name: str, output: str) -> dict:
    """Анализирует вывод произвольной команды"""
    analysis = {
        "tool": tool_name,
        "lines": len(output.split('\n')),
        "size": len(output),
        "summary": f"Вывод команды ({len(output.split('\n'))} строк)"
    }
    return analysis

# ============================================================
# ВЫВОД ОТЧЁТА
# ============================================================

def print_analysis_report(analysis: dict):
    """Красиво выводит отчёт по любой утилите"""
    
    tool = analysis.get("tool", "unknown")
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}📊 ОТЧЁТ {tool.upper()}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════════════════{Colors.END}")
    
    if tool == "sqlmap":
        if analysis.get("vulnerable"):
            print(f"\n{Colors.ICON_VULN} {Colors.RED}{Colors.BOLD}СТАТУС: SQL-ИНЪЕКЦИЯ НАЙДЕНА!{Colors.END}")
        else:
            print(f"\n{Colors.ICON_SUCCESS} {Colors.GREEN}{Colors.BOLD}СТАТУС: SQL-инъекция не найдена{Colors.END}")
        
        if analysis.get("vulnerability_type"):
            print(f"\n{Colors.ICON_VULN} {Colors.YELLOW}ТИПЫ УЯЗВИМОСТЕЙ:{Colors.END}")
            for vuln in analysis["vulnerability_type"]:
                print(f"   • {vuln}")
        
        if analysis.get("databases"):
            print(f"\n{Colors.ICON_DB} {Colors.GREEN}БАЗЫ ДАННЫХ:{Colors.END}")
            for db in analysis["databases"][:20]:
                print(f"   • {db}")
        
        if analysis.get("tables"):
            print(f"\n{Colors.ICON_TABLE} {Colors.GREEN}ТАБЛИЦЫ (первые 20):{Colors.END}")
            for table in analysis["tables"][:20]:
                print(f"   • {table}")
        
        if analysis.get("current_user"):
            print(f"\n{Colors.ICON_INFO} {Colors.CYAN}ТЕКУЩИЙ ПОЛЬЗОВАТЕЛЬ:{Colors.END} {analysis['current_user']}")
    
    elif tool == "nmap":
        print(f"\n{Colors.ICON_INFO} {Colors.GREEN}СТАТУС ХОСТА:{Colors.END} {analysis.get('host_status', 'unknown')}")
        
        if analysis.get("open_ports"):
            print(f"\n{Colors.ICON_PORT} {Colors.GREEN}ОТКРЫТЫЕ ПОРТЫ:{Colors.END}")
            for port in analysis["open_ports"]:
                print(f"   • {port['port']}/tcp - {port['service']}")
        
        if analysis.get("filtered_ports"):
            print(f"\n{Colors.ICON_WARNING} {Colors.YELLOW}FILTERED ПОРТЫ:{Colors.END}")
            for port in analysis["filtered_ports"][:10]:
                print(f"   • {port['port']}/tcp - {port['service']}")
        
        if analysis.get("os_guess"):
            print(f"\n{Colors.ICON_INFO} {Colors.CYAN}ПРЕДПОЛАГАЕМАЯ ОС:{Colors.END} {analysis['os_guess']}")
    
    elif tool == "gobuster":
        if analysis.get("directories"):
            print(f"\n{Colors.ICON_DIR} {Colors.GREEN}НАЙДЕННЫЕ ДИРЕКТОРИИ:{Colors.END}")
            for d in analysis["directories"][:20]:
                status_color = Colors.GREEN if d["status"] in ["200", "301", "302"] else Colors.YELLOW
                print(f"   • /{d['path']} {status_color}(Status: {d['status']}){Colors.END}")
        
        if analysis.get("status_codes"):
            print(f"\n{Colors.ICON_INFO} СТАТУС КОДЫ:")
            for code, count in analysis["status_codes"].items():
                print(f"   • {code}: {count} раз")
    
    elif tool == "nikto":
        if analysis.get("server_info"):
            print(f"\n{Colors.ICON_INFO} {Colors.CYAN}СЕРВЕР:{Colors.END} {analysis['server_info']}")
        
        if analysis.get("vulnerabilities"):
            print(f"\n{Colors.ICON_VULN} {Colors.RED}УЯЗВИМОСТИ:{Colors.END}")
            for vuln in analysis["vulnerabilities"][:10]:
                print(f"   • {vuln['type']}")
        
        if analysis.get("interesting_paths"):
            print(f"\n{Colors.ICON_DIR} {Colors.YELLOW}ИНТЕРЕСНЫЕ ПУТИ:{Colors.END}")
            for path in analysis["interesting_paths"][:10]:
                print(f"   • {path}")
    
    elif tool == "whatweb":
        if analysis.get("technologies"):
            print(f"\n{Colors.ICON_INFO} {Colors.GREEN}ТЕХНОЛОГИИ:{Colors.END}")
            for tech in analysis["technologies"][:15]:
                print(f"   • {tech}")
        
        if analysis.get("cms"):
            print(f"\n{Colors.ICON_INFO} {Colors.CYAN}ОПРЕДЕЛЁННАЯ CMS:{Colors.END} {analysis['cms']}")
        
        if analysis.get("server"):
            print(f"{Colors.ICON_INFO} {Colors.CYAN}ВЕБ-СЕРВЕР:{Colors.END} {analysis['server']}")
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.BOLD}📊 {analysis['summary']}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════════════════{Colors.END}\n")

# ============================================================
# ЗАПУСК УТИЛИТ С АНАЛИЗОМ
# ============================================================

def run_sqlmap_with_analysis(url: str, flags: str = "--batch --dbs") -> dict:
    command = f"sqlmap -u '{url}' {flags}"
    result = run_command_with_output(command, timeout=1200)
    
    if result["success"] and result["output"]:
        analysis = analyze_sqlmap_output(result["output"])
        print_analysis_report(analysis)
        return {"success": True, "output": result["output"], "analysis": analysis}
    return {"success": False, "error": result.get("error", "Ошибка")}

def run_nmap_with_analysis(target: str, flags: str = "-sV") -> dict:
    command = f"nmap {flags} {target}"
    result = run_command_with_output(command, timeout=600)
    
    if result["output"]:
        analysis = analyze_nmap_output(result["output"])
        print_analysis_report(analysis)
        return {"success": True, "output": result["output"], "analysis": analysis}
    return {"success": False, "error": result.get("error", "Ошибка")}

def run_gobuster_with_analysis(url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt") -> dict:
    command = f"gobuster dir -u {url} -w {wordlist}"
    result = run_command_with_output(command, timeout=600)
    
    if result["output"]:
        analysis = analyze_gobuster_output(result["output"])
        print_analysis_report(analysis)
        return {"success": True, "output": result["output"], "analysis": analysis}
    return {"success": False, "error": result.get("error", "Ошибка")}

def run_nikto_with_analysis(target: str) -> dict:
    command = f"nikto -h {target}"
    result = run_command_with_output(command, timeout=900)
    
    if result["output"]:
        analysis = analyze_nikto_output(result["output"])
        print_analysis_report(analysis)
        return {"success": True, "output": result["output"], "analysis": analysis}
    return {"success": False, "error": result.get("error", "Ошибка")}

def run_whatweb_with_analysis(target: str) -> dict:
    command = f"whatweb {target}"
    result = run_command_with_output(command, timeout=120)
    
    if result["output"]:
        analysis = analyze_whatweb_output(result["output"])
        print_analysis_report(analysis)
        return {"success": True, "output": result["output"], "analysis": analysis}
    return {"success": False, "error": result.get("error", "Ошибка")}

def run_custom_command_with_analysis(command: str) -> dict:
    result = run_command_with_output(command, timeout=300)
    
    if result["output"]:
        tool_name = command.split()[0] if command else "custom"
        analysis = analyze_custom_output(tool_name, result["output"])
        print_analysis_report(analysis)
        return {"success": True, "output": result["output"], "analysis": analysis}
    return {"success": False, "error": result.get("error", "Ошибка")}

# ============================================================
# ИНСТРУМЕНТЫ ДЛЯ API
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_sqlmap",
            "description": "Запускает sqlmap, анализирует вывод и показывает найденные БД, таблицы, уязвимости",
            "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "flags": {"type": "string", "default": "--batch --dbs"}}, "required": ["url"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_nmap",
            "description": "Запускает nmap, анализирует открытые порты и сервисы",
            "parameters": {"type": "object", "properties": {"target": {"type": "string"}, "flags": {"type": "string", "default": "-sV"}}, "required": ["target"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_gobuster",
            "description": "Запускает gobuster, анализирует найденные директории",
            "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "wordlist": {"type": "string", "default": "/usr/share/wordlists/dirb/common.txt"}}, "required": ["url"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_nikto",
            "description": "Запускает nikto, анализирует найденные уязвимости",
            "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_whatweb",
            "description": "Запускает whatweb, анализирует технологии веб-сайта",
            "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_custom_command",
            "description": "Выполняет любую команду и анализирует вывод",
            "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}
        }
    }
]

def execute_tool(tool_name: str, parameters: dict) -> str:
    try:
        if tool_name == "run_sqlmap":
            result = run_sqlmap_with_analysis(parameters["url"], parameters.get("flags", "--batch --dbs"))
        elif tool_name == "run_nmap":
            result = run_nmap_with_analysis(parameters["target"], parameters.get("flags", "-sV"))
        elif tool_name == "run_gobuster":
            result = run_gobuster_with_analysis(parameters["url"], parameters.get("wordlist", "/usr/share/wordlists/dirb/common.txt"))
        elif tool_name == "run_nikto":
            result = run_nikto_with_analysis(parameters["target"])
        elif tool_name == "run_whatweb":
            result = run_whatweb_with_analysis(parameters["target"])
        elif tool_name == "run_custom_command":
            result = run_custom_command_with_analysis(parameters["command"])
        else:
            return f"Неизвестный инструмент: {tool_name}"
        
        return json.dumps({
            "success": result.get("success", False),
            "summary": result.get("analysis", {}).get("summary", ""),
            "tool": tool_name
        }, ensure_ascii=False, indent=2)
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
║              🤖 DEEPSEEK AGENT - УНИВЕРСАЛЬНЫЙ АНАЛИЗАТОР 🤖               ║
║         📊 Анализирует вывод ВСЕХ утилит: nmap, sqlmap, gobuster и др.    ║
╚═══════════════════════════════════════════════════════════════════════════╝{Colors.END}
    """)
    print(f"{Colors.ICON_INFO} Агент ВИДИТ и АНАЛИЗИРУЕТ вывод ЛЮБЫХ утилит:")
    print(f"   • {Colors.GREEN}sqlmap{Colors.END} - поиск БД, таблиц, уязвимостей")
    print(f"   • {Colors.GREEN}nmap{Colors.END} - открытые порты, сервисы, ОС")
    print(f"   • {Colors.GREEN}gobuster{Colors.END} - найденные директории")
    print(f"   • {Colors.GREEN}nikto{Colors.END} - веб-уязвимости")
    print(f"   • {Colors.GREEN}whatweb{Colors.END} - технологии сайта")
    print()

def main():
    print_banner()
    agent = DeepSeekAgent()
    
    print(f"{Colors.ICON_AGENT} {Colors.GREEN}Агент запущен!{Colors.END}")
    print(f"{Colors.ICON_INFO} Примеры запросов:")
    print(f"   • {Colors.YELLOW}запусти sqlmap на http://testphp.vulnweb.com/artists.php?artist=1{Colors.END}")
    print(f"   • {Colors.YELLOW}просканируй nmap localhost{Colors.END}")
    print(f"   • {Colors.YELLOW}проверь директории на example.com{Colors.END}")
    print(f"   • {Colors.YELLOW}сделай nikto сканирование target.com{Colors.END}")
    print(f"   • {Colors.YELLOW}определи технологии на example.com{Colors.END}")
    print(f"\n{Colors.ICON_INFO} Для выхода введите: exit\n")
    
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
            
            if response and response.strip():
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