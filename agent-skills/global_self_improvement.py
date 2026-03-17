"""
Robofabio Global Self-Improvement System v2.0
Überwacht und optimiert ALLE Aktivitäten automatisch
"""

import json
import sqlite3
import functools
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
import os
import sys


@dataclass
class ActivityLog:
    """Jede Aktivität wird geloggt"""
    timestamp: str
    activity_type: str  # 'conversation', 'tool_call', 'code_execution', 'web_search', 'file_operation', etc.
    description: str
    tokens_input: int
    tokens_output: int
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    context: str = ""  # Zusätzlicher Kontext (z.B. Dateiname, URL)
    learning_value: int = 0  # 0-5 wie viel daraus gelernt werden kann
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class UserPreference:
    """Gelernte Präferenzen von Master Albert"""
    id: Optional[int] = None
    category: str = ""  # 'communication', 'work_style', 'technical', 'business'
    preference: str = ""  # Was wurde gelernt
    evidence: str = ""  # Belege
    confidence: float = 0.5
    first_observed: str = ""
    last_confirmed: str = ""
    times_observed: int = 0
    importance: int = 3  # 1-5 wie wichtig
    
    def __post_init__(self):
        if not self.first_observed:
            self.first_observed = datetime.now().isoformat()
        if not self.last_confirmed:
            self.last_confirmed = datetime.now().isoformat()


@dataclass
class SkillProgress:
    """Fortschritt beim Erlernen von Skills"""
    skill_name: str
    proficiency: float  # 0-1
    times_used: int
    last_used: str
    success_rate: float
    notes: str = ""


