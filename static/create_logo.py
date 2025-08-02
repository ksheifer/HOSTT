import cairosvg
import math

def create_logo_png(png_filename="logo.png"):
    size = 300  # Увеличиваем размер полотна (например, 300x300 пикселей)
    center = size / 2
    radius = size / 2

    # Функция для создания пути
    def create_path(angle_start, angle_end, color):
        x1 = center + radius * math.cos(math.radians(angle_start))
        y1 = center + radius * math.sin(math.radians(angle_start))
        x2 = center + radius * math.cos(math.radians(angle_end))
        y2 = center + radius * math.sin(math.radians(angle_end))
        return f'M {center},{center} L {x1},{y1} A {radius},{radius} 0 0,1 {x2},{y2} Z', color

    # Создаем SVG как строку
    svg_data = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}px" height="{size}px">
        <circle cx="{center}" cy="{center}" r="{radius}" fill="white" stroke="none"/>
        <path d="{create_path(-60, 60, '#146E14')[0]}" fill="#146E14"/>
        <path d="{create_path(60, 180, '#4CAF50')[0]}" fill="#4CAF50"/>
        <path d="{create_path(180, 300, '#C3E600')[0]}" fill="#C3E600"/>
    </svg>'''

    # Преобразуем SVG в PNG
    cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), write_to=png_filename, dpi=300)

    print(f"PNG file has been saved as {png_filename}")

create_logo_png()
