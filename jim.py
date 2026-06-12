#!/usr/bin/env python3
"""
Jim - AI-Powered Pentesting Assistant for Kali Linux
Умный агент: анализирует цель и выбирает нужные утилиты
"""

import sys
import os
import subprocess
import json
import re
import shutil
from datetime import datetime

VERSION = "2.0.0"

# ============================================================
# ОБРАБОТКА АРГУМЕНТОВ КОМАНДНОЙ СТРОКИ
# ============================================================

def update_jim():
    """Обновляет Jim из GitHub репозитория"""
    print("🔄 Обновление Jim AI Agent...")
    jim_dir = os.path.expanduser("~/.jim")
    repo_url = "https://github.com/Lolicks/hackagent.git"
    temp_dir = "/tmp/jim-update"
    
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        print("📦 Скачивание обновлений...")
        subprocess.run(["git", "clone", "--depth", "1", repo_url, temp_dir], capture_output=True, check=True)
        
        print("📄 Обновление файлов...")
        shutil.copy2(f"{temp_dir}/jim.py", f"{jim_dir}/jim.py")
        if os.path.exists(f"{temp_dir}/system_prompt.txt"):
            shutil.copy2(f"{temp_dir}/system_prompt.txt", f"{jim_dir}/")
        
        shutil.rmtree(temp_dir)
        
        print("✅ Jim успешно обновлён!")
        return True
    except Exception as e:
        print(f"❌ Ошибка обновления: {e}")
        return False

if len(sys.argv) > 1:
    if sys.argv[1] in ["-v", "--version"]:
        print(f"Jim AI Agent v{VERSION}")
        sys.exit(0)
    elif sys.argv[1] in ["-h", "--help"]:
        print("""
Jim AI Agent - Умный помощник для пентеста

Использование:
    jim                    Запустить агента
    jim -h, --help         Справка
    jim -v, --version      Версия
    jim -u, --update       Обновить

Примеры:
    jim
    > Протестируй сайт example.com
    > Проверь SQL на testphp.vulnweb.com/artists.php?artist=1
""")
        sys.exit(0)
    elif sys.argv[1] in ["-u", "--update", "-update"]:
        success = update_jim()
        sys.exit(0 if success else 1)

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
    
    ICON_AGENT = "🐍"
    ICON_USER = "👤"
    ICON_TOOL = "🔧"
    ICON_SUCCESS = "✅"
    ICON_ERROR = "❌"
    ICON_WARNING = "⚠️"
    ICON_INFO = "ℹ️"
    ICON_ANALYSIS = "🔍"
    ICON_FOUND = "🎯"
    ICON_NOT_FOUND = "❌"
    ICON_REPORT = "📊"

# ============================================================
# ЗАГРУЗКА НАСТРОЕК
# ============================================================

def load_api_key():
    """Загружает API ключ из ~/.jim/.env"""
    env_path = os.path.expanduser("~/.jim/.env")
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return None

