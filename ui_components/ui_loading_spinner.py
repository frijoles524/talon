from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF, QSize, QEvent
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QWidget



class UILoadingSpinner(QWidget):
	def __init__(self, parent=None, radius=24, line_length=10, line_width=3, lines=12, duration_ms=900, dim_background=False, dim_opacity=0.0, block_input=True):
		super().__init__(parent)
		self._radius = max(6, int(radius))
		self._line_length = max(4, int(line_length))
		self._line_width = max(1, int(line_width))
		self._lines = max(8, int(lines))
		self._duration_ms = max(240, int(duration_ms))
		self._dim_background = bool(dim_background)
		self._dim_opacity = min(0.95, max(0.0, float(dim_opacity)))
		self._block_input = bool(block_input)
		self._step = 0
		self._timer = QTimer(self)
		self._timer.timeout.connect(self._advance)
		self._interval = max(10, int(self._duration_ms / self._lines))
		self.setAttribute(Qt.WA_NoSystemBackground, True)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.setAttribute(Qt.WA_TransparentForMouseEvents, not self._block_input)
		self.setFocusPolicy(Qt.NoFocus)
		if parent is not None:
			parent.installEventFilter(self)
			self.setGeometry(parent.rect())
		self.hide()

	def sizeHint(self):
		d = (self._radius + self._line_length) * 2 + self._line_width * 2
		return QSize(d, d)

	def start(self):
		if not self._timer.isActive():
			self._timer.start(self._interval)
		self.show()
		self.raise_()
		self.update()

	def stop(self):
		self._timer.stop()
		self.hide()

	def isRunning(self):
		return self._timer.isActive()

	def setDimBackground(self, enabled):
		self._dim_background = bool(enabled)
		self.update()

	def setDimOpacity(self, opacity):
		self._dim_opacity = min(0.95, max(0.0, float(opacity)))
		self.update()

	def setBlockInput(self, block):
		self._block_input = bool(block)
		self.setAttribute(Qt.WA_TransparentForMouseEvents, not self._block_input)

	def eventFilter(self, obj, event):
		if obj is self.parent():
			t = event.type()
			if t in (QEvent.Resize, QEvent.Move, QEvent.Show):
				self.setGeometry(obj.rect())
		return False

	def _advance(self):
		self._step = (self._step + 1) % self._lines
		self.update()

	def paintEvent(self, _):
		if not self.isVisible():
			return
		p = QPainter(self)
		p.setRenderHint(QPainter.Antialiasing, True)
		if self._dim_background and self._dim_opacity > 0.0:
			p.fillRect(self.rect(), QColor(0, 0, 0, int(255 * self._dim_opacity)))
		cx = self.width() / 2.0
		cy = self.height() / 2.0
		p.translate(QPointF(cx, cy))
		outer = max(6.0, min(self._radius, min(self.width(), self.height()) / 2.0 - self._line_length - self._line_width))
		for i in range(self._lines):
			alpha = int(255 * ((i + 1) / self._lines))
			idx = (self._step + i) % self._lines
			p.save()
			p.rotate(360.0 * idx / self._lines)
			p.setPen(Qt.NoPen)
			p.setBrush(QColor(255, 255, 255, alpha))
			x = outer
			y = -self._line_width / 2.0
			rect = QRectF(x, y, self._line_length, self._line_width)
			p.drawRoundedRect(rect, self._line_width / 2.0, self._line_width / 2.0)
			p.restore()
		p.end()