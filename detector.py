from fastapi import FastAPI, UploadFile, File, HTTPException
import cv2
import numpy as np
import pytesseract
import subprocess
import os
from time import time
import matplotlib.pyplot as plt

app = FastAPI()

def process_image(image_path):
    template_path = "C:\\Users\\oziel\\Downloads\\ApiRed\\app\\imagenes\\ine.jpg"

    # Cargar la imagen y el template
    image = cv2.imread(image_path)
    template = cv2.imread(template_path)

    # Convertir las imágenes a escala de grises
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Utilizar ORB para detectar puntos clave y extraer características locales invariantes (binarias)
    orb = cv2.ORB_create()
    kpsA, descsA = orb.detectAndCompute(image_gray, None)
    kpsB, descsB = orb.detectAndCompute(template_gray, None)

    # Realizar el emparejamiento de características
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descsA, descsB)
    matches = sorted(matches, key=lambda x: x.distance)

    # Seleccionar las mejores coincidencias
    num_keep = int(len(matches) * 0.2)
    matches = matches[:num_keep]

    # Obtener las coordenadas de los puntos clave emparejados
    ptsA = np.float32([kpsA[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    ptsB = np.float32([kpsB[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    # Calcular la matriz de homografía
    M, _ = cv2.findHomography(ptsA, ptsB, cv2.RANSAC)

    # Aplicar la transformación de perspectiva a la imagen de entrada
    aligned_image = cv2.warpPerspective(image, M, (template.shape[1], template.shape[0]))

    # Procesar la imagen alineada
    aligned_gray = cv2.cvtColor(aligned_image, cv2.COLOR_BGR2GRAY)
    aligned_gray = cv2.GaussianBlur(aligned_gray, (3, 3), 0, 0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(12, 12))
    aligned_gray = clahe.apply(aligned_gray)
    _, aligned_gray = cv2.threshold(aligned_gray, thresh=165, maxval=255, type=cv2.THRESH_TRUNC + cv2.THRESH_OTSU)
    aligned_gray = cv2.copyMakeBorder(aligned_gray, top=20, bottom=20, left=20, right=20, borderType=cv2.BORDER_CONSTANT, value=(255, 255, 255))

    # Detección de texto utilizando pytesseract
    text = pytesseract.image_to_string(aligned_gray, lang='eng')

    return aligned_gray, text

def call_curl(image_path):
    subprocess.call(['curl', '-X', 'POST', '-F', f'file=@{image_path}', 'http://127.0.0.1:8000/align_images'])

@app.post("/align_images")
async def align_images(file: UploadFile = File(...)):
    # Guardar la imagen cargada en el servidor
    image_path = f"uploaded_images/{file.filename}"
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())

    # Verificar si el archivo existe antes de procesarlo
    if os.path.exists(image_path):
        # Procesar la imagen
        aligned_image, detected_text = process_image(image_path)

        # Devolver la imagen alineada y el texto detectado
        return {"aligned_image": aligned_image.tolist(), "detected_text": detected_text}
    else:
        raise HTTPException(status_code=400, detail="El archivo no existe.")

@app.post("/call_curl")
async def perform_curl(file: UploadFile = File(...)):
    image_path = f"uploaded_images/{file.filename}"
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())
    call_curl(image_path)