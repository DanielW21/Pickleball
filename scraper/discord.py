import requests
import json
from datetime import datetime

class DiscordNotifier:
    def __init__(self, config):
        self.posts_webhook = config["DISCORD_POSTS"]  
        self.logs_webhook = config["DISCORD_LOGS"]  
        self.user_id = config.get("DISCORD_UID")   

    def send_notification(self, available_events):
        """Send to appropriate channel based on content"""
        scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if available_events:
            self._send_logs_message(f"✅ Scan at {scan_time}: ")
            self._send_posts_message(available_events)
        else:
            self._send_logs_message(f"🕒 Scan at {scan_time}: No spots available")

    def _send_posts_message(self, events):
        """Rich embed for the posts channel"""
        embeds = []
        for event in events:
            embed = {
                "title": f"🏓 {event['name']}",
                "color": 0x00FF00,  # Green
                "fields": [
                    {"name": "📅 Date", "value": event["date"], "inline": True},
                    {"name": "⏰ Time", "value": event["time"], "inline": True},
                    {"name": "📍 Location", "value": event["location"], "inline": False},
                    {"name": "🟢 Spots", "value": event["spots_left"], "inline": True},
                ],
                "url": event["booking_link"]
            }
            embeds.append(embed)

        content = "🎉 New spots available!"
        if self.user_id:
            content = f"<@{self.user_id}> {content}"

        self._send_discord_message(
            webhook_url=self.posts_webhook,
            content=content,
            embeds=embeds
        )

    def _send_logs_message(self, message):
        """Plain text for the logs channel"""
        self._send_discord_message(
            webhook_url=self.logs_webhook,
            content=message
        )

    def _send_discord_message(self, webhook_url, content, embeds=None):
        """Generic message sender"""
        payload = {"content": content}
        if embeds:
            payload["embeds"] = embeds

        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            return response.status_code == 204
        except Exception as e:
            print(f"❌ Discord message failed: {e}")
            return False