class GlobalSelfImprovement:
    """
    Globaler Self-Improvement Engine
    Trackt ALLES und lernt daraus
    """
    
    def __init__(self, db_path: str = "/root/.openclaw/workspace/memory/robofabio_mind.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
        self._init_default_preferences()
        
    def init_database(self):
        """Initialisiert alle Tabellen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Alle Aktivitäten
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    activity_type TEXT,
                    description TEXT,
                    tokens_input INTEGER,
                    tokens_output INTEGER,
                    duration_ms REAL,
                    success BOOLEAN,
                    error_message TEXT,
                    context TEXT,
                    learning_value INTEGER DEFAULT 0
                )
            """)
            
            # User Preferences (Master Albert's Stil)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    preference TEXT,
                    evidence TEXT,
                    confidence REAL DEFAULT 0.5,
                    first_observed TEXT,
                    last_confirmed TEXT,
                    times_observed INTEGER DEFAULT 1,
                    importance INTEGER DEFAULT 3
                )
            """)
            
            # Skill Progress
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skill_progress (
                    skill_name TEXT PRIMARY KEY,
                    proficiency REAL DEFAULT 0.0,
                    times_used INTEGER DEFAULT 0,
                    last_used TEXT,
                    success_rate REAL DEFAULT 0.0,
                    notes TEXT
                )
            """)
            
            # Performance Metrics (aggregiert)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_performance (
                    date TEXT PRIMARY KEY,
                    total_activities INTEGER,
                    total_tokens INTEGER,
                    avg_duration_ms REAL,
                    success_rate REAL,
                    top_skill TEXT,
                    key_learning TEXT
                )
            """)
            
            # Fehler-Log für Pattern-Erkennung
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type TEXT,
                    error_message TEXT,
                    context TEXT,
                    timestamp TEXT,
                    resolution TEXT,
                    times_occurred INTEGER DEFAULT 1
                )
            """)
            
            conn.commit()
    
    def _init_default_preferences(self):
        """Start-Präferenzen von Master Albert (aus MEMORY.md)"""
        defaults = [
            ("communication", "Deutsch bevorzugt", "Alle Konversationen auf Deutsch", 0.95, 5),
            ("communication", "Direkte Antworten", "'kurz und knackig' mehrfach erwähnt", 0.9, 5),
            ("work_style", "Profit-orientiert", "Jede Aktion wird auf ROI geprüft", 0.95, 5),
            ("technical", "Sicherheit wichtig", "Credentials nie im Chat", 0.9, 5),
            ("business", "Trading Focus", "Polymarket, Bitget, Arbitrage", 0.9, 4),
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for cat, pref, ev, conf, imp in defaults:
                cursor.execute("""
                    INSERT OR IGNORE INTO user_preferences 
                    (category, preference, evidence, confidence, importance, first_observed, last_confirmed)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (cat, pref, ev, conf, imp, datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
    
    # ═══════════════════════════════════════════════════════════
    # GLOBAL TRACKING - Alles wird aufgezeichnet
    # ═══════════════════════════════════════════════════════════
    
    def log_activity(self, activity: ActivityLog):
        """Loggt jede Aktivität"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO activities 
                (activity_type, description, tokens_input, tokens_output, duration_ms, 
                 success, error_message, context, learning_value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                activity.activity_type, activity.description,
                activity.tokens_input, activity.tokens_output, activity.duration_ms,
                activity.success, activity.error_message, activity.context,
                activity.learning_value
            ))
            conn.commit()
        
        # Auto-Analyse bei Fehlern
        if not activity.success:
            self._analyze_error(activity)
    
    def track_execution(self, activity_type: str, description: str = ""):
        """Decorator für automatisches Tracking"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = (time.time() - start) * 1000
                    
                    self.log_activity(ActivityLog(
                        timestamp=datetime.now().isoformat(),
                        activity_type=activity_type,
                        description=description or func.__name__,
                        tokens_input=0,  # Wird von außerhalb gesetzt
                        tokens_output=0,
                        duration_ms=duration,
                        success=True,
                        context=str(args[:2]) if args else ""
                    ))
                    return result
                    
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    self.log_activity(ActivityLog(
                        timestamp=datetime.now().isoformat(),
                        activity_type=activity_type,
                        description=description or func.__name__,
                        tokens_input=0,
                        tokens_output=0,
                        duration_ms=duration,
                        success=False,
                        error_message=str(e),
                        context=str(args[:2]) if args else ""
                    ))
                    raise
            return wrapper
        return decorator
    
    # ═══════════════════════════════════════════════════════════
    # PREFERENCE LEARNING - Master Albert verstehen
    # ═══════════════════════════════════════════════════════════
    
    def learn_preference(self, category: str, preference: str, evidence: str, 
                         importance: int = 3) -> bool:
        """Lernt eine neue Präferenz oder verstärkt bestehende"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute("""
                SELECT id, times_observed, confidence FROM user_preferences 
                WHERE category = ? AND preference = ?
            """, (category, preference))
            
            row = cursor.fetchone()
            now = datetime.now().isoformat()
            
            if row:
                # Update
                id_, times, conf = row
                new_times = times + 1
                # Confidence steigt mit wiederholter Beobachtung
                new_conf = min(0.99, conf + 0.05)
                
                cursor.execute("""
                    UPDATE user_preferences 
                    SET times_observed = ?, confidence = ?, last_confirmed = ?,
                        evidence = evidence || '; ' || ?
                    WHERE id = ?
                """, (new_times, new_conf, now, evidence, id_))
            else:
                # New preference
                cursor.execute("""
                    INSERT INTO user_preferences 
                    (category, preference, evidence, confidence, importance, first_observed, last_confirmed)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (category, preference, evidence, 0.6, importance, now, now))
            
            conn.commit()
            return True
    
    def get_preferences(self, category: str = None, min_confidence: float = 0.5) -> List[Dict]:
        """Holt gelernte Präferenzen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if category:
                cursor.execute("""
                    SELECT category, preference, evidence, confidence, times_observed, importance
                    FROM user_preferences
                    WHERE category = ? AND confidence >= ?
                    ORDER BY importance DESC, confidence DESC
                """, (category, min_confidence))
            else:
                cursor.execute("""
                    SELECT category, preference, evidence, confidence, times_observed, importance
                    FROM user_preferences
                    WHERE confidence >= ?
                    ORDER BY importance DESC, confidence DESC
                """, (min_confidence,))
            
            return [
                {
                    'category': row[0],
                    'preference': row[1],
                    'evidence': row[2],
                    'confidence': row[3],
                    'times_observed': row[4],
                    'importance': row[5]
                }
                for row in cursor.fetchall()
            ]
    
    # ═══════════════════════════════════════════════════════════
    # SKILL TRACKING - Fortschritt messen
    # ═══════════════════════════════════════════════════════════
    
    def update_skill(self, skill_name: str, success: bool, notes: str = ""):
        """Aktualisiert Skill-Fortschritt"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM skill_progress WHERE skill_name = ?", (skill_name,))
            row = cursor.fetchone()
            
            now = datetime.now().isoformat()
            
            if row:
                # Update
                _, prof, times, _, success_rate, _ = row
                new_times = times + 1
                new_success_rate = ((success_rate * times) + (1 if success else 0)) / new_times
                # Proficiency wächst langsam
                new_prof = min(1.0, prof + (0.01 if success else -0.005))
                
                cursor.execute("""
                    UPDATE skill_progress 
                    SET proficiency = ?, times_used = ?, last_used = ?, 
                        success_rate = ?, notes = ?
                    WHERE skill_name = ?
                """, (new_prof, new_times, now, new_success_rate, notes, skill_name))
            else:
                # New skill
                prof = 0.1 if success else 0.0
                cursor.execute("""
                    INSERT INTO skill_progress 
                    (skill_name, proficiency, times_used, last_used, success_rate, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (skill_name, prof, 1, now, 1.0 if success else 0.0, notes))
            
            conn.commit()
    
    def get_skills(self) -> List[Dict]:
        """Holt alle Skills mit Fortschritt"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT skill_name, proficiency, times_used, last_used, success_rate, notes
                FROM skill_progress
                ORDER BY proficiency DESC
            """)
            
            return [
                {
                    'name': row[0],
                    'proficiency': row[1],
                    'times_used': row[2],
                    'last_used': row[3],
                    'success_rate': row[4],
                    'notes': row[5]
                }
                for row in cursor.fetchall()
            ]
    
    # ═══════════════════════════════════════════════════════════
    # ERROR ANALYSIS - Aus Fehlern lernen
    # ═══════════════════════════════════════════════════════════
    
    def _analyze_error(self, activity: ActivityLog):
        """Analysiert Fehler für Pattern-Erkennung"""
        if not activity.error_message:
            return
        
        error_type = self._categorize_error(activity.error_message)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if similar error exists
            cursor.execute("""
                SELECT id, times_occurred FROM error_patterns 
                WHERE error_type = ? AND context = ?
            """, (error_type, activity.context[:100]))
            
            row = cursor.fetchone()
            
            if row:
                # Update
                id_, times = row
                cursor.execute("""
                    UPDATE error_patterns 
                    SET times_occurred = ?, timestamp = ?
                    WHERE id = ?
                """, (times + 1, datetime.now().isoformat(), id_))
            else:
                # New error
                cursor.execute("""
                    INSERT INTO error_patterns 
                    (error_type, error_message, context, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (error_type, activity.error_message, activity.context, datetime.now().isoformat()))
            
            conn.commit()
    
    def _categorize_error(self, error_message: str) -> str:
        """Kategorisiert Fehlertypen"""
        error_lower = error_message.lower()
        
        if any(x in error_lower for x in ['api key', 'authentication', 'unauthorized']):
            return 'auth_error'
        elif any(x in error_lower for x in ['timeout', 'connection', 'network']):
            return 'network_error'
        elif any(x in error_lower for x in ['not found', '404', 'missing']):
            return 'not_found_error'
        elif any(x in error_lower for x in ['rate limit', 'too many requests']):
            return 'rate_limit_error'
        elif any(x in error_lower for x in ['permission', 'access denied']):
            return 'permission_error'
        else:
            return 'unknown_error'
    
    def get_common_errors(self, limit: int = 5) -> List[Dict]:
        """Holt häufigste Fehler"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT error_type, context, times_occurred, resolution
                FROM error_patterns
                ORDER BY times_occurred DESC
                LIMIT ?
            """, (limit,))
            
            return [
                {
                    'type': row[0],
                    'context': row[1],
                    'times': row[2],
                    'resolution': row[3]
                }
                for row in cursor.fetchall()
            ]
    
    # ═══════════════════════════════════════════════════════════
    # DAILY REPORT - Der Statusbericht
    # ═══════════════════════════════════════════════════════════
    
    def generate_status_report(self) -> str:
        """Generiert vollständigen Status-Report"""
        # Stats der letzten 24h
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*),
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END),
                    SUM(tokens_input + tokens_output),
                    AVG(duration_ms),
                    COUNT(DISTINCT activity_type)
                FROM activities
                WHERE timestamp > datetime('now', '-1 day')
            """)
            
            total, successful, tokens, avg_duration, types = cursor.fetchone()
        
        skills = self.get_skills()
        preferences = self.get_preferences(min_confidence=0.7)
        errors = self.get_common_errors(3)
        
        report = f"""
