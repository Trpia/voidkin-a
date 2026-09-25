from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

import os
from datetime import datetime

# Try to import moviepy (optional - app still works without it)
try:
    from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False

Window.clearcolor = get_color_from_hex("#0f0f13")


class VoidkinAI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12),
            **kwargs
        )

        # Title
        title = Label(
            text="VOIDKIN AI",
            font_size=dp(34),
            bold=True,
            color=get_color_from_hex("#e0e0ff"),
            size_hint_y=None,
            height=dp(50)
        )
        self.add_widget(title)

        subtitle = Label(
            text="FREE AI VIDEO STUDIO",
            font_size=dp(15),
            color=get_color_from_hex("#a0a0c0"),
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(subtitle)

        # Prompt
        self.prompt = TextInput(
            hint_text="Describe your video...",
            multiline=True,
            size_hint_y=None,
            height=dp(120),
            background_color=get_color_from_hex("#1a1a22"),
            foreground_color=get_color_from_hex("#ffffff"),
            cursor_color=get_color_from_hex("#7c7cff"),
            padding=dp(12)
        )
        self.add_widget(self.prompt)

        # Format + Duration
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(55), spacing=dp(10))

        self.format = Spinner(
            text="9:16 Portrait",
            values=["9:16 Portrait", "16:9 Landscape", "1:1 Square"],
            size_hint_x=0.6,
            background_color=get_color_from_hex("#222233")
        )
        row.add_widget(self.format)

        self.duration = Spinner(
            text="5s",
            values=["3s", "5s", "8s", "10s"],
            size_hint_x=0.4,
            background_color=get_color_from_hex("#222233")
        )
        row.add_widget(self.duration)
        self.add_widget(row)

        # Style
        self.style = Spinner(
            text="Cinematic",
            values=["Cinematic", "Anime", "Cyberpunk", "Minimal", "Dreamy", "Documentary"],
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex("#222233")
        )
        self.add_widget(self.style)

        # Generate button
        self.generate = Button(
            text="GENERATE VIDEO",
            size_hint_y=None,
            height=dp(60),
            background_color=get_color_from_hex("#5b5bff"),
            background_normal="",
            bold=True,
            font_size=dp(18)
        )
        self.generate.bind(on_press=self.start_generation)
        self.add_widget(self.generate)

        # Status
        self.status = Label(
            text="Ready • Enter a prompt and hit GENERATE",
            font_size=dp(15),
            color=get_color_from_hex("#c0c0e0"),
            halign="center",
            valign="middle"
        )
        self.status.bind(size=lambda *x: setattr(self.status, 'text_size', (self.status.width - 20, None)))
        self.add_widget(self.status)

        self.is_generating = False

    def start_generation(self, instance):
        if self.is_generating:
            return

        prompt = self.prompt.text.strip()
        if not prompt:
            self.status.text = "⚠️ Please enter a prompt first."
            return

        self.is_generating = True
        self.generate.disabled = True
        self.generate.text = "GENERATING..."
        self.status.text = "🎬 Preparing video..."

        Clock.schedule_once(lambda dt: self.generate_video(prompt), 0.1)

    def generate_video(self, prompt):
        try:
            if not HAS_MOVIEPY:
                self.status.text = (
                    "✅ Prompt received!\n\n"
                    f"Format: {self.format.text}\n"
                    f"Duration: {self.duration.text}\n"
                    f"Style: {self.style.text}\n\n"
                    f"Prompt:\n{prompt}\n\n"
                    "(Install moviepy for real video generation)"
                )
                return

            # Real video generation
            format_map = {
                "9:16 Portrait": (1080, 1920),
                "16:9 Landscape": (1920, 1080),
                "1:1 Square": (1080, 1080)
            }
            size = format_map.get(self.format.text, (1080, 1920))
            duration = int(self.duration.text.replace("s", ""))
            style = self.style.text

            os.makedirs("voidkin_outputs", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"voidkin_outputs/voidkin_{timestamp}.mp4"

            bg_colors = {
                "Cinematic": (15, 15, 25),
                "Anime": (30, 20, 50),
                "Cyberpunk": (10, 5, 30),
                "Minimal": (20, 20, 20),
                "Dreamy": (25, 15, 35),
                "Documentary": (18, 18, 18)
            }
            bg = bg_colors.get(style, (15, 15, 25))

            bg_clip = ColorClip(size=size, color=bg, duration=duration)

            title_clip = TextClip(
                "VOIDKIN AI",
                fontsize=48,
                color="white",
                method="caption",
                size=(size[0] - 80, None)
            ).set_position(("center", 80)).set_duration(duration)

            wrapped = self._wrap_text(prompt, 35)
            prompt_clip = TextClip(
                wrapped,
                fontsize=36,
                color="white",
                method="caption",
                size=(size[0] - 100, None),
                align="center"
            ).set_position("center").set_duration(duration)

            style_clip = TextClip(
                f"{style}  •  {self.format.text}  •  {duration}s",
                fontsize=22,
                color="#aaaaaa"
            ).set_position(("center", size[1] - 100)).set_duration(duration)

            final = CompositeVideoClip([bg_clip, title_clip, prompt_clip, style_clip])
            final.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio=False,
                preset="ultrafast",
                logger=None
            )

            self.status.text = (
                f"✅ VIDEO READY!\n\n"
                f"Saved to:\n{output_path}\n\n"
                f"Format: {self.format.text}\n"
                f"Style: {style}"
            )

        except Exception as e:
            self.status.text = f"❌ Error:\n{str(e)}"
        finally:
            self.is_generating = False
            self.generate.disabled = False
            self.generate.text = "GENERATE VIDEO"

    def _wrap_text(self, text, max_chars):
        words = text.split()
        lines, current = [], []
        for w in words:
            if len(" ".join(current + [w])) <= max_chars:
                current.append(w)
            else:
                if current:
                    lines.append(" ".join(current))
                current = [w]
        if current:
            lines.append(" ".join(current))
        return "\n".join(lines)


class VoidkinApp(App):
    def build(self):
        self.title = "Voidkin AI"
        return VoidkinAI()


if __name__ == "__main__":
    VoidkinApp().run()
