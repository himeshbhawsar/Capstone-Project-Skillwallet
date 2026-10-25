import os
import math
from PIL import Image, ImageDraw, ImageFont

def create_sample_images():
    os.makedirs("samples", exist_ok=True)
    
    # 1. Sample PPE Site Image (Concrete structure, workers with vests/helmets, scaffolding)
    img_ppe = Image.new("RGB", (900, 600), color=(180, 190, 205))
    draw = ImageDraw.Draw(img_ppe)
    
    # Sky / background
    for y in range(250):
        c = int(140 + y * 0.3)
        draw.line([(0, y), (900, y)], fill=(c, c + 20, 240))
        
    # Crane in distance
    draw.line([(700, 50), (700, 350)], fill=(220, 140, 20), width=6)
    draw.line([(550, 80), (880, 80)], fill=(220, 140, 20), width=5)
    draw.line([(700, 50), (600, 80)], fill=(80, 80, 80), width=2)
    draw.line([(700, 50), (850, 80)], fill=(80, 80, 80), width=2)
    draw.line([(800, 80), (800, 160)], fill=(40, 40, 40), width=2) # Hook line
    draw.rectangle([(795, 160), (805, 175)], fill=(30, 30, 30))
    
    # Concrete building frame
    draw.rectangle([(80, 180), (520, 580)], fill=(120, 125, 130), outline=(70, 75, 80), width=4)
    # Floor slabs
    draw.rectangle([(60, 280), (540, 305)], fill=(90, 95, 100))
    draw.rectangle([(60, 420), (540, 445)], fill=(90, 95, 100))
    
    # Columns
    for x in [120, 260, 400, 480]:
        draw.rectangle([(x, 180), (x+30, 580)], fill=(110, 115, 120), outline=(60, 65, 70), width=2)
        
    # Rebar protruding top
    for x in range(125, 500, 20):
        draw.line([(x, 180), (x, 145)], fill=(160, 90, 50), width=3)
        
    # Scaffolding on left
    for y in range(220, 580, 60):
        draw.line([(40, y), (140, y)], fill=(180, 180, 40), width=4)
    for x in [40, 140]:
        draw.line([(x, 220), (x, 580)], fill=(180, 180, 40), width=4)
    draw.line([(40, 220), (140, 280)], fill=(180, 180, 40), width=2)
    draw.line([(140, 220), (40, 280)], fill=(180, 180, 40), width=2)
    draw.line([(40, 280), (140, 340)], fill=(180, 180, 40), width=2)
    
    # Ground slab
    draw.rectangle([(0, 500), (900, 600)], fill=(100, 105, 110))
    
    # Caution tape / Barrier
    for i in range(0, 900, 40):
        draw.polygon([(i, 510), (i+20, 510), (i+30, 525), (i+10, 525)], fill=(255, 220, 0))
        draw.polygon([(i+20, 510), (i+40, 510), (i+50, 525), (i+30, 525)], fill=(20, 20, 20))

    # Worker 1: Fully Compliant (Hardhat Yellow, Neon Green Vest with Reflective stripes, Boots)
    # Head + Helmet
    draw.ellipse([(200, 340), (230, 370)], fill=(220, 170, 130))
    draw.polygon([(195, 345), (235, 345), (230, 330), (200, 330)], fill=(255, 215, 0)) # Yellow Helmet
    # Torso with Hi-Vis Vest
    draw.rectangle([(195, 370), (235, 430)], fill=(50, 205, 50)) # Neon vest
    draw.line([(195, 395), (235, 395)], fill=(240, 240, 240), width=4) # Reflective strip
    draw.line([(205, 370), (205, 430)], fill=(240, 240, 240), width=3)
    draw.line([(225, 370), (225, 430)], fill=(240, 240, 240), width=3)
    # Legs (Blue denim jeans)
    draw.rectangle([(198, 430), (212, 490)], fill=(40, 60, 120))
    draw.rectangle([(218, 430), (232, 490)], fill=(40, 60, 120))
    # Steel toe boots (Dark brown/black)
    draw.rectangle([(194, 485), (214, 500)], fill=(45, 30, 15))
    draw.rectangle([(216, 485), (236, 500)], fill=(45, 30, 15))
    
    # Worker 2: High Risk Non-Compliant (On scaffold platform, NO helmet, NO harness, wearing casual clothes)
    # Scaffold plank
    draw.rectangle([(30, 335), (150, 345)], fill=(160, 120, 80))
    # Head (NO HELMET - Dark hair visible)
    draw.ellipse([(70, 270), (95, 295)], fill=(210, 160, 120))
    draw.arc([(70, 268), (95, 285)], start=180, end=360, fill=(30, 20, 15), width=6) # Dark hair
    # Casual red shirt (No Hi-Vis)
    draw.rectangle([(68, 295), (98, 335)], fill=(200, 50, 40))
    # Legs
    draw.rectangle([(70, 335), (81, 380)], fill=(60, 60, 70))
    draw.rectangle([(85, 335), (96, 380)], fill=(60, 60, 70))
    # Sneakers (non steel-toe)
    draw.rectangle([(67, 375), (82, 385)], fill=(220, 220, 220))
    draw.rectangle([(84, 375), (99, 385)], fill=(220, 220, 220))
    
    # Overlay site badge
    draw.rectangle([(20, 20), (320, 70)], fill=(15, 23, 42, 220))
    draw.text((30, 30), "SITE AUDIT: ZONE 4B SECTOR", fill=(255, 255, 255))
    draw.text((30, 48), "STANDARDS: OSHA 1926 / IS 456", fill=(245, 158, 11))
    
    img_ppe.save("samples/ppe_site_worker.jpg", quality=95)
    
    # 2. Sample Concrete Shear Crack (45-degree diagonal structural crack)
    img_crack = Image.new("RGB", (800, 600), color=(175, 178, 180))
    draw_c = ImageDraw.Draw(img_crack)
    
    # Concrete texture noise
    import random
    random.seed(42)
    for _ in range(8000):
        rx = random.randint(0, 799)
        ry = random.randint(0, 599)
        shade = random.randint(140, 210)
        draw_c.point((rx, ry), fill=(shade, shade, shade))
        
    # Rebar grid ghosting beneath surface
    for x in range(100, 800, 150):
        draw_c.line([(x, 0), (x, 600)], fill=(160, 163, 165), width=3)
    for y in range(100, 600, 150):
        draw_c.line([(0, y), (800, y)], fill=(160, 163, 165), width=3)
        
    # Major structural 45-degree shear crack
    points = [
        (150, 120), (180, 155), (215, 185), (250, 230), (285, 260),
        (330, 305), (370, 340), (410, 390), (450, 425), (495, 470),
        (540, 510), (590, 560)
    ]
    # Draw crack fissure with dark center and fractured edges
    for i in range(len(points)-1):
        p1 = points[i]
        p2 = points[i+1]
        # Dark inner fracture void
        draw_c.line([p1, p2], fill=(20, 20, 25), width=7)
        # Concrete flaking edges
        draw_c.line([(p1[0]-2, p1[1]-1), (p2[0]-2, p2[1]-1)], fill=(90, 92, 95), width=2)
        draw_c.line([(p1[0]+3, p1[1]+2), (p2[0]+3, p2[1]+2)], fill=(215, 218, 220), width=2)
        
        # Branching micro-cracks
        if i in [2, 5, 8]:
            bx = p1[0] + random.randint(20, 45)
            by = p1[1] - random.randint(15, 35)
            draw_c.line([p1, (bx, by)], fill=(45, 45, 50), width=3)
            
    # Scale marker / crack comparison ruler in bottom corner
    draw_c.rectangle([(620, 490), (770, 570)], fill=(250, 250, 250), outline=(30, 30, 30), width=2)
    draw_c.text((630, 498), "CRACK SCALE (mm)", fill=(20, 20, 20))
    for t, mm in enumerate([1.0, 2.5, 5.0, 8.0]):
        y_pos = 520 + t * 11
        draw_c.line([(630, y_pos), (690, y_pos)], fill=(0, 0, 0), width=max(1, int(mm/1.5)))
        draw_c.text((705, y_pos - 5), f"{mm} mm", fill=(20, 20, 20))
        
    img_crack.save("samples/concrete_shear_crack.jpg", quality=95)

    # 3. Sample Hairline Surface Crack
    img_hairline = Image.new("RGB", (800, 600), color=(185, 188, 185))
    draw_h = ImageDraw.Draw(img_hairline)
    for _ in range(7000):
        rx = random.randint(0, 799)
        ry = random.randint(0, 599)
        shade = random.randint(160, 215)
        draw_h.point((rx, ry), fill=(shade, shade, shade))
        
    # Meandering fine shrinkage hairline crack
    h_points = [(120, 280), (190, 275), (260, 290), (330, 285), (410, 300), 
                (480, 295), (550, 310), (620, 305), (690, 315)]
    for i in range(len(h_points)-1):
        draw_h.line([h_points[i], h_points[i+1]], fill=(60, 60, 65), width=2)
        
    draw_h.rectangle([(20, 20), (320, 60)], fill=(15, 23, 42, 220))
    draw_h.text((30, 30), "SPECIMEN: BEAM B-102 (PLASTER COAT)", fill=(255, 255, 255))
    img_hairline.save("samples/concrete_hairline.jpg", quality=95)
    print("Sample images created successfully!")

if __name__ == "__main__":
    create_sample_images()
