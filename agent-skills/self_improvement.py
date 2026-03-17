"""
Self-Improvement System für Robofabio
Meta-Agent für kontinuierliche Optimierung

Core Loop:
1. OBSERVE → Performance messen (Tokens, Zeit, Erfolgsrate)
2. ANALYZE → Muster erkennen (was funktioniert?)
3. IMPROVE → Strategien anpassen
4. EXECUTE → Neue Taktiken testen
5. MEASURE → Ergebnisse vergleichen
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import os


@dataclass
class PerformanceMetric:
    """Ein Performance-Datapoint"""
    timestamp: str
    session_id: str
    task_type: str  # z.B. "trading", "content_creation", "research"
    tokens_used: int
    time_seconds: float
    success: bool
    user_satisfaction: int  # 1-5 (manuell oder aus Feedback)
    error_count: int
    strategy_used: str  # Welche Taktik wurde angewendet
    outcome: str  # Was war das Ergebnis
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ImprovementStrategy:
    """Eine Verbesserungs-Strategie"""
    id: Optional[int] = None
    name: str = ""  # z.B. "parallel_tool_calls", "memory_first_approach"
    description: str = ""
    category: str = ""  # "speed", "accuracy", "token_efficiency", "user_experience"
    implemented_at: str = ""
    success_rate: float = 0.0  # 0-1
    times_used: int = 0
    active: bool = True
    
    def __post_init__(self):
        if not self.implemented_at:
            self.implemented_at = datetime.now().isoformat()


@dataclass
class LearningEntry:
    """Ein gelerntes Konzept/Pattern"""
    id: Optional[int] = None
    concept: str = ""  # Was wurde gelernt
    context: str = ""  # In welchem Zusammenhang
    evidence: str = ""  # Beweis/Erfahrung
    confidence: float = 0.0  # 0-1 wie sicher
    first_observed: str = ""
    last_reinforced: str = ""
    times_observed: int = 1
    
    def __post_init__(self):
        if not self.first_observed:
            self.first_observed = datetime.now().isoformat()
        if not self.last_reinforced:
            self.last_reinforced = datetime.now().isoformat()


class SelfImprovementEngine:
    """
    Der Meta-Agent für Selbstverbesserung
    """
    
    def __init__(self, db_path: str = "robofabio_brain.db"):
        self.db_path = db_path
        self.init_database()
        
        # Aktive Strategien laden
        self.active_strategies = self._load_active_strategies()
        
    def init_database(self):
        """Initialisiert die Self-Improvement DB"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Performance Metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT,
                    task_type TEXT,
                    tokens_used INTEGER,
                    time_seconds REAL,
                    success BOOLEAN,
                    user_satisfaction INTEGER,
                    error_count INTEGER,
                    strategy_used TEXT,
                    outcome TEXT
                )
            """)
            
            # Improvement Strategies
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    description TEXT,
                    category TEXT,
                    implemented_at TEXT,
                    success_rate REAL DEFAULT 0.0,
                    times_used INTEGER DEFAULT 0,
                    active BOOLEAN DEFAULT 1
                )
            """)
            
            # Learnings/Memories
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    concept TEXT,
                    context TEXT,
                    evidence TEXT,
                    confidence REAL DEFAULT 0.0,
                    first_observed TEXT,
                    last_reinforced TEXT,
                    times_observed INTEGER DEFAULT 1
                )
            """)
            
            # Daily Summaries
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_summaries (
                    date TEXT PRIMARY KEY,
                    total_tasks INTEGER,
                    success_rate REAL,
                    avg_tokens_per_task REAL,
                    avg_time_seconds REAL,
                    key_learnings TEXT,
                    improvements_made TEXT
                )
            """)
            
            conn.commit()
            
            # Default Strategien einfügen
            self._init_default_strategies()
    
    def _init_default_strategies(self):
        """Standard-Strategien einfügen"""
        defaults = [
            ("memory_first", "Immer zuerst Memory checken vor Web-Suche", "speed", 1),
            ("parallel_tools", "Wo möglich Tools parallel ausführen", "speed", 1),
            ("batch_similar", "Ähnliche Tasks batchen", "token_efficiency", 1),
            ("proactive_suggestions", "Proaktiv Verbesserungen vorschlagen", "user_experience", 1),
            ("error_prevention", "Vorherige Fehler vermeiden", "accuracy", 1),
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for name, desc, cat, active in defaults:
                cursor.execute("""
                    INSERT OR IGNORE INTO strategies 
                    (name, description, category, implemented_at, active)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, desc, cat, datetime.now().isoformat(), active))
            conn.commit()
    
    # ═══════════════════════════════════════════════════════════
    # OBSERVE: Performance tracken
    # ═══════════════════════════════════════════════════════════
    
    def record_performance(self, metric: PerformanceMetric):
        """Speichert Performance-Daten"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO performance_metrics 
                (session_id, task_type, tokens_used, time_seconds, success, 
                 user_satisfaction, error_count, strategy_used, outcome)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.session_id, metric.task_type, metric.tokens_used,
                metric.time_seconds, metric.success, metric.user_satisfaction,
                metric.error_count, metric.strategy_used, metric.outcome
            ))
            conn.commit()
        
        # Auto-analyse nach jedem 10. Eintrag
        if self._get_total_metrics() % 10 == 0:
            self._auto_analyze()
    
    def _get_total_metrics(self) -> int:
        """Gibt Anzahl der Metrics zurück"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM performance_metrics")
            return cursor.fetchone()[0]
    
    # ═══════════════════════════════════════════════════════════
    # ANALYZE: Muster erkennen
    # ═══════════════════════════════════════════════════════════
    
    def _auto_analyze(self):
        """Automatische Analyse der letzten Performance"""
        stats = self.get_recent_stats(days=7)
        
        # Wenn Erfolgsrate unter 80%, analysieren
        if stats['success_rate'] < 0.8:
            self._identify_failure_patterns()
        
        # Wenn Token-Nutzung steigt
        if stats['avg_tokens'] > 5000:
            self._suggest_token_optimization()
    
    def get_recent_stats(self, days: int = 7) -> Dict:
        """Performance der letzten X Tage"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT 
                    COUNT(*),
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END),
                    AVG(tokens_used),
                    AVG(time_seconds),
                    AVG(user_satisfaction)
                FROM performance_metrics
                WHERE timestamp > datetime('now', '-{days} days')
            """)
            
            total, successful, avg_tokens, avg_time, avg_satisfaction = cursor.fetchone()
            
            return {
                'total_tasks': total or 0,
                'success_rate': (successful / total) if total > 0 else 0,
                'avg_tokens': avg_tokens or 0,
                'avg_time': avg_time or 0,
                'avg_satisfaction': avg_satisfaction or 0
            }
    
    def _identify_failure_patterns(self):
        """Identifiziert häufige Fehler-Muster"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Finde Task-Types mit niedriger Success-Rate
            cursor.execute("""
                SELECT task_type, 
                       COUNT(*) as total,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM performance_metrics
                WHERE timestamp > datetime('now', '-7 days')
                GROUP BY task_type
                HAVING total > 3
            """)
            
            for row in cursor.fetchall():
                task_type, total, successful = row
                rate = successful / total if total > 0 else 0
                
                if rate < 0.7:
                    # Speichere als Learning
                    self.add_learning(
                        concept=f"{task_type}_low_success_rate",
                        context=f"Task type '{task_type}' has only {rate:.1%} success rate",
                        evidence=f"Failed {total - successful} out of {total} attempts",
                        confidence=0.8
                    )
    
    def _suggest_token_optimization(self):
        """Schlägt Token-Optimierungen vor"""
        self.add_learning(
            concept="high_token_usage",
            context="Average token usage above 5000 per task",
            evidence="Consider batching or more targeted queries",
            confidence=0.7
        )
    
    # ═══════════════════════════════════════════════════════════
    # LEARN: Wissen aufbauen
    # ═══════════════════════════════════════════════════════════
    
    def add_learning(self, concept: str, context: str, evidence: str, confidence: float = 0.5):
        """Fügt ein neues Learning hinzu oder verstärkt bestehendes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute(
                "SELECT id, times_observed, confidence FROM learnings WHERE concept = ?",
                (concept,)
            )
            row = cursor.fetchone()
            
            if row:
                # Update existing
                id_, times, old_conf = row
                new_times = times + 1
                new_conf = min(0.99, old_conf + (confidence * 0.1))  # Confidence wächst
                
                cursor.execute("""
                    UPDATE learnings 
                    SET times_observed = ?, 
                        confidence = ?,
                        last_reinforced = ?,
                        evidence = evidence || '\n' || ?
                    WHERE id = ?
                """, (new_times, new_conf, datetime.now().isoformat(), evidence, id_))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO learnings (concept, context, evidence, confidence)
                    VALUES (?, ?, ?, ?)
                """, (concept, context, evidence, confidence))
            
            conn.commit()
    
    def get_relevant_learnings(self, context: str, limit: int = 3) -> List[Dict]:
        """Holt relevante Learnings für einen Kontext"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Einfache Keyword-Matching (könnte mit Embeddings besser sein)
            keywords = context.lower().split()
            
            cursor.execute("""
                SELECT concept, context, evidence, confidence, times_observed
                FROM learnings
                WHERE confidence > 0.5
                ORDER BY times_observed DESC, confidence DESC
                LIMIT ?
            """, (limit,))
            
            return [
                {
                    'concept': row[0],
                    'context': row[1],
                    'evidence': row[2],
                    'confidence': row[3],
                    'times_observed': row[4]
                }
                for row in cursor.fetchall()
            ]
    
    # ═══════════════════════════════════════════════════════════
    # IMPROVE: Strategien anpassen
    # ═══════════════════════════════════════════════════════════
    
    def update_strategy_success(self, strategy_name: str, success: bool):
        """Aktualisiert Erfolgsrate einer Strategie"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT times_used, success_rate FROM strategies WHERE name = ?",
                (strategy_name,)
            )
            row = cursor.fetchone()
            
            if row:
                times, current_rate = row
                new_times = times + 1
                # Bayes-ähnliches Update
                new_rate = ((current_rate * times) + (1 if success else 0)) / new_times
                
                cursor.execute("""
                    UPDATE strategies 
                    SET times_used = ?, success_rate = ?
                    WHERE name = ?
                """, (new_times, new_rate, strategy_name))
                conn.commit()
    
    def get_best_strategies(self, category: str = None, limit: int = 3) -> List[Dict]:
        """Gibt die besten Strategien zurück"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if category:
                cursor.execute("""
                    SELECT name, description, success_rate, times_used
                    FROM strategies
                    WHERE active = 1 AND category = ?
                    ORDER BY success_rate DESC, times_used DESC
                    LIMIT ?
                """, (category, limit))
            else:
                cursor.execute("""
                    SELECT name, description, success_rate, times_used
                    FROM strategies
                    WHERE active = 1
                    ORDER BY success_rate DESC, times_used DESC
                    LIMIT ?
                """, (limit,))
            
            return [
                {
                    'name': row[0],
                    'description': row[1],
                    'success_rate': row[2],
                    'times_used': row[3]
                }
                for row in cursor.fetchall()
            ]
    
    def _load_active_strategies(self) -> List[str]:
        """Lädt Namen aktiver Strategien"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM strategies WHERE active = 1")
            return [row[0] for row in cursor.fetchall()]
    
    # ═══════════════════════════════════════════════════════════
    # DAILY REVIEW: Tägliche Selbst-Verbesserung
    # ═══════════════════════════════════════════════════════════
    
    def generate_daily_report(self) -> str:
        """Generiert täglichen Selbst-Verbesserungs-Report"""
        stats = self.get_recent_stats(days=1)
        best_strategies = self.get_best_strategies(limit=3)
        recent_learnings = self.get_relevant_learnings("general", limit=5)
        
        report = f"""
🤖 ROBOFABIO DAILY SELF-IMPROVEMENT REPORT
{'='*50}

📊 PERFORMANCE (Letzte 24h)
   Tasks: {stats['total_tasks']}
   Success Rate: {stats['success_rate']:.1%}
   Avg Tokens: {stats['avg_tokens']:.0f}
   Avg Time: {stats['avg_time']:.1f}s
   Satisfaction: {stats['avg_satisfaction']:.1f}/5

🎯 TOP STRATEGIES
"""
        for i, strat in enumerate(best_strategies, 1):
            report += f"   {i}. {strat['name']} ({strat['success_rate']:.1%})\n"
        
        report += "\n🧠 KEY LEARNINGS\n"
        for learning in recent_learnings:
            report += f"   • {learning['concept']} (conf: {learning['confidence']:.0%})\n"
        
        # Verbesserungs-Vorschläge
        report += "\n💡 SUGGESTED IMPROVEMENTS\n"
        
        if stats['success_rate'] < 0.8:
            report += "   ⚠️ Success rate low - review failure patterns\n"
        if stats['avg_tokens'] > 4000:
            report += "   💰 High token usage - optimize queries\n"
        if stats['avg_satisfaction'] < 4:
            report += "   😕 Satisfaction down - ask for feedback\n"
        
        return report
    
    def save_daily_summary(self):
        """Speichert tägliche Zusammenfassung"""
        stats = self.get_recent_stats(days=1)
        report = self.generate_daily_report()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO daily_summaries
                (date, total_tasks, success_rate, avg_tokens_per_task, avg_time_seconds, key_learnings)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().strftime('%Y-%m-%d'),
                stats['total_tasks'],
                stats['success_rate'],
                stats['avg_tokens'],
                stats['avg_time'],
                report
            ))
            conn.commit()