🤖 ROBOFABIO STATUS REPORT
{'='*60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📊 LAST 24H ACTIVITY
   Total Activities: {total or 0}
   Success Rate: {(successful/total*100) if total else 0:.1f}%
   Total Tokens: {tokens or 0:,}
   Avg Duration: {(avg_duration or 0)/1000:.2f}s
   Activity Types: {types or 0}

🎓 SKILLS ({len(skills)} total)
"""
        
        for skill in skills[:5]:
            bar = '█' * int(skill['proficiency'] * 10) + '░' * (10 - int(skill['proficiency'] * 10))
            report += f"   {skill['name'][:25]:25} [{bar}] {skill['proficiency']:.0%}\n"
        
        report += f"\n🧠 HIGH-CONFIDENCE PREFERENCES ({len(preferences)} total)\n"
        for pref in preferences[:5]:
            report += f"   • {pref['preference']} ({pref['confidence']:.0%})\n"
        
        if errors:
            report += f"\n⚠️ COMMON ERRORS\n"
            for err in errors:
                report += f"   • {err['type']}: {err['times']}x\n"
        
        report += f"\n💡 SELF-IMPROVEMENT SUGGESTIONS\n"
        
        # Auto-generiere Vorschläge
        if total and (successful/total) < 0.8:
            report += "   • Success rate below 80% - analyzing failure patterns\n"
        if tokens and tokens > 100000:
            report += "   • High token usage - consider batching strategies\n"
        if not errors:
            report += "   • No recurring errors - all systems nominal\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report
    
    def save_daily_summary(self):
        """Speichert tägliche Zusammenfassung"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*),
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END),
                    SUM(tokens_input + tokens_output),
                    AVG(duration_ms)
                FROM activities
                WHERE DATE(timestamp) = ?
            """, (today,))
            
            total, successful, tokens, avg_duration = cursor.fetchone()
            success_rate = (successful / total) if total else 0
            
            # Top Skill
            cursor.execute("""
                SELECT activity_type, COUNT(*) as count
                FROM activities
                WHERE DATE(timestamp) = ?
                GROUP BY activity_type
                ORDER BY count DESC
                LIMIT 1
            """, (today,))
            row = cursor.fetchone()
            top_skill = row[0] if row else "none"
            
            cursor.execute("""
                INSERT OR REPLACE INTO daily_performance
                (date, total_activities, total_tokens, avg_duration_ms, success_rate, top_skill)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (today, total or 0, tokens or 0, avg_duration or 0, success_rate, top_skill))
            
            conn.commit()


