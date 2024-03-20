import os
import gradio as gr
import requests
import json
from PIL import Image

css = """
.example-image img{
    display: flex; /* Use flexbox to align items */
    justify-content: center; /* Center the image horizontally */
    align-items: center; /* Center the image vertically */
    height: 300px; /* Set the height of the container */
    object-fit: contain; /* Preserve aspect ratio while fitting the image within the container */
}

.example-image{
    display: flex; /* Use flexbox to align items */
    justify-content: center; /* Center the image horizontally */
    align-items: center; /* Center the image vertically */
    height: 350px; /* Set the height of the container */
    object-fit: contain; /* Preserve aspect ratio while fitting the image within the container */
}

.face-row {
    display: flex;
    justify-content: space-around; /* Distribute space evenly between elements */
    align-items: center; /* Align items vertically */
    width: 100%; /* Set the width of the row to 100% */
}

.face-image{
    justify-content: center; /* Center the image horizontally */
    align-items: center; /* Center the image vertically */
    height: 160px; /* Set the height of the container */
    width: 160px;
    object-fit: contain; /* Preserve aspect ratio while fitting the image within the container */
}

.face-image img{
    justify-content: center; /* Center the image horizontally */
    align-items: center; /* Center the image vertically */
    height: 160px; /* Set the height of the container */
    object-fit: contain; /* Preserve aspect ratio while fitting the image within the container */
}

.markdown-success-container {
    background-color: #F6FFED;
    padding: 20px;
    margin: 20px;
    border-radius: 1px;
    border: 2px solid green;
    text-align: center;
}

.markdown-fail-container {
    background-color: #FFF1F0;
    padding: 20px;
    margin: 20px;
    border-radius: 1px;
    border: 2px solid red;
    text-align: center;
}

.markdown-attribute-container {
    display: flex;
    justify-content: space-around; /* Distribute space evenly between elements */
    align-items: center; /* Align items vertically */
    padding: 10px;
    margin: 10px;
}

.block-background {
    # background-color: #202020; /* Set your desired background color */
    border-radius: 5px;
}

"""

def convert_fun(input_str):
    # Remove line breaks and extra whitespaces
    return ' '.join(input_str.split())

def get_attributes(frame):    
    url = "https://recognito.p.rapidapi.com/api/analyze_face"
    try:
        files = {'image': open(frame, 'rb')}
        headers = {"X-RapidAPI-Key": os.environ.get("API_KEY")}

        r = requests.post(url=url, files=files, headers=headers)
    except:
        raise gr.Error("Please select images file!")

    faces = None
    face_crop, one_line_attribute = None, ""
    try:
        image = Image.open(frame)

        face = Image.new('RGBA',(150, 150), (80,80,80,0))
        
        res = r.json().get('image')
        if res is not None and res:
            face = res.get('detection')
            x1 = face.get('x')
            y1 = face.get('y')
            x2 = x1 + face.get('w')
            y2 = y1 + face.get('h')

            if x1 < 0:
                x1 = 0
            if y1 < 0:
                y1 = 0
            if x2 >= image.width:
                x2 = image.width - 1
            if y2 >= image.height:
                y2 = image.height - 1

            face_crop = image.crop((x1, y1, x2, y2))
            face_image_ratio = face_crop.width / float(face_crop.height)
            resized_w = int(face_image_ratio * 150)
            resized_h = 150

            face_crop = face_crop.resize((int(resized_w), int(resized_h)))
            
            attr = res.get('attribute')
            
            age = attr.get('age')
            gender = attr.get('gender')
            emotion = attr.get('emotion')
            ethnicity = attr.get('ethnicity')

            mask = attr.get('face_mask')
            glass = 'No Glasses'
            if attr.get('glasses') == 'USUAL':
                glass = 'Glasses'
            if attr.get('glasses') == 'DARK':
                glass = 'Sunglasses'
            
            open_eye_thr = 0.3
            left_eye = 'Close'
            if attr.get('eye_left') >= open_eye_thr:
                left_eye = 'Open'

            right_eye = 'Close'
            if attr.get('eye_right') >= open_eye_thr:
                right_eye = 'Open'

            facehair = attr.get('facial_hair')
            haircolor = attr.get('hair_color')
            hairtype = attr.get('hair_type')
            headwear = attr.get('headwear')

            pitch = attr.get('pitch')
            roll = attr.get('roll')
            yaw = attr.get('yaw')
            quality = attr.get('quality')

            attribute = f"""
            <br/>
            <div class="markdown-attribute-container">
            <table>
            <tr>
                <th style="text-align: center;">Attribute</th>
                <th style="text-align: center;">Result</th>
                <th style="text-align: center;">Score</th>
                <th style="text-align: center;">Threshold</th>
            </tr>
            <tr>
                <td>Gender</td>
                <td>{gender}</td>
                <td></td><td></td>
            </tr>
            <tr>
                <td>Age</td>
                <td>{int(age)}</td>
                <td></td><td></td>
            </tr>
            <tr>
                <td>Pitch</td>
                <td>{"{:.4f}".format(pitch)}</td>
                <td></td><td></td>
            </tr>
            <tr>
                <td>Yaw</td>
                <td>{"{:.4f}".format(yaw)}</td>
                <td></td><td></td>
            </tr>
            <tr>
                <td>Roll</td>
                <td>{"{:.4f}".format(roll)}</td>
                <td></td><td></td>
            </tr>
            <tr>
                <td>Emotion</td>
                <td>{emotion}</td>
                <td></td><td></td>
            </tr>
                <tr>
                <td>Left Eye</td>
                <td>{left_eye}</td>
                <td>{"{:.4f}".format(attr.get('eye_left'))}</td>
                <td>{open_eye_thr}</td>
            </tr>
            <tr>
                <td>Right Eye</td>
                <td>{right_eye}</td>
                <td>{"{:.4f}".format(attr.get('eye_right'))}</td>
                <td>{open_eye_thr}</td>
            </tr>
            <tr>
                <td>Mask</td>
                <td>{mask}</td>
                <td></td><td></td>
            </tr>
            <tr>
                <td>Glass</td>
                <td>{glass}</td>
                <td></td><td></td>
            </tr>
            <tr>
                <td>FaceHair</td>
                <td>{facehair}</td>
                <td></td><td></td>
            </tr>
            <tr>
                <td>HairColor</td>
                <td>{haircolor}</td>
                <td></td><td></td>
            </tr>
            <tr>
                <td>HairType</td>
                <td>{hairtype}</td>
                <td></td><td></td>
            </tr>
            <tr>
                <td>HeadWear</td>
                <td>{headwear}</td>
                <td></td><td></td>
            </tr>
            <tr>
                <td>Image Quality</td>
                <td>{"{:.4f}".format(quality)}</td>
                <td></td><td></td>
            </tr>
            </table>
            </div>
            """
            one_line_attribute = convert_fun(attribute)
    except:
        pass
    
    return face_crop, one_line_attribute

