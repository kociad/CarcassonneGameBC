import pygame
from ui.components.inputField import InputField
from ui.components.toast import Toast
import typing


class Slider:
    """A slider UI component for selecting a numeric value."""

    def __init__(self, rect: pygame.Rect, font, minValue: float, maxValue: float, initialValue: float = None, value: float = None, onChange: typing.Callable = None) -> None:
        """
        Initialize the slider.
        
        Args:
            rect: Rectangle defining slider position and size
            font: Font to use for rendering
            minValue: Minimum value of the slider
            maxValue: Maximum value of the slider
            initialValue: Initial value (alternative to value)
            value: Initial value
            onChange: Function to call when value changes
        """
        self.rect = pygame.Rect(rect)
        self.font = font
        self.minValue = minValue
        self.maxValue = maxValue
        self.value = value if value is not None else (initialValue if initialValue is not None else minValue)
        self.onChange = onChange
        self.lastReportedValue = self.value
        self.disabled = False
        self.handleRadius = 10
        self.dragging = False
        self.bgColor = (200, 200, 200)
        self.fgColor = (100, 100, 255)
        self.handleColor = (255, 255, 255)
        self.borderColor = (0, 0, 0)
        self.disabledBgColor = (100, 100, 100)
        self.disabledFgColor = (60, 60, 60)
        self.disabledHandleColor = (150, 150, 150)
        self.disabledBorderColor = (80, 80, 80)
        self.toastQueue = []
        self.activeToast = None
        inputFieldWidth = 60
        inputFieldHeight = self.rect.height
        inputX = self.rect.right + 10
        inputY = self.rect.y
        self.inputField = InputField(
            rect=(inputX, inputY, inputFieldWidth, inputFieldHeight),
            font=font,
            initialText=str(self.value),
            onTextChange=None,
            numeric=True,
            minValue=minValue,
        )

    def _validateAndApplyInput(self) -> None:
        """Validate input field value and apply if valid."""
        inputText = self.inputField.getText().strip()
        if not inputText:
            self.inputField.setText(str(self.value))
            return
        try:
            newValue = int(inputText)
            if newValue < self.minValue:
                self._showToast(f"Value must be at least {self.minValue}", "error")
                self.inputField.setText(str(self.value))
            elif newValue > self.maxValue:
                self._showToast(f"Value must be at most {self.maxValue}", "error")
                self.inputField.setText(str(self.value))
            else:
                if newValue != self.value:
                    self.value = newValue
                    if newValue != self.lastReportedValue:
                        self.lastReportedValue = newValue
                        if self.onChange:
                            self.onChange(newValue)
        except ValueError:
            self.inputField.setText(str(self.value))

    def _showToast(self, message: str, toastType: str = "info") -> None:
        """
        Show toast notification.
        
        Args:
            message: Message to display
            toastType: Type of toast notification
        """
        if self.activeToast and self.activeToast.message == message:
            return
        if any(t.message == message for t in self.toastQueue):
            return
        toast = Toast(message, type=toastType)
        self.toastQueue.append(toast)

    def setDisabled(self, disabled: bool) -> None:
        """
        Enable or disable the slider.
        
        Args:
            disabled: Whether to disable the slider
        """
        self.disabled = disabled
        self.inputField.setDisabled(disabled)
        if disabled:
            self.dragging = False

    def isDisabled(self) -> bool:
        """Check if the slider is disabled."""
        return self.disabled

    def handleEvent(self, event: pygame.event.Event, yOffset: int = 0) -> None:
        """
        Handle a pygame event for the slider.
        
        Args:
            event: Pygame event to handle
            yOffset: Vertical offset for event detection
        """
        wasActive = self.inputField.active
        self.inputField.handleEvent(event, yOffset=yOffset)
        if wasActive and not self.inputField.active:
            self._validateAndApplyInput()
        if (self.inputField.active and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
            self._validateAndApplyInput()
        if self.disabled:
            return
        shiftedRect = self.rect.move(0, yOffset)
        handleRect = self._handleRect(yOffset)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if handleRect.collidepoint(event.pos):
                self.dragging = True
            elif shiftedRect.collidepoint(event.pos):
                relX = min(max(event.pos[0], shiftedRect.left), shiftedRect.right)
                ratio = (relX - shiftedRect.left) / shiftedRect.width
                newValue = int(self.minValue + ratio * (self.maxValue - self.minValue))
                if newValue != self.value:
                    self.value = newValue
                    self.inputField.setText(str(newValue))
                    if newValue != self.lastReportedValue:
                        self.lastReportedValue = newValue
                        if self.onChange:
                            self.onChange(newValue)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            relX = min(max(event.pos[0], shiftedRect.left), shiftedRect.right)
            ratio = (relX - shiftedRect.left) / shiftedRect.width
            newValue = int(self.minValue + ratio * (self.maxValue - self.minValue))
            if newValue != self.value:
                self.value = newValue
                self.inputField.setText(str(newValue))
                if newValue != self.lastReportedValue:
                    self.lastReportedValue = newValue
                    if self.onChange:
                        self.onChange(newValue)

    def _handleRect(self, yOffset: int = 0) -> pygame.Rect:
        """
        Get the rectangle for the slider handle.
        
        Args:
            yOffset: Vertical offset
            
        Returns:
            Rectangle for the slider handle
        """
        handleX = self.rect.left + ((self.value - self.minValue) / (self.maxValue - self.minValue)) * self.rect.width
        handleY = self.rect.centery + yOffset
        return pygame.Rect(
            handleX - self.handleRadius,
            handleY - self.handleRadius,
            self.handleRadius * 2,
            self.handleRadius * 2
        )

    def draw(self, surface: pygame.Surface, yOffset: int = 0) -> None:
        """
        Draw the slider on the given surface.
        
        Args:
            surface: Surface to draw on
            yOffset: Vertical offset for drawing
        """
        shiftedRect = self.rect.move(0, yOffset)
        if self.disabled:
            bgColor = self.disabledBgColor
            fgColor = self.disabledFgColor
            handleColor = self.disabledHandleColor
            borderColor = self.disabledBorderColor
        else:
            bgColor = self.bgColor
            fgColor = self.fgColor
            handleColor = self.handleColor
            borderColor = self.borderColor
        pygame.draw.rect(surface, bgColor, shiftedRect)
        pygame.draw.rect(surface, borderColor, shiftedRect, 1)
        fillWidth = ((self.value - self.minValue) / (self.maxValue - self.minValue)) * shiftedRect.width
        pygame.draw.rect(surface, fgColor, pygame.Rect(shiftedRect.left, shiftedRect.top, fillWidth, shiftedRect.height))
        handleRect = self._handleRect(yOffset)
        pygame.draw.circle(surface, handleColor, handleRect.center, self.handleRadius)
        pygame.draw.circle(surface, borderColor, handleRect.center, self.handleRadius, 1)
        self.inputField.draw(surface, yOffset=yOffset)
        if not self.activeToast and self.toastQueue:
            self.activeToast = self.toastQueue.pop(0)
            self.activeToast.start()
        if self.activeToast:
            self.activeToast.draw(surface)
            if self.activeToast.isExpired():
                self.activeToast = None

    def getValue(self) -> float:
        """Get the current value of the slider."""
        return self.value

    def setValue(self, newValue: float) -> None:
        """
        Set the slider value.
        
        Args:
            newValue: New value to set
        """
        self.value = max(self.minValue, min(self.maxValue, newValue))
        self.lastReportedValue = self.value
        self.inputField.setText(str(self.value))

    def setMinValue(self, newMinValue: float) -> None:
        """
        Update the minimum value of the slider.
        
        Args:
            newMinValue: New minimum value
        """
        self.minValue = newMinValue
        self.inputField.minValue = newMinValue
        if self.value < self.minValue:
            self.value = self.minValue
            self.lastReportedValue = self.value