def load_system_prompt():
    """Загружает системный промпт"""
    prompt_path = os.path.expanduser("~/.jim/system_prompt.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    return """Ты - Jim, умный ИИ-агент для пентеста. 
Анализируй цель, выбирай нужные утилиты, не запускай лишнее.
После каждой утилиты объясняй, что нашёл или не нашёл."""

API_KEY = load_api_key()
SYSTEM_PROMPT = load_system_prompt()

# ============================================================
# АНАЛИЗ ЦЕЛИ
# ============================================================

def analyze_target(user_input: str) -> dict:
    """Анализирует запрос пользователя и определяет, что нужно делать"""
    analysis = {
        "target": "",
        "has_url": False,
        "has_ip": False,
        "has_sql_error": False,
        "has_parameters": False,
        "suggested_tools": [],
        "explanation": ""
    }
    
    # Извлекаем цель (IP или URL)
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    url_pattern = r'https?://[^\s]+|[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}[^\s]*'
    
    ip_matches = re.findall(ip_pattern, user_input)
    url_matches = re.findall(url_pattern, user_input)
    
    if ip_matches:
        analysis["has_ip"] = True
        analysis["target"] = ip_matches[0]
        analysis["explanation"] = f"Обнаружен IP-адрес: {ip_matches[0]}"
    elif url_matches:
        analysis["has_url"] = True
        analysis["target"] = url_matches[0]
        analysis["explanation"] = f"Обнаружен URL: {url_matches[0]}"
    
    # Проверяем наличие параметров в URL
    if "?" in analysis["target"] and "=" in analysis["target"]:
        analysis["has_parameters"] = True
        analysis["suggested_tools"].append("sqlmap")
        analysis["explanation"] += " | Обнаружены параметры → нужно проверить SQL-инъекции"
    
    # Проверяем ключевые слова
    if "sql" in user_input.lower() or "инъекц" in user_input.lower():
        analysis["has_sql_error"] = True
        if "sqlmap" not in analysis["suggested_tools"]:
            analysis["suggested_tools"].append("sqlmap")
        analysis["explanation"] += " | Упоминание SQL → проверка инъекций"
    
    # Базовые инструменты для любого веб-тестирования
    if analysis["has_url"] or analysis["has_ip"]:
        analysis["suggested_tools"].append("whatweb")
        analysis["suggested_tools"].append("nmap")
        analysis["explanation"] += " | Базовое сканирование портов и технологий"
    
    # Убираем дубликаты
    analysis["suggested_tools"] = list(dict.fromkeys(analysis["suggested_tools"]))
    
    return analysis

# ============================================================
# ЗАПУСК УТИЛИТ С АНАЛИЗОМ
# ============================================================

def run_tool(tool: str, target: str) -> dict:
    """Запускает утилиту и возвращает результат с анализом"""
    
    print(f"\n{Colors.ICON_TOOL} {Colors.CYAN}Запуск:{Colors.END} {Colors.BOLD}{tool}{Colors.END}")
    print(f"{Colors.DIM}{'─' * 70}{Colors.END}")
    
    commands = {
        "whatweb": f"whatweb {target}",
        "nmap": f"nmap -sV --open {target}",
        "sqlmap": f"sqlmap -u '{target}' --batch --dbs --level=1"
    }
    
    if tool not in commands:
        return {"success": False, "error": f"Неизвестный инструмент: {tool}"}
    
    try:
        result = subprocess.run(
            commands[tool],
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        output = result.stdout + result.stderr
        
        # Анализ результата
        analysis = analyze_tool_output(tool, output)
        
        return {
            "success": result.returncode == 0,
            "output": output[:2000],
            "analysis": analysis
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "analysis": {"found": False, "message": "Время ожидания истекло"}}
    except Exception as e:
        return {"success": False, "output": "", "analysis": {"found": False, "message": str(e)}}

def analyze_tool_output(tool: str, output: str) -> dict:
    """Анализирует вывод утилиты и даёт понятное пояснение"""
    
    output_lower = output.lower()
    analysis = {"found": False, "message": "", "details": ""}
    
    if tool == "whatweb":
        # Ищем технологии
        techs = re.findall(r'\[(.*?)\]', output)
        if techs:
            analysis["found"] = True
            analysis["message"] = f"🎯 НАЙДЕНО: Определены технологии"
            analysis["details"] = f"   • {', '.join(techs[:5])}"
        else:
            analysis["found"] = False
            analysis["message"] = f"❌ НЕ НАЙДЕНО: Не удалось определить технологии"
            analysis["details"] = "   • Возможно сайт защищён или использует нестандартные технологии"
    
    elif tool == "nmap":
        # Ищем открытые порты
        ports = re.findall(r'(\d+)/tcp\s+open', output)
        services = re.findall(r'(\d+)/tcp\s+open\s+(\w+)', output)
        
        if ports:
            analysis["found"] = True
            analysis["message"] = f"🎯 НАЙДЕНО: Открытые порты ({len(ports)} шт)"
            details = []
            for port, service in services[:10]:
                details.append(f"   • Порт {port}: {service}")
            analysis["details"] = "\n".join(details) if details else "   • Подробности в выводе выше"
        else:
            analysis["found"] = False
            analysis["message"] = f"❌ НЕ НАЙДЕНО: Открытых портов"
            analysis["details"] = "   • Возможно хост недоступен или firewall блокирует"
    
    elif tool == "sqlmap":
        # Проверяем наличие SQL-инъекции
        if "vulnerable" in output_lower or "injectable" in output_lower:
            analysis["found"] = True
            analysis["message"] = f"🎯 НАЙДЕНО: SQL-инъекция!"
            
            # Определяем тип
            if "boolean" in output_lower:
                analysis["details"] = "   • Тип: Boolean-based Blind SQLi"
            elif "union" in output_lower:
                analysis["details"] = "   • Тип: Union-based SQLi"
            elif "time" in output_lower:
                analysis["details"] = "   • Тип: Time-based Blind SQLi"
            else:
                analysis["details"] = "   • Параметр уязвим для SQL-инъекций"
            
            # Ищем базы данных
            dbs = re.findall(r'\[\*\*\]\s+(\w+)', output)
            if dbs:
                analysis["details"] += f"\n   • Найдены БД: {', '.join(dbs[:3])}"
        else:
            analysis["found"] = False
            analysis["message"] = f"❌ НЕ НАЙДЕНО: SQL-инъекция"
            analysis["details"] = "   • Параметры безопасны или защищены WAF"
    
    return analysis

# ============================================================
# ФОРМИРОВАНИЕ ОТЧЕТА
# ============================================================

def print_phase_header(phase: str, target: str):
    """Печатает заголовок этапа"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}📋 {phase}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.END}")