# ═══════════════════════════════════════════════════════════
# GLOBAL INSTANCE - Für einfachen Zugriff
# ═══════════════════════════════════════════════════════════

_global_improvement = None

def get_improvement() -> GlobalSelfImprovement:
    """Globaler Zugriff auf Self-Improvement"""
    global _global_improvement
    if _global_improvement is None:
        _global_improvement = GlobalSelfImprovement()
    return _global_improvement


def log(activity_type: str, description: str, success: bool = True, **kwargs):
    """Kurzform für Logging"""
    imp = get_improvement()
    imp.log_activity(ActivityLog(
        activity_type=activity_type,
        description=description,
        success=success,
        **kwargs
    ))


def learn_pref(category: str, preference: str, evidence: str):
    """Kurzform für Preference Learning"""
    get_improvement().learn_preference(category, preference, evidence)


def status() -> str:
    """Kurzform für Status Report"""
    return get_improvement().generate_status_report()


if __name__ == "__main__":
    # Test
    print("🤖 Testing Global Self-Improvement System...\n")
    
    # Log some activities
    log("conversation", "Test conversation", True, tokens_input=100, tokens_output=150)
    log("tool_call", "Web search executed", True, duration_ms=500)
    log("code_execution", "Script ran successfully", True, context="test.py")
    
    # Learn preference
    learn_pref("communication", "short answers", "User said 'kurz' multiple times")
    
    # Update skill
    imp = get_improvement()
    imp.update_skill("web_search", True, "Brave API working well")
    imp.update_skill("browser_automation", True, "Playwright installed")
    
    # Status report
    print(status())