def check_liveness(frame):
    
    url = "https://recognito-faceliveness.p.rapidapi.com/api/check_liveness"
    try:
        files = {'image': open(frame, 'rb')}
        headers = {"X-RapidAPI-Key": os.environ.get("API_KEY")}

        r = requests.post(url=url, files=files, headers=headers)
    except:
        raise gr.Error("Please select images file!")

    faces = None

    face_crop, liveness_result, liveness_score = None, "", -200
    try:
        image = Image.open(frame)

        face = Image.new('RGBA',(150, 150), (80,80,80,0))
        res = r.json().get('data')
        if res is not None and res:
            face = res.get('face_rect')
            x1 = face.get('x')
            y1 = face.get('y')
            x2 = x1 + face.get('w')
            y2 = y1 + face.get('h')

            if x1 < 0:
                x1 = 0
            if y1 < 0:
                y1 = 0
            if x2 >= image.width:
                x2 = image.width - 1
            if y2 >= image.height:
                y2 = image.height - 1

            face_crop = image.crop((x1, y1, x2, y2))
            face_image_ratio = face_crop.width / float(face_crop.height)
            resized_w = int(face_image_ratio * 150)
            resized_h = 150

            face_crop = face_crop.resize((int(resized_w), int(resized_h)))
            liveness_score = res.get('liveness_score')
            liveness = res.get('result')

            if liveness == 'REAL':
                liveness_result = f"""<br/><div class="markdown-success-container"><p style="text-align: center; font-size: 20px; color: green;">Liveness Check:  REAL<br/>Score: {liveness_score}</p></div>"""
            else:
                liveness_result = f"""<br/><div class="markdown-fail-container"><p style="text-align: center; font-size: 20px; color: red;">Liveness Check:  {liveness}<br/>Score: {liveness_score}</p></div>"""

    except:
        pass
    
    return face_crop, liveness_result, liveness_score

def analyze_face(frame):
    face_crop_1, liveness_result, liveness_score = check_liveness(frame)
    face_crop_2, attribute = get_attributes(frame)

    face_crop = face_crop_1 if (face_crop_1 is not None) else face_crop_2
    return [face_crop, liveness_result, attribute]


