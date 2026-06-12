import subprocess
import json
import re
import os
from typing import Dict, Any

def execute_system_command(command: str, timeout: int = 60, confirm_dangerous: bool = True) -> Dict[str, Any]:
    """Выполняет системную команду"""
    print(f"🛠️ [TOOL] execute: {command[:100]}")
    
    dangerous_keywords = ['--os-shell', 'rm -rf', 'mkfs', 'dd if=', 'format', 'shutdown', 'reboot']
    
    if confirm_dangerous:
        for dangerous in dangerous_keywords:
            if dangerous in command.lower():
                confirm = input(f"\n⚠️ Опасная команда! Выполнить? (y/N): ")
                if confirm.lower() != 'y':
                    return {"success": False, "output": "Команда отклонена"}
                break
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
            executable='/bin/bash' if os.name != 'nt' else None
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout if result.stdout else result.stderr,
            "error": result.stderr if not result.stdout else None
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": f"Timeout ({timeout} сек)"}
    except Exception as e:
        return {"success": False, "output": f"Ошибка: {str(e)}"}

def analyze_sqlmap_output(output: str) -> Dict[str, Any]:
    """Анализирует вывод sqlmap"""
    analysis = {
        "vulnerabilities": [],
        "databases": [],
        "tables": [],
        "risk": "LOW",
        "summary": ""
    }
    
    if "vulnerable" in output.lower():
        analysis["vulnerabilities"].append("SQL Injection")
    
    dbs = re.findall(r'\[\*\*\]\s+(\w+)', output)
    if not dbs:
        dbs = re.findall(r'\[\[\s*\]\]\s*(\w+)', output)
    analysis["databases"] = list(set(dbs))
    
    tables = re.findall(r'\| (\w+) \|', output)
    analysis["tables"] = list(set(tables))[:20]
    
    if analysis["vulnerabilities"]:
        analysis["risk"] = "HIGH 🔴"
        analysis["summary"] = f"SQL-инъекция! Найдено {len(analysis['databases'])} БД"
    elif analysis["databases"]:
        analysis["risk"] = "MEDIUM 🟡"
        analysis["summary"] = f"Найдено {len(analysis['databases'])} БД"
    else:
        analysis["summary"] = "Уязвимостей не обнаружено"
    
    return analysis

def read_file(filepath: str) -> str:
    """Читает файл"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return content[:5000]
    except Exception as e:
        return f"Ошибка: {e}"

def write_file(filepath: str, content: str) -> str:
    """Сохраняет файл"""
    try:
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ Сохранено: {filepath}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def python_calculate(expression: str) -> str:
    """Выполняет вычисления"""
    try:
        allowed = {"abs": abs, "round": round, "min": min, "max": max, "sum": sum}
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"📊 {expression} = {result}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_system_command",
            "description": "Выполняет системную команду",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Команда для выполнения"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_sqlmap_output",
            "description": "Анализирует вывод sqlmap",
            "parameters": {
                "type": "object",
                "properties": {
                    "output": {"type": "string", "description": "Вывод sqlmap"}
                },
                "required": ["output"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Читает файл",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Сохраняет файл",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "python_calculate",
            "description": "Вычисления",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
            }
        }
    }
]