import io
import os
import numpy as np
import requests
import cv2
import datetime
import tempfile
import pygame
import face_recognition
from django.shortcuts import render, redirect
from django.core.files import File
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from .models import Candidate
from .models import Detection
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile

# Create your views here.


def candidate_form(request):
    if request.method == 'POST':
        # get the form data from the request
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        photo = request.FILES['photo']

        # Load the input image using face_recognition library
        image = face_recognition.load_image_file(photo)

        # Detect face landmarks in the input image
        face_landmarks_list = face_recognition.face_landmarks(image)
         # Get face encodings
        face_encodings = face_recognition.face_encodings(image)[0]

        # save the candidate information and face landmarks to the database
        candidate = Candidate(name=name, age=age, gender=gender, photo=photo, landmarks=face_encodings)
        candidate.save()

        return redirect('success')

    return render(request, 'candidate_form.html')

def success(request):
    return render(request, 'success.html')

def candidate_list(request):
    candidates = Candidate.objects.all()
    return render(request, 'candidate_list.html', {'candidates': candidates})

def delete_candidate(request):
    candidates = Candidate.objects.all()

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        candidate = Candidate.objects.get(id=candidate_id)
        candidate.delete()
        return HttpResponseRedirect('/candidates/') # redirect to the candidate list page after deleting the candidate

    context = {'candidates': candidates}
    return render(request, 'delete_candidate.html', context)

def video_feed(request):
    cascPath = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    faceCascade = cv2.CascadeClassifier(cascPath)
    known_names = list(Candidate.objects.values_list('name', flat=True))
    query_encodings = list(Candidate.objects.values_list('landmarks', flat=True))
    known_encodings = []
    for face_encoding_str in query_encodings:
        face_encoding = [float(num_str) for num_str in face_encoding_str.strip('[]').split()]
        known_encodings.append(face_encoding)

    cap = cv2.VideoCapture(0)

    def generate():
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            results =[]
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(30, 30)
            )
            try:
                img_enc = face_recognition.face_encodings(frame)[0]
                results = face_recognition.compare_faces(known_encodings, img_enc)
            except IndexError:
                pass           

            # get face bounding box for overlay
            if len(results)!=0:                
                for i in range(len(results)):
                    if results[i]:
                        try:
                            name = known_names[i]
                            (top, right, bottom, left) = face_recognition.face_locations(gray)[0]
                            frame = cv2.rectangle(frame , (left, top), (right, bottom), (0, 255, 0), 2)
                            frame = cv2.putText(frame , name, (left + 2, bottom + 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)
                        except IndexError:
                            print("")
                    else:
                        try:
                            name = "Unknown"
                            (top, right, bottom, left) = face_recognition.face_locations(gray)[0]
                            frame = cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                            frame = cv2.putText(frame, name, (left + 2, bottom + 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)
                            sound_file_path = os.path.join(settings.MEDIA_ROOT, 'Intruder.wav')
                            #Alerting the environment with sound
                            pygame.mixer.init(44100, -16,2,2048)
                            sound = pygame.mixer.Sound(sound_file_path)
                            sound.play()
                            #Realtime notification alert
                            response=requests.post('Your IFTTT webhooks API to generate notifications for realtime alert')
                            if response.status_code ==200:
                                print('Intrusion alert successfully notified')
                            else:
                                print('request failed')
                            
                            # Assuming you have access to the current frame as an image object
                            current_frame = frame # Replace this with your code to get the current frame

                            # Convert the current frame to an image file object
                            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_image:
                                cv2.imwrite(temp_image.name, current_frame)
                                image_file = File(temp_image)

                                # Create a new Detection object and save the frame
                                detection = Detection()
                                detection.frame.save('current_frame.jpg', image_file, save=True)  # Adjust the filename as needed

                                # Optionally, you can also save other fields of the Detection model
                                detection.time = datetime.datetime.now().isoformat()  # Set the time value as needed
                                detection.save()

                        except IndexError:
                            print("")
            else:
                try:
                    name = "Unknown"
                    (top, right, bottom, left) = face_recognition.face_locations(gray)[0]
                    frame = cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    frame = cv2.putText(frame, name, (left + 2, bottom + 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)
                    sound_file_path = os.path.join(settings.MEDIA_ROOT, 'Intruder.wav')
                    pygame.mixer.init(44100, -16,2,2048)
                    sound = pygame.mixer.Sound(sound_file_path)
                    sound.play()
                    response=requests.post('Your IFTTT webhooks API to generate notifications for realtime alert')
                    if response.status_code ==200:
                        print('Intrusion alert successfully notified')
                    else:
                        print('request failed')
                    
                    # Assuming you have access to the current frame as an image object
                    current_frame = frame # Replace this with your code to get the current frame

                    # Convert the current frame to an image file object
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_image:
                        cv2.imwrite(temp_image.name, current_frame)
                        image_file = File(temp_image)

                        # Create a new Detection object and save the frame
                        detection = Detection()
                        detection.frame.save('current_frame.jpg', image_file, save=True)  # Adjust the filename as needed

                        # Optionally, you can also save other fields of the Detection model
                        detection.time = datetime.datetime.now().isoformat()  # Set the time value as needed
                        detection.save()

                except IndexError:
                    print("")

            # Convert frame to JPEG and yield it to be sent to the client
            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

def webcam_feed(request):
    return render(request, 'webcam_feed.html')

def detection_list(request):
    detections = Detection.objects.all()
    if request.method == 'POST':
        # Check if the 'delete' action is triggered
        if 'delete' in request.POST:
            selected_detections = request.POST.getlist('selected_detections')

            # Check if the 'select-all-checkbox' is selected
            if 'select-all-checkbox' in request.POST:
                # Retrieve all detection IDs
                selected_detections = [str(detection.id) for detection in detections]

            # Delete the selected detections
            Detection.objects.filter(id__in=selected_detections).delete()
            return redirect('detection_list')
        elif 'email' in request.POST:
            # Query all detections
            detections = Detection.objects.all()

            # Generate PDF content
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer)

            x = 1 * inch
            y = 10.5 * inch
            image_width = 2 * inch
            image_height = 2 * inch

            for detection in detections:
                # Draw detection details in the PDF
                p.drawString(x, y, f"Time: {detection.time}")

                # Load the image from the URL
                try:
                    response = requests.get(detection.frame.url, stream=True)
                    print(response)
                    if response.status_code == 200:
                        with io.BytesIO(response.content) as img_buffer:
                            img_buffer.seek(0)
                            p.drawImage(img_buffer, x, y - 60, width=image_width, height=image_height)
                    else:
                        p.drawString(x, y - 60, "Image not found.")
                except requests.exceptions.RequestException:
                    p.drawString(x, y - 60, "Failed to load image.")

                # Move to the next page
                p.showPage()

            p.save()

            # Save the PDF file with a name based on the current date and time
            folder_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"{folder_name}.pdf"
            file_path = f"{folder_name}/{file_name}"

            # Create a FileSystemStorage instance
            storage = FileSystemStorage(location=settings.MEDIA_ROOT)
            saved_file_path = storage.save(file_path, ContentFile(buffer.getvalue()))

            # Check if the file exists
            if storage.exists(saved_file_path):
                return HttpResponse('PDF saved successfully.')
            else:
                return HttpResponse('Failed to save the PDF.')
        return HttpResponse('Invalid request.')
    return render(request, 'detection_list.html', {'detections': detections})