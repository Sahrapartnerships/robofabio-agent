# Upload-Post API Integration für Robofabio
# TikTok + Instagram Automation - 100% API-basiert

import requests
import os
import json
from typing import List, Optional
from datetime import datetime, timedelta

class SocialMediaPoster:
    """
    100% automatisierte Social Media Posting via Upload-Post API
    Unterstützt: TikTok, Instagram, YouTube, Facebook, X, Threads, etc.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.upload-post.com/api"
        self.headers = {
            "Authorization": f"Apikey {api_key}"
        }
    
    def upload_to_tiktok(
        self,
        video_path: str,
        title: str,
        description: str = "",
        hashtags: List[str] = None,
        schedule_time: Optional[datetime] = None
    ) -> dict:
        """
        Postet ein Video auf TikTok via API
        
        Args:
            video_path: Pfad zur Video-Datei
            title: Titel des Posts
            description: Beschreibung
            hashtags: Liste der Hashtags
            schedule_time: Wann gepostet werden soll (None = sofort)
        """
        url = f"{self.base_url}/upload"
        
        # Erstelle Caption mit Hashtags
        caption = description
        if hashtags:
            caption += "\n\n" + " ".join([f"#{tag}" for tag in hashtags])
        
        files = {
            'video': open(video_path, 'rb')
        }
        
        data = {
            'title': title,
            'caption': caption,
            'platform[]': 'tiktok',
            'user': 'default'
        }
        
        if schedule_time:
            data['schedule'] = schedule_time.isoformat()
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
        finally:
            files['video'].close()
    
    def upload_carousel_to_instagram(
        self,
        image_paths: List[str],
        caption: str,
        hashtags: List[str] = None,
        schedule_time: Optional[datetime] = None
    ) -> dict:
        """
        Postet einen Carousel (mehrere Bilder) auf Instagram
        
        Args:
            image_paths: Liste der Bild-Pfade (max 10 für Instagram)
            caption: Caption Text
            hashtags: Liste der Hashtags
            schedule_time: Zeitplan
        """
        url = f"{self.base_url}/upload"
        
        # Füge Hashtags zur Caption hinzu
        if hashtags:
            caption += "\n\n" + " ".join([f"#{tag}" for tag in hashtags])
        
        files = []
        for i, path in enumerate(image_paths[:10]):  # Instagram max 10
            files.append(('images[]', open(path, 'rb')))
        
        data = {
            'caption': caption,
            'platform[]': 'instagram',
            'user': 'default'
        }
        
        if schedule_time:
            data['schedule'] = schedule_time.isoformat()
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
        finally:
            for _, f in files:
                f.close()
    
    def schedule_weekend_posts(self, posts_config: List[dict]) -> List[dict]:
        """
        Plant alle Weekend-Posts für Elternratgeber
        
        posts_config: Liste mit:
            - platform: 'tiktok' | 'instagram'
            - content_path: Pfad zu Video/Bildern
            - caption: Text
            - hashtags: Liste
            - schedule_time: datetime
        """
        results = []
        
        for post in posts_config:
            try:
                if post['platform'] == 'tiktok':
                    result = self.upload_to_tiktok(
                        video_path=post['content_path'],
                        title=post.get('title', ''),
                        description=post['caption'],
                        hashtags=post.get('hashtags', []),
                        schedule_time=post['schedule_time']
                    )
                elif post['platform'] == 'instagram':
                    result = self.upload_carousel_to_instagram(
                        image_paths=post['content_paths'],
                        caption=post['caption'],
                        hashtags=post.get('hashtags', []),
                        schedule_time=post['schedule_time']
                    )
                
                results.append({
                    'status': 'success',
                    'platform': post['platform'],
                    'schedule': post['schedule_time'].isoformat(),
                    'response': result
                })
                
            except Exception as e:
                results.append({
                    'status': 'error',
                    'platform': post['platform'],
                    'error': str(e)
                })
        
        return results
    
    def get_analytics(self, platform: str = None) -> dict:
        """Holt Analytics von allen Plattformen"""
        url = f"{self.base_url}/analytics"
        
        params = {}
        if platform:
            params['platform'] = platform
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()


# ===== ELTERNRATGEBER WEEKEND LAUNCH CONFIG =====

def get_weekend_schedule() -> List[dict]:
    """
    Konfiguration für alle Weekend Posts
    """
    base_time = datetime.now()
    
    return [
        # === TIKTOK POSTS ===
        {
            'platform': 'tiktok',
            'content_path': '/root/life/elternratgeber-system/tiktok_carousels/batch_1/video_1.mp4',
            'title': '3 Fehler bei Schulstress',
            'caption': 'Diese 3 Fehler machen 90% der Eltern... 😰',
            'hashtags': ['schulstress', 'elternratgeber', 'lernen', 'schulkind'],
            'schedule_time': base_time + timedelta(hours=2)  # Heute Abend
        },
        {
            'platform': 'tiktok',
            'content_path': '/root/life/elternratgeber-system/tiktok_carousels/batch_2/video_2.mp4',
            'title': 'Cornell Methode',
            'caption': 'Die Cornell-Methode: So lernen Top-Schüler 📚',
            'hashtags': ['lernmethoden', 'schulstress', 'elternratgeber'],
            'schedule_time': base_time + timedelta(days=1, hours=10)  # Morgen
        },
        
        # === INSTAGRAM POSTS ===
        {
            'platform': 'instagram',
            'content_paths': [
                '/root/life/elternratgeber-system/tiktok_carousels/batch_1/slide_01.png',
                '/root/life/elternratgeber-system/tiktok_carousels/batch_1/slide_02.png',
                '/root/life/elternratgeber-system/tiktok_carousels/batch_1/slide_03.png',
                '/root/life/elternratgeber-system/tiktok_carousels/batch_1/slide_04.png',
                '/root/life/elternratgeber-system/tiktok_carousels/batch_1/slide_05.png',
            ],
            'caption': '''🚀 ENDLICH LIVE! 🚀

Nach Monaten der Arbeit ist er da:
"Schulstress Befreit PLUS"

Der komplette Ratgeber für entspannte Eltern und erfolgreiche Kinder.

Was du lernst:
✅ Die 3 größten Kommunikationsfehler
✅ 5 bewährte Lernmethoden
✅ Die 4-P-S-Formel für Konzentration
✅ Sofort umsetzbare Templates

⚡ NUR DIESES WOCHENENDE:
40% Rabatt → Nur 29€

Link in Bio 👆''',
            'hashtags': ['schulstress', 'elternratgeber', 'lernmethoden', 'konzentration'],
            'schedule_time': base_time + timedelta(hours=1)
        },
    ]


# ===== USAGE EXAMPLE =====
if __name__ == "__main__":
    # Lade API Key aus Umgebungsvariable
    api_key = os.getenv('UPLOAD_POST_API_KEY')
    
    if not api_key:
        print("❌ UPLOAD_POST_API_KEY nicht gesetzt")
        print("👉 Melde dich an bei https://www.upload-post.com")
        print("👉 Hole deinen API Key")
        print("👉 Setze: export UPLOAD_POST_API_KEY='dein-key'")
        exit(1)
    
    # Initialisiere Poster
    poster = SocialMediaPoster(api_key)
    
    # Hole Weekend Schedule
    posts = get_weekend_schedule()
    
    # Plane alle Posts
    print(f"🚀 Plane {len(posts)} Posts...")
    results = poster.schedule_weekend_posts(posts)
    
    # Zeige Ergebnisse
    for result in results:
        if result['status'] == 'success':
            print(f"✅ {result['platform'].upper()}: Geplant für {result['schedule']}")
        else:
            print(f"❌ {result['platform'].upper()}: {result['error']}")
    
    print("\n🎉 Weekend Launch ist geplant!")