def compare_face(frame1, frame2):
    url = "https://recognito.p.rapidapi.com/api/compare_face"
    try:
        files = {'image1': open(frame1, 'rb'), 'image2': open(frame2, 'rb')}
        headers = {"X-RapidAPI-Key": os.environ.get("API_KEY")}

        r = requests.post(url=url, files=files, headers=headers)
    except:
        raise gr.Error("Please select images files!")

    faces = None

    try:
        image1 = Image.open(frame1)
        image2 = Image.open(frame2)

        face1 = Image.new('RGBA',(150, 150), (80,80,80,0))
        face2 = Image.new('RGBA',(150, 150), (80,80,80,0))

        res1 = r.json().get('image1')
        
        if res1 is not None and res1:
            face = res1.get('detection')
            x1 = face.get('x')
            y1 = face.get('y')
            x2 = x1 + face.get('w')
            y2 = y1 + face.get('h')
            if x1 < 0:
                x1 = 0
            if y1 < 0:
                y1 = 0
            if x2 >= image1.width:
                x2 = image1.width - 1
            if y2 >= image1.height:
                y2 = image1.height - 1

            face1 = image1.crop((x1, y1, x2, y2))
            face_image_ratio = face1.width / float(face1.height)
            resized_w = int(face_image_ratio * 150)
            resized_h = 150

            face1 = face1.resize((int(resized_w), int(resized_h)))

        res2 = r.json().get('image2')
        if res2 is not None and res2:
            face = res2.get('detection')
            x1 = face.get('x')
            y1 = face.get('y')
            x2 = x1 + face.get('w')
            y2 = y1 + face.get('h')

            if x1 < 0:
                x1 = 0
            if y1 < 0:
                y1 = 0
            if x2 >= image2.width:
                x2 = image2.width - 1
            if y2 >= image2.height:
                y2 = image2.height - 1

            face2 = image2.crop((x1, y1, x2, y2))
            face_image_ratio = face2.width / float(face2.height)
            resized_w = int(face_image_ratio * 150)
            resized_h = 150

            face2 = face2.resize((int(resized_w), int(resized_h)))
    except:
        pass
        
    matching_result = Image.open("icons/blank.png")
    similarity_score = ""
    if face1 is not None and face2 is not None:
        matching_score = r.json().get('matching_score')
        if matching_score is not None:
            str_score = str("{:.4f}".format(matching_score))
            if matching_score >= 0.7:
                matching_result = Image.open("icons/same.png")
                similarity_score = f"""<br/><div class="markdown-success-container"><p style="text-align: center; font-size: 20px; color: green;">Similarity score: {str_score}</p></div>"""
            else:
                matching_result = Image.open("icons/different.png")
                similarity_score = f"""<br/><div class="markdown-fail-container"><p style="text-align: center; font-size: 20px; color: red;">Similarity score: {str_score}</p></div>"""
    
    return [face1, face2, matching_result, similarity_score]


def image_change_callback(image_data):
    # This function will be called whenever a new image is set for the gr.Image component
    print("New image set:", image_data)