def print_analysis_result(analysis: dict, tool: str):
    """Печатает результат анализа"""
    if analysis.get("found"):
        print(f"\n{Colors.GREEN}{analysis['message']}{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}{analysis['message']}{Colors.END}")
    
    if analysis.get("details"):
        print(analysis["details"])

def print_final_report(scan_results: list, target: str):
    """Печатает итоговый отчёт"""
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'═' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}{Colors.ICON_REPORT} ИТОГОВЫЙ ОТЧЁТ{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'═' * 70}{Colors.END}")
    
    print(f"\n{Colors.CYAN}🎯 Цель:{Colors.END} {target}")
    print(f"{Colors.CYAN}📅 Время:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n{Colors.BOLD}📊 Результаты сканирования:{Colors.END}")
    
    found_anything = False
    for result in scan_results:
        if result.get("analysis", {}).get("found"):
            found_anything = True
            print(f"\n   {Colors.GREEN}✅ {result['tool'].upper()}:{Colors.END}")
            print(f"      {result['analysis'].get('message', '')}")
            if result['analysis'].get('details'):
                print(f"      {result['analysis']['details']}")
    
    if not found_anything:
        print(f"\n   {Colors.YELLOW}⚠️ Уязвимостей не обнаружено{Colors.END}")
        print(f"   {Colors.DIM}Рекомендация: проверьте доступность цели и права доступа{Colors.END}")
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'═' * 70}{Colors.END}")

# ============================================================
# ОСНОВНОЙ ЦИКЛ АГЕНТА
# ============================================================

def print_banner():
    os.system('clear')
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                           ║")
    print("║              🐍 JIM AI - УМНЫЙ ПЕНТЕСТ АССИСТЕНТ 🐍                        ║")
    print("║                   Анализирую цель → Выбираю утилиты → Отчёт               ║")
    print("║                                                                           ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")

def main():
    if not API_KEY:
        print(f"{Colors.ICON_ERROR} {Colors.RED}API ключ не найден!{Colors.END}")
        print("Запустите установку заново: ./install.sh")
        return
    
    print_banner()
    print(f"{Colors.ICON_AGENT} {Colors.GREEN}Jim готов!{Colors.END}")
    print(f"{Colors.ICON_INFO} Просто опишите цель, а я сам решу, что проверять")
    print(f"{Colors.DIM}{'─' * 70}{Colors.END}")
    
    while True:
        try:
            user_input = input(f"\n{Colors.BOLD}{Colors.GREEN}┌─[{Colors.ICON_USER}]{Colors.END} ").strip()
            
            if user_input.lower() in ['/exit', 'exit', 'quit']:
                print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}До свидания!{Colors.END}\n")
                break
            
            if user_input.lower() == '/clear':
                os.system('clear')
                print_banner()
                continue
            
            if not user_input:
                continue
            
            # 1. Анализ цели
            print(f"\n{Colors.ICON_ANALYSIS} {Colors.BLUE}Анализирую цель...{Colors.END}")
            analysis = analyze_target(user_input)
            
            print(f"\n{Colors.CYAN}🎯 Цель: {analysis['target']}{Colors.END}")
            print(f"{Colors.CYAN}📋 План: {analysis['explanation']}{Colors.END}")
            
            if not analysis["suggested_tools"]:
                print(f"{Colors.ICON_WARNING} {Colors.YELLOW}Не удалось определить цель. Укажите IP или URL.{Colors.END}")
                continue
            
            # 2. Запуск утилит
            scan_results = []
            
            for tool in analysis["suggested_tools"]:
                print_phase_header(f"Этап {len(scan_results)+1}: {tool.upper()}", analysis["target"])
                
                result = run_tool(tool, analysis["target"])
                result["tool"] = tool
                scan_results.append(result)
                
                # Выводим анализ
                print_analysis_result(result.get("analysis", {}), tool)
                
                # Если нашли SQL - не продолжаем (уже есть результат)
                if tool == "sqlmap" and result.get("analysis", {}).get("found"):
                    print(f"\n{Colors.GREEN}✅ SQL-инъекция подтверждена! Дальнейшее тестирование не требуется.{Colors.END}")
                    break
            
            # 3. Итоговый отчёт
            print_final_report(scan_results, analysis["target"])
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.ICON_WARNING} {Colors.YELLOW}Прервано{Colors.END}")
            continue
        except Exception as e:
            print(f"\n{Colors.ICON_ERROR} {Colors.RED}Ошибка: {e}{Colors.END}")

if __name__ == "__main__":
    main()