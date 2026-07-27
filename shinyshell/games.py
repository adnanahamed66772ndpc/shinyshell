"""Games and animations for Shell."""

import sys
import time
import random as _rand


from contextlib import contextmanager
class _GamesMixin:
    """Fun and games: slot, coin_flip, magic8, dice, spin_wheel, matrix, confetti, marquee, particles, pomodoro, timer, typewrite, rainbow."""

    def slot(self, spins: int = 3) -> list:
        """Slot machine animation. sh.slot(5)"""
        icons_list = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣", "⭐", "🔔"]
        print()
        for i in range(spins):
            result = [_rand.choice(icons_list) for _ in range(3)]
            sys.stdout.write(f"\r  [ {result[0]} | {result[1]} | {result[2]} ]    ")
            sys.stdout.flush()
            time.sleep(0.15)
        print()
        if result[0] == result[1] == result[2]:
            self.success(f"JACKPOT! {result[0]}{result[1]}{result[2]}")
        return result

    def coin_flip(self) -> str:
        """Animated coin flip. sh.coin_flip()"""
        faces = ["Heads 🪙", "Tails 🪙"]
        print()
        for _ in range(8):
            sys.stdout.write(f"\r  {_rand.choice(faces)}  ")
            sys.stdout.flush()
            time.sleep(0.08)
        result = _rand.choice(faces)
        print(f"\r  {result}  ")
        return result

    def magic8(self) -> str:
        """Magic 8 ball. sh.magic8()"""
        answers = ["It is certain ✅", "Yes 👍", "Ask again 🔄", "Cannot predict now 🤷", "No 👎", "Very doubtful ❌"]
        print()
        for _ in range(6):
            sys.stdout.write(f"\r  🎱 {_rand.choice(answers)}  ")
            sys.stdout.flush()
            time.sleep(0.1)
        result = _rand.choice(answers)
        print(f"\r  🎱 {result}  ")
        return result

    def dice(self, sides: int = 6, count: int = 1) -> list:
        """Animated dice roller. sh.dice(6, 2) → [3, 5]"""
        dice_faces = {
            1: ["┌─────┐", "│     │", "│  ●  │", "│     │", "└─────┘"],
            2: ["┌─────┐", "│ ●   │", "│     │", "│   ● │", "└─────┘"],
            3: ["┌─────┐", "│ ●   │", "│  ●  │", "│   ● │", "└─────┘"],
            4: ["┌─────┐", "│ ● ● │", "│     │", "│ ● ● │", "└─────┘"],
            5: ["┌─────┐", "│ ● ● │", "│  ●  │", "│ ● ● │", "└─────┘"],
            6: ["┌─────┐", "│ ● ● │", "│ ● ● │", "│ ● ● │", "└─────┘"],
        }
        results = [_rand.randint(1, sides) for _ in range(count)]
        results_str = ", ".join(str(r) for r in results)
        print()
        # Animation
        for _ in range(5):
            rand_faces = [_rand.choice(list(dice_faces.values())) for _ in range(min(count, 3))]
            for row in range(5):
                line = "  " + " ".join(f[row] for f in rand_faces)
                sys.stdout.write(f"\r{line}\n")
            sys.stdout.write(f"\033[{5 * min(count, 3)}A")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write(f"\033[{5 * min(count, 3)}B")
        if count <= 3:
            real_faces = [dice_faces.get(r, dice_faces[1]) for r in results]
            for row in range(5):
                print("  " + " ".join(f[row] for f in real_faces))
        self.success(f"Rolled: {results_str}")
        return results

    def spin_wheel(self, options: list) -> str:
        """Spin the wheel. sh.spin_wheel(['Prize A','Prize B','Prize C'])"""
        print()
        for _ in range(15):
            sys.stdout.write(f"\r  🎡 {_rand.choice(options)}  ")
            sys.stdout.flush()
            time.sleep(0.08)
        result = _rand.choice(options)
        print(f"\r  🎡 {self._style(result, 'bold', color='green')}  ")
        return result

    def matrix(self, duration: float = 5.0) -> None:
        """Matrix-style rain animation. sh.matrix(10)"""
        chars = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃ0123456789"
        width = min(self._width - 4, 60)
        cols = [0] * width
        print()
        start = time.time()
        try:
            while time.time() - start < duration:
                line = "  "
                for i in range(width):
                    if cols[i] > 0:
                        line += self._style(_rand.choice(chars), color="green")
                        cols[i] -= 1
                    elif _rand.random() < 0.05:
                        cols[i] = _rand.randint(5, 15)
                        line += self._style(_rand.choice(chars), "bold", color="bright_green")
                    else:
                        line += " "
                sys.stdout.write(f"\r{line}")
                sys.stdout.flush()
                time.sleep(0.05)
        except KeyboardInterrupt:
            pass
        print("\n")

    def confetti(self, duration: float = 3.0) -> None:
        """Confetti animation. sh.confetti(5)"""
        confetti_chars = "🎉🎊✨🌟💫⭐🎈🎀"
        print()
        start = time.time()
        try:
            while time.time() - start < duration:
                line = "  " + " ".join(_rand.choice(confetti_chars) + _rand.choice([" ", "  "]) for _ in range(20))
                sys.stdout.write(f"\r{line}")
                sys.stdout.flush()
                time.sleep(0.15)
        except KeyboardInterrupt:
            pass
        print()

    def marquee(self, text: str, width: int = 40, duration: float = 5.0) -> None:
        """Scrolling marquee. sh.marquee('Breaking News!')"""
        text = "   " + text + "   ★   "
        start = time.time()
        tlen = len(text)
        print()
        try:
            while time.time() - start < duration:
                for offset in range(tlen):
                    visible = (text * 3)[offset:offset + width]
                    sys.stdout.write(f"\r  {self._style(visible, color='cyan')}")
                    sys.stdout.flush()
                    time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        print()

    def particles(self, duration: float = 5.0) -> None:
        """Particle animation. sh.particles(5)"""
        h, w = 15, 40
        particles = [(w // 2, 0, _rand.random() * 0.3 + 0.1) for _ in range(20)]
        print()
        start = time.time()
        try:
            while time.time() - start < duration:
                new_p = []
                sys.stdout.write("\033[J")
                for x, y, speed in particles:
                    y += speed
                    if y < h:
                        new_p.append((x + (_rand.random() - 0.5) * 0.5, y, speed))
                        px, py = int(x), int(y)
                        if 0 <= py < h and 0 <= px < w:
                            sys.stdout.write(f"\033[{py + 1};{px * 2 + 1}H{self._style('•', color='yellow')}")
                if len(new_p) < 20:
                    new_p.append((w // 2 + (_rand.random() - 0.5) * 10, 0, _rand.random() * 0.3 + 0.1))
                particles = new_p
                sys.stdout.flush()
                time.sleep(0.08)
        except KeyboardInterrupt:
            pass
        print()

    def pomodoro(self, work_min: int = 25, break_min: int = 5, cycles: int = 4) -> None:
        """Pomodoro timer. sh.pomodoro(25, 5, 4)"""
        for cycle in range(1, cycles + 1):
            self.header(f"🍅 Pomodoro {cycle}/{cycles} — WORK ({work_min}min)")
            self._countdown_timer(work_min * 60, "Working")
            if cycle < cycles:
                self.success(f"Break time! ({break_min}min)")
                self._countdown_timer(break_min * 60, "Break")
        self.header("🎉 ALL DONE! Great work!")

    def _countdown_timer(self, seconds: int, label: str):
        for remaining in range(seconds, 0, -1):
            m, s = divmod(remaining, 60)
            sys.stdout.write(f"\r  ⏱️  {label}: {m:02d}:{s:02d} remaining  ")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r" + " " * 40 + "\r")
        sys.stdout.flush()

    def timer(self, seconds: int, label: str = "Timer") -> None:
        """Count-down timer. sh.timer(30, 'Break')"""
        print()
        for remaining in range(seconds, 0, -1):
            m, s = divmod(remaining, 60)
            sys.stdout.write(f"\r  ⏱️  {label}: {m:02d}:{s:02d}  ")
            sys.stdout.flush()
            time.sleep(1)
        print(f"\r  🔔 {label} done! {' ' * 20}\n")
        self.audio_beep(3)

    def typewrite(self, text: str, speed: float = 0.03) -> None:
        """Typewriter animation effect. sh.typewrite('Hello World', speed=0.05)"""
        print()
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(speed)
        print()

    def rainbow(self, text: str) -> None:
        """Rainbow gradient text. sh.rainbow('Hello World')"""
        colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
        result = ""
        for i, ch in enumerate(text):
            if ch.strip():
                result += self._style(ch, color=colors[i % len(colors)])
            else:
                result += ch
        print(f"\n  {result}\n")