with gr.Blocks(css=css) as demo:
    gr.Markdown(
        """
        <a href="https://recognito.vision" style="display: flex; align-items: center;">
            <img src="https://recognito.vision/wp-content/uploads/2024/03/Recognito-modified.png" style="width: 8%; margin-right: 15px;"/>
            <div>
                <p style="font-size: 32px; font-weight: bold; margin: 0;">Recognito</p>
                <p style="font-size: 18px; margin: 0;">www.recognito.vision</p>
            </div>
        </a>

        <p style="font-size: 20px; font-weight: bold;">✨ NIST FRVT Top #1 Face Recognition Algorithm Developer</p>
        <div style="display: flex; align-items: center;">
            &emsp;&emsp;<a href="https://pages.nist.gov/frvt/html/frvt11.html"> <p style="font-size: 14px;">👉🏻 Latest NIST FRVT Report</p></a>
        </div>
        <p style="font-size: 20px; font-weight: bold;">🤝 Contact us for our on-premise Face Recognition, Liveness Detection SDKs deployment</p>
        </div><div style="display: flex; align-items: center;">
            &emsp;&emsp;<a target="_blank" href="mailto:hello@recognito.vision"><img src="https://img.shields.io/badge/email-hello@recognito.vision-blue.svg?logo=gmail " alt="www.recognito.vision"></a>
            &nbsp;&nbsp;&nbsp;&nbsp;<a target="_blank" href="https://wa.me/+14158003112"><img src="https://img.shields.io/badge/whatsapp-recognito-blue.svg?logo=whatsapp " alt="www.recognito.vision"></a>
            &nbsp;&nbsp;&nbsp;&nbsp;<a target="_blank" href="https://t.me/recognito_vision"><img src="https://img.shields.io/badge/telegram-@recognito-blue.svg?logo=telegram " alt="www.recognito.vision"></a>
            &nbsp;&nbsp;&nbsp;&nbsp;<a target="_blank" href="https://join.slack.com/t/recognito-workspace/shared_invite/zt-2d4kscqgn-"><img src="https://img.shields.io/badge/slack-recognito-blue.svg?logo=slack " alt="www.recognito.vision"></a>
        </div>
        <br/>
        <div style="display: flex; align-items: center;">
            &emsp;&emsp;<a href="https://recognito.vision" style="display: flex; align-items: center;"><img src="https://recognito.vision/wp-content/uploads/2024/03/recognito_64.png" style="width: 24px; margin-right: 5px;"/></a>
            &nbsp;&nbsp;&nbsp;&nbsp;<a href="https://www.linkedin.com/company/recognito-vision" style="display: flex; align-items: center;"><img src="https://recognito.vision/wp-content/uploads/2024/03/linkedin64.png" style="width: 24px; margin-right: 5px;"/></a>
            &nbsp;&nbsp;&nbsp;&nbsp;<a href="https://huggingface.co/Recognito" style="display: flex; align-items: center;"><img src="https://recognito.vision/wp-content/uploads/2024/03/hf1_64.png" style="width: 24px; margin-right: 5px;"/></a>
            &nbsp;&nbsp;&nbsp;&nbsp;<a href="https://github.com/Recognito-Vision" style="display: flex; align-items: center;"><img src="https://recognito.vision/wp-content/uploads/2024/03/github64.png" style="width: 24px; margin-right: 5px;"/></a>
            &nbsp;&nbsp;&nbsp;&nbsp;<a href="https://hub.docker.com/u/recognito" style="display: flex; align-items: center;"><img src="https://recognito.vision/wp-content/uploads/2024/03/docker64.png" style="width: 24px; margin-right: 5px;"/></a>
        </div>
        <br/><br/><br/>
        """
    )
    
    with gr.Tabs():
        with gr.Tab("Face Recognition"):
            with gr.Row():
                with gr.Column(scale=2):
                    with gr.Row():
                        with gr.Column(scale=1):
                            compare_face_input1 = gr.Image(label="Image1", type='filepath', elem_classes="example-image")
                            gr.Examples(['examples/1.jpg', 'examples/2.jpg', 'examples/3.jpg', 'examples/4.jpg'], 
                                        inputs=compare_face_input1)
                        with gr.Column(scale=1):
                            compare_face_input2 = gr.Image(label="Image2", type='filepath', elem_classes="example-image")
                            gr.Examples(['examples/5.jpg', 'examples/6.jpg', 'examples/7.jpg', 'examples/8.jpg'], 
                                        inputs=compare_face_input2)
                            
                with gr.Blocks():
                    with gr.Column(scale=1, min_width=400, elem_classes="block-background"):     
                        compare_face_button = gr.Button("Compare Face", variant="primary", size="lg")
                        with gr.Row(elem_classes="face-row"):
                            face_output1 = gr.Image(value="icons/face.jpg", label="Face 1", scale=0, elem_classes="face-image")
                            compare_result = gr.Image(value="icons/blank.png", min_width=30, scale=0, show_download_button=False, show_label=False)
                            face_output2 = gr.Image(value="icons/face.jpg", label="Face 2", scale=0, elem_classes="face-image")
                        similarity_markdown = gr.Markdown("")

                        compare_face_button.click(compare_face, inputs=[compare_face_input1, compare_face_input2], outputs=[face_output1, face_output2, compare_result, similarity_markdown])
                
        with gr.Tab("Face Liveness, Analysis"):
            with gr.Row():
                with gr.Column(scale=1):
                    face_input = gr.Image(label="Image", type='filepath', elem_classes="example-image")
                    gr.Examples(['examples/att_1.jpg', 'examples/att_2.jpg', 'examples/att_3.jpg', 'examples/att_4.jpg', 'examples/att_5.jpg', 'examples/att_6.jpg', 'examples/att_7.jpg', 'examples/att_8.jpg', 'examples/att_9.jpg', 'examples/att_10.jpg'], 
                                inputs=face_input)

                with gr.Blocks():
                    with gr.Column(scale=1, elem_classes="block-background"):     
                        analyze_face_button = gr.Button("Analyze Face", variant="primary", size="lg")
                        with gr.Row(elem_classes="face-row"):
                            face_output = gr.Image(value="icons/face.jpg", label="Face", scale=0, elem_classes="face-image")
                        
                        liveness_result = gr.Markdown("")
                        attribute_result = gr.Markdown("")
                    
                    analyze_face_button.click(analyze_face, inputs=face_input, outputs=[face_output, liveness_result, attribute_result])

    gr.HTML('<a href="https://visitorbadge.io/status?path=https%3A%2F%2Fhuggingface.co%2Fspaces%2FRecognito%2FFaceRecognition-LivenessDetection-FaceAnalysis"><img src="https://api.visitorbadge.io/api/combined?path=https%3A%2F%2Fhuggingface.co%2Fspaces%2FRecognito%2FFaceRecognition-LivenessDetection-FaceAnalysis&countColor=%2337d67a&style=flat&labelStyle=upper" /></a>')
    
demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False)