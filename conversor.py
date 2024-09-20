from PIL import Image

def image_to_pattern(image_path, threshold=128):
    img = Image.open(image_path).convert('L')  # Converte a imagem para escala de cinza
    width, height = img.size
    pixels = img.load()

    pattern = []
    for y in range(height):
        row = ""
        for x in range(width):
            if pixels[x, y] < threshold:
                row += "1"
            else:
                row += "0"
        pattern.append(row)
    
    return pattern

# Caminho da imagem
image_path = 'IMG_0DAB6DEA9A20-1.png'

# Converte a imagem para padrão de matriz
pattern = image_to_pattern(image_path)

# Imprime o padrão de matriz
for row in pattern:
    print(row)
