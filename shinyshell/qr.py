"""QR code and image display for Shell."""

import hashlib
from contextlib import contextmanager


class _QRMixin:
    """QR code and ASCII image display: qr, image."""

    def qr(self, data: str, title: str | None = None) -> None:
        """Generate a QR code in the terminal.

        Uses the `qrcode` library if installed for real QR codes.
        Falls back to a deterministic hash-based pattern (stdlib only).
        """
        try:
            import qrcode
            self._qr_real(data, title)
        except ImportError:
            self._qr_stdlib(data, title)

    def _qr_real(self, data: str, title: str | None = None) -> None:
        """Real QR code using qrcode library (optional dependency)."""
        import qrcode
        qr = qrcode.QRCode(border=2)
        qr.add_data(data)
        qr.make(fit=True)
        matrix = qr.modules
        size = len(matrix)

        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        for row in matrix:
            line = "  "
            for cell in row:
                line += self._style("██", color="white", bg="black") if cell else "  "
            print(line)
        print()

    def _qr_stdlib(self, data: str, title: str | None = None) -> None:
        """Fallback: hash-based deterministic pattern (no qrcode library needed)."""
        h = hashlib.sha256(data.encode()).hexdigest()
        size = 21
        matrix = [[False] * size for _ in range(size)]

        for i in range(size):
            for j in range(size):
                idx = (i * size + j) % len(h)
                matrix[i][j] = int(h[idx], 16) > 7

        for r, c in [(0, 0), (0, size - 7), (size - 7, 0)]:
            for i in range(7):
                for j in range(7):
                    if r + i < size and c + j < size:
                        edge = i == 0 or i == 6 or j == 0 or j == 6
                        inner = 2 <= i <= 4 and 2 <= j <= 4
                        matrix[r + i][c + j] = edge or inner

        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        for row in matrix:
            line = "  "
            for cell in row:
                line += self._style("██", color="white", bg="black") if cell else "  "
            print(line)
        print()

    def image(self, path: str, width: int = 80) -> None:
        """Display an image as ASCII art. Requires Pillow.

        Install: pip install shinyshell[image]
        """
        try:
            from PIL import Image
        except ImportError:
            self.error("Pillow not installed. Run: pip install shinyshell[image]")
            return
        try:
            img = Image.open(path).convert("L")
            aspect = img.height / img.width
            h = int(aspect * width * 0.55)
            img = img.resize((width, h))
            chars = "@%#*+=-:. "
            print()
            for y in range(h):
                line = "".join(
                    chars[int(img.getpixel((x, y)) / 255 * (len(chars) - 1))]
                    for x in range(width)
                )
                print(f"  {line}")
            print()
        except Exception as e:
            self.error(f"Cannot load image: {e}")
