def updateResolution(width, height):
    with open("src/settings.py", "r") as f:
        lines = f.readlines()

    with open("src/settings.py", "w") as f:
        for line in lines:
            if line.startswith("WINDOW_WIDTH"):
                f.write(f"WINDOW_WIDTH = {width}\n")
            elif line.startswith("WINDOW_HEIGHT"):
                f.write(f"WINDOW_HEIGHT = {height}\n")
            else:
                f.write(line)
                