# ═══════════════════════════════════════════════════════════
# EINFACHE API FÜR INTEGRATION
# ═══════════════════════════════════════════════════════════

class RobofabioBrain:
    """
    Einfache API für den Haupt-Agenten
    """
    
    def __init__(self):
        self.engine = SelfImprovementEngine()
    
    def start_task(self, task_type: str, strategy: str = None) -> str:
        """Startet Tracking für einen Task"""
        import uuid
        session_id = str(uuid.uuid4())[:8]
        
        # Speichere Start-Zeit für später
        self._current_session = {
            'id': session_id,
            'task_type': task_type,
            'strategy': strategy or 'default',
            'start_time': datetime.now(),
            'tokens_start': self._estimate_tokens()
        }
        
        # Hole relevante Learnings
        learnings = self.engine.get_relevant_learnings(task_type)
        
        return session_id, learnings
    
    def end_task(self, session_id: str, success: bool, outcome: str, 
                 satisfaction: int = 3, errors: int = 0):
        """Beendet Tracking und speichert Ergebnis"""
        if not hasattr(self, '_current_session'):
            return
        
        session = self._current_session
        duration = (datetime.now() - session['start_time']).total_seconds()
        
        metric = PerformanceMetric(
            session_id=session_id,
            task_type=session['task_type'],
            tokens_used=self._estimate_tokens() - session.get('tokens_start', 0),
            time_seconds=duration,
            success=success,
            user_satisfaction=satisfaction,
            error_count=errors,
            strategy_used=session['strategy'],
            outcome=outcome
        )
        
        self.engine.record_performance(metric)
        
        # Update Strategy Success
        if session['strategy']:
            self.engine.update_strategy_success(session['strategy'], success)
    
    def _estimate_tokens(self) -> int:
        """Schätzt aktuelle Token-Nutzung (Platzhalter)"""
        # In echter Implementierung: Von LLM API holen
        return 0
    
    def learn(self, concept: str, context: str, evidence: str):
        """Erlaubt dem Agenten zu lernen"""
        self.engine.add_learning(concept, context, evidence)
    
    def get_insights(self) -> str:
        """Gibt aktuelle Insights"""
        return self.engine.generate_daily_report()


# Singleton für globalen Zugriff
_brain = None

def get_brain() -> RobofabioBrain:
    """Globaler Zugriff auf das Brain"""
    global _brain
    if _brain is None:
        _brain = RobofabioBrain()
    return _brain


if __name__ == "__main__":
    # Test
    brain = get_brain()
    
    # Simuliere einen Task
    session_id, learnings = brain.start_task("trading_analysis", "parallel_tools")
    print(f"Started session {session_id}")
    print(f"Relevant learnings: {len(learnings)}")
    
    # Task beenden
    brain.end_task(session_id, success=True, outcome="Profit +5%", satisfaction=5)
    
    # Report
    print("\n" + brain.get_insights())
