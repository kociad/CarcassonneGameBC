import pygame
import time
from typing import List, Tuple
from utils.settingsManager import settings_manager

class GameLogEntry:
    def __init__(self, message: str, level: str = "INFO", timestamp: float = None):
        self.message = message
        self.level = level  # INFO, DEBUG, WARNING, ERROR
        self.timestamp = timestamp or time.time()
        
    def getFormattedTime(self) -> str:
        return time.strftime("%H:%M:%S", time.localtime(self.timestamp))

class GameLog:
    def __init__(self):
        # Get max entries from settings
        self.maxEntries = settings_manager.get("GAME_LOG_MAX_ENTRIES", 2000)
        
        self.entries: List[GameLogEntry] = []
        self.visible = False
        self.scrollOffset = 0
        self.font = pygame.font.Font(None, 28)
        self.titleFont = pygame.font.Font(None, 36)
        
        # Better colors with tinting for different log levels
        self.levelColors = {
            "INFO": (240, 240, 240),      # Light gray
            "DEBUG": (150, 200, 255),     # Light blue
            "WARNING": (255, 220, 100),   # Gold/yellow
            "ERROR": (255, 120, 120),     # Light red
        }
        
        # Background tinting for log levels
        self.levelBackgrounds = {
            "INFO": (0, 0, 0, 0),         # No background
            "DEBUG": (0, 50, 100, 30),    # Dark blue tint
            "WARNING": (100, 80, 0, 40),  # Dark yellow tint
            "ERROR": (100, 0, 0, 50),     # Dark red tint
        }
        
    def addEntry(self, message: str, level: str = "INFO"):
        """Add new log entry"""
        entry = GameLogEntry(message, level)
        self.entries.append(entry)
        
        # Remove old entries if we exceed max
        if len(self.entries) > self.maxEntries:
            self.entries.pop(0)
            
        # Auto-scroll to bottom when new entry is added
        self.scrollToBottom()
    
    def toggleVisibility(self):
        """Toggle log visibility"""
        self.visible = not self.visible
        
    def scrollToBottom(self):
        """Scroll to show latest entries"""
        self.scrollOffset = 0
        
    def handleScroll(self, scrollDelta: int):
        """Handle scrolling through log entries"""
        if not self.visible:
            return
            
        # Filter entries based on debug setting to get accurate count
        debugEnabled = settings_manager.get("DEBUG", False)
        filteredCount = 0
        for entry in self.entries:
            if entry.level == "DEBUG" and not debugEnabled:
                continue
            filteredCount += 1
        
        self.scrollOffset += scrollDelta * 5  # 5 lines per scroll
        
        # Calculate max scroll based on filtered entries
        usableHeight = settings_manager.get("WINDOW_HEIGHT", 1080) - 100
        lineHeight = 32
        maxVisibleLines = usableHeight // lineHeight
        maxScroll = max(0, filteredCount - maxVisibleLines)
        
        self.scrollOffset = max(0, min(self.scrollOffset, maxScroll))
    
    def getVisibleLines(self) -> int:
        """Calculate how many lines can fit on screen"""
        screenHeight = settings_manager.get("WINDOW_HEIGHT", 1080)
        usableHeight = screenHeight - 100  # Leave space for title and margins
        lineHeight = 32  # Increased line height for better readability
        return usableHeight // lineHeight
        
    def updateMaxEntries(self):
        """Update max entries from settings and trim if necessary"""
        newMaxEntries = settings_manager.get("GAME_LOG_MAX_ENTRIES", 2000)
        
        if newMaxEntries != self.maxEntries:
            self.maxEntries = newMaxEntries
            
            # Trim existing entries if new limit is lower
            if len(self.entries) > self.maxEntries:
                removeCount = len(self.entries) - self.maxEntries
                self.entries = self.entries[removeCount:]
                self.scrollToBottom()
    
    def draw(self, screen):
        """Draw the game log overlay"""
        if not self.visible:
            return
            
        screenWidth = settings_manager.get("WINDOW_WIDTH", 1920)
        screenHeight = settings_manager.get("WINDOW_HEIGHT", 1080)
        
        # Semi-transparent dark background for better readability
        overlay = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Dark background with high alpha
        screen.blit(overlay, (0, 0))
        
        # Draw title with better visibility
        titleText = self.titleFont.render("Game Log (Press TAB to close, Mouse Wheel to scroll)", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(screenWidth // 2, 30))
        
        # Title background
        titleBg = pygame.Surface((titleRect.width + 20, titleRect.height + 10), pygame.SRCALPHA)
        titleBg.fill((50, 50, 50, 180))
        screen.blit(titleBg, (titleRect.x - 10, titleRect.y - 5))
        screen.blit(titleText, titleRect)
        
        # Filter entries based on debug setting FIRST
        debugEnabled = settings_manager.get("DEBUG", False)
        filteredEntries = []
        for entry in self.entries:
            if entry.level == "DEBUG" and not debugEnabled:
                continue
            filteredEntries.append(entry)
        
        # Calculate how many lines can fit on screen
        usableHeight = screenHeight - 100  # Leave space for title and margins
        lineHeight = 32
        maxVisibleLines = usableHeight // lineHeight
        
        # Calculate which entries to show based on scroll offset
        totalFilteredEntries = len(filteredEntries)
        if totalFilteredEntries == 0:
            return
            
        # Show entries from bottom up, accounting for scroll
        startIndex = max(0, totalFilteredEntries - maxVisibleLines - self.scrollOffset)
        endIndex = min(totalFilteredEntries, totalFilteredEntries - self.scrollOffset)
        
        # Clamp scroll offset based on filtered entries
        maxScroll = max(0, totalFilteredEntries - maxVisibleLines)
        self.scrollOffset = max(0, min(self.scrollOffset, maxScroll))
        
        # Recalculate indices after clamping
        startIndex = max(0, totalFilteredEntries - maxVisibleLines - self.scrollOffset)
        endIndex = min(totalFilteredEntries, totalFilteredEntries - self.scrollOffset)
        
        yPos = 70  # Start below title
        entriesDrawn = 0
        
        # Display the filtered entries
        for i in range(startIndex, endIndex):
            if i < 0 or i >= len(filteredEntries):
                continue
                
            entry = filteredEntries[i]
            
            if yPos + lineHeight > screenHeight - 20:
                break
                
            # Format the log line
            timeStr = entry.getFormattedTime()
            levelStr = f"[{entry.level}]"
            fullMessage = f"{timeStr} {levelStr} {entry.message}"
            
            # Get colors for this log level
            textColor = self.levelColors.get(entry.level, (255, 255, 255))
            bgColor = self.levelBackgrounds.get(entry.level, (0, 0, 0, 0))
            
            # Draw background tint if needed
            if bgColor[3] > 0:  # If alpha > 0
                lineBg = pygame.Surface((screenWidth - 20, lineHeight), pygame.SRCALPHA)
                lineBg.fill(bgColor)
                screen.blit(lineBg, (10, yPos - 2))
            
            # Handle text wrapping if message is too long
            maxWidth = screenWidth - 40
            testSurface = self.font.render(fullMessage, True, textColor)
            
            if testSurface.get_width() > maxWidth:
                # Text wrapping for long messages
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
                        currentLine = f"           {word}"  # Simple indent
                        
                if currentLine.strip():
                    lines.append(currentLine)
                
                # Draw wrapped lines
                for line in lines:
                    if yPos + lineHeight > screenHeight - 20:
                        break
                    wrappedSurface = self.font.render(line, True, textColor)
                    screen.blit(wrappedSurface, (20, yPos))
                    yPos += lineHeight
                    entriesDrawn += 1
            else:
                # Draw single line
                screen.blit(testSurface, (20, yPos))
                yPos += lineHeight
                entriesDrawn += 1
        
        # Draw scroll indicator
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