import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_sharpmemorydisplay
import speedtest
import csv
import plotter

keys = ["upload", "download", "ping",  "timestamp", "bytes_sent", "bytes_received"]

FONTSIZE = 12

spi = busio.SPI(board.SCK, MOSI=board.MOSI)
scs = digitalio.DigitalInOut(board.D6)  # inverted chip select

# display = adafruit_sharpmemorydisplay.SharpMemoryDisplay(spi, scs, 96, 96)
display = adafruit_sharpmemorydisplay.SharpMemoryDisplay(spi, scs, 400, 240)

# Clear display.
display.fill(1)
display.show()

# Load a TTF font.
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)


# Speedtest stuff
servers = []
threads = None

while True:

    try:
        s = speedtest.Speedtest()
        s.get_servers(servers)
        s.get_best_server()
        s.download(threads=threads)
        s.upload(threads=threads)
        s.results.share()
    except Exception as e:
        print("ERROR")
        print(e)
        print("end")
        continue

    results_dict = s.results.dict()
    print(results_dict)

    with open("log.csv", 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=keys, extrasaction="ignore")
        if (file.tell() == 0):
            writer.writeheader()
        writer.writerow(results_dict)

    try:
        image = plotter.get_img()
    except ValueError: # This might happen when log is still empty and spline can't be generated 
        image = Image.new("1", (display.width, display.height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    
    text = f"    Upload: {results_dict['upload']/1000000:.2f}Mbps  Download:  {results_dict['download']/1000000:.2f}Mbps  Ping: {results_dict['ping']:.2f}ms"
    (font_width, font_height) = font.getsize(text)
    draw.text(
            (5, display.height-30),
        text,
        font=font,
        fill=0,
    )

    # Display image
    image = image.rotate(180)
    display.image(image)
    display.show()
