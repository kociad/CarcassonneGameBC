import pygame
import time
from typing import List, Tuple
import typing
from utils.settingsManager import settingsManager


class GameLogEntry:
    """Represents a single entry in the game log."""

    def __init__(self, message: str, level: str = "INFO", timestamp: float = None) -> None:
        """
        Initialize a game log entry.
        
        Args:
            message: Log message
            level: Log level (INFO, DEBUG, SCORING, WARNING, ERROR)
            timestamp: Timestamp for the entry
        """
        self.message = message
        self.level = level
        self.timestamp = timestamp or time.time()

    def getFormattedTime(self) -> str:
        """Get the formatted timestamp for the log entry."""
        return time.strftime("%H:%M:%S", time.localtime(self.timestamp))


class GameLog:
    """Handles the display and management of the game log UI overlay."""

    def __init__(self) -> None:
        """Initialize the game log."""
        self.maxEntries = settingsManager.get("GAME_LOG_MAX_ENTRIES", 2000)
        self.entries: List[GameLogEntry] = []
        self.visible = False
        self.scrollOffset = 0
        self.font = pygame.font.Font(None, 28)
        self.titleFont = pygame.font.Font(None, 36)
        self.levelColors = {
            "INFO": (240, 240, 240),
            "DEBUG": (150, 200, 255),
            "SCORING": (255, 255, 0),
            "WARNING": (255, 220, 100),
            "ERROR": (255, 120, 120),
        }
        self.levelBackgrounds = {
            "INFO": (0, 0, 0, 0),
            "DEBUG": (0, 50, 100, 30),
            "SCORING": (80, 80, 0, 40),
            "WARNING": (100, 80, 0, 40),
            "ERROR": (100, 0, 0, 50),
        }

    def addEntry(self, message: str, level: str = "INFO") -> None:
        """
        Add a new log entry.
        
        Args:
            message: Log message
            level: Log level
        """
        entry = GameLogEntry(message, level)
        self.entries.append(entry)
        if len(self.entries) > self.maxEntries:
            self.entries.pop(0)
        self.scrollToBottom()

    def toggleVisibility(self) -> None:
        """Toggle the visibility of the game log."""
        self.visible = not self.visible

    def scrollToBottom(self) -> None:
        """Scroll to the bottom of the log."""
        self.scrollOffset = 0

    def handleScroll(self, scrollDelta: int) -> None:
        """
        Handle scrolling through log entries.
        
        Args:
            scrollDelta: Scroll amount
        """
        if not self.visible:
            return
        debugEnabled = settingsManager.get("DEBUG", False)
        filteredCount = 0
        for entry in self.entries:
            if entry.level == "DEBUG" and not debugEnabled:
                continue
            filteredCount += 1
        self.scrollOffset += scrollDelta * 5
        usableHeight = settingsManager.get("WINDOW_HEIGHT", 1080) - 100
        lineHeight = 32
        maxVisibleLines = usableHeight // lineHeight
        maxScroll = max(0, filteredCount - maxVisibleLines)
        self.scrollOffset = max(0, min(self.scrollOffset, maxScroll))

    def getVisibleLines(self) -> int:
        """Get the number of visible lines in the log."""
        screenHeight = settingsManager.get("WINDOW_HEIGHT", 1080)
        usableHeight = screenHeight - 100
        lineHeight = 32
        return usableHeight // lineHeight

    def updateMaxEntries(self) -> None:
        """Update the maximum number of log entries from settings."""
        newMaxEntries = settingsManager.get("GAME_LOG_MAX_ENTRIES", 2000)
        if newMaxEntries != self.maxEntries:
            self.maxEntries = newMaxEntries
            if len(self.entries) > self.maxEntries:
                removeCount = len(self.entries) - self.maxEntries
                self.entries = self.entries[removeCount:]
                self.scrollToBottom()

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the game log overlay.
        
        Args:
            screen: Surface to draw on
        """
        if not self.visible:
            return
        screenWidth = settingsManager.get("WINDOW_WIDTH", 1920)
        screenHeight = settingsManager.get("WINDOW_HEIGHT", 1080)
        overlay = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        titleText = self.titleFont.render("Game Log (Press TAB to close, Mouse Wheel to scroll)", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(screenWidth // 2, 30))
        titleBg = pygame.Surface((titleRect.width + 20, titleRect.height + 10), pygame.SRCALPHA)
        titleBg.fill((50, 50, 50, 180))
        screen.blit(titleBg, (titleRect.x - 10, titleRect.y - 5))
        screen.blit(titleText, titleRect)
        debugEnabled = settingsManager.get("DEBUG", False)
        filteredEntries = []
        for entry in self.entries:
            if entry.level == "DEBUG" and not debugEnabled:
                continue
            filteredEntries.append(entry)
        usableHeight = screenHeight - 100
        lineHeight = 32
        maxVisibleLines = usableHeight // lineHeight
        totalFilteredEntries = len(filteredEntries)
        if totalFilteredEntries == 0:
            return
        startIndex = max(0, totalFilteredEntries - maxVisibleLines - self.scrollOffset)
        endIndex = min(totalFilteredEntries, totalFilteredEntries - self.scrollOffset)
        maxScroll = max(0, totalFilteredEntries - maxVisibleLines)
        self.scrollOffset = max(0, min(self.scrollOffset, maxScroll))
        startIndex = max(0, totalFilteredEntries - maxVisibleLines - self.scrollOffset)
        endIndex = min(totalFilteredEntries, totalFilteredEntries - self.scrollOffset)
        yPos = 70
        entriesDrawn = 0
        for i in range(startIndex, endIndex):
            if i < 0 or i >= len(filteredEntries):
                continue
            entry = filteredEntries[i]
            if yPos + lineHeight > screenHeight - 20:
                break
            timeStr = entry.getFormattedTime()
            levelStr = f"[{entry.level}]"
            fullMessage = f"{timeStr} {levelStr} {entry.message}"
            textColor = self.levelColors.get(entry.level, (255, 255, 255))
            bgColor = self.levelBackgrounds.get(entry.level, (0, 0, 0, 0))
            if bgColor[3] > 0:
                lineBg = pygame.Surface((screenWidth - 20, lineHeight), pygame.SRCALPHA)
                lineBg.fill(bgColor)
                screen.blit(lineBg, (10, yPos - 2))
            maxWidth = screenWidth - 40
            testSurface = self.font.render(fullMessage, True, textColor)
            if testSurface.get_width() > maxWidth:
                words = entry.message.split(' ')
                lines = []
                currentLine = f"{timeStr} {levelStr}"
                for word in words:
                    testLine = f"{currentLine} {word}"
                    if self.font.size(testLine)[0] <= maxWidth:
                        currentLine = testLine
                    else:
                        if currentLine.strip():
                            lines.append(currentLine)
                        currentLine = f"           {word}"
                if currentLine.strip():
                    lines.append(currentLine)
                for line in lines:
                    if yPos + lineHeight > screenHeight - 20:
                        break
                    wrappedSurface = self.font.render(line, True, textColor)
                    screen.blit(wrappedSurface, (20, yPos))
                    yPos += lineHeight
                    entriesDrawn += 1
            else:
                screen.blit(testSurface, (20, yPos))
                yPos += lineHeight
                entriesDrawn += 1
        if totalFilteredEntries > maxVisibleLines:
            visibleStart = max(1, totalFilteredEntries - self.scrollOffset - entriesDrawn + 1)
            visibleEnd = totalFilteredEntries - self.scrollOffset
            scrollInfo = f"Lines {visibleStart}-{visibleEnd} of {totalFilteredEntries}"
            scrollSurface = self.font.render(scrollInfo, True, (180, 180, 180))
            scrollBg = pygame.Surface((scrollSurface.get_width() + 10, scrollSurface.get_height() + 6), pygame.SRCALPHA)
            scrollBg.fill((0, 0, 0, 150))
            scrollRect = (screenWidth - scrollSurface.get_width() - 25, screenHeight - 35)
            screen.blit(scrollBg, (scrollRect[0] - 5, scrollRect[1] - 3))
            screen.blit(scrollSurface, scrollRect)