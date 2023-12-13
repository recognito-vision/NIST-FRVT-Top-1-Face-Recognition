import os
import gradio as gr
import requests
import json
from PIL import Image

def get_attributes(json):    
    liveness = "GENUINE" if json.get('liveness') >= 0.5 else "FAKE"
    attr = json.get('attribute')
    age = attr.get('age')
    gender = attr.get('gender')
    emotion = attr.get('emotion')
    ethnicity = attr.get('ethnicity')

    mask = [attr.get('face_mask')]
    if attr.get('glasses') == 'USUAL':
        mask.append('GLASSES')
    if attr.get('glasses') == 'DARK':
        mask.append('SUNGLASSES')
    
    eye = []
    if attr.get('eye_left') >= 0.3:
        eye.append('LEFT')
    if attr.get('eye_right') >= 0.3:
        eye.append('RIGHT')
    facehair = attr.get('facial_hair')
    haircolor = attr.get('hair_color')
    hairtype = attr.get('hair_type')
    headwear = attr.get('headwear')

    activity = []
    if attr.get('food_consumption') >= 0.5:
        activity.append('EATING')
    if attr.get('phone_recording') >= 0.5:
        activity.append('PHONE_RECORDING')
    if attr.get('phone_use') >= 0.5:
        activity.append('PHONE_USE')
    if attr.get('seatbelt') >= 0.5:
        activity.append('SEATBELT')
    if attr.get('smoking') >= 0.5:
        activity.append('SMOKING')

    pitch = attr.get('pitch')
    roll = attr.get('roll')
    yaw = attr.get('yaw')
    quality = attr.get('quality')
    return liveness, age, gender, emotion, ethnicity, mask, eye, facehair, haircolor, hairtype, headwear, activity, pitch, roll, yaw, quality

def compare_face(frame1, frame2):
    url = "https://recognito.p.rapidapi.com/api/face"
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

        liveness1, age1, gender1, emotion1, ethnicity1, mask1, eye1, facehair1, haircolor1, hairtype1, headwear1, activity1, pitch1, roll1, yaw1, quality1 = [None] * 16
        liveness2, age2, gender2, emotion2, ethnicity2, mask2, eye2, facehair2, haircolor2, hairtype2, headwear2, activity2, pitch2, roll2, yaw2, quality2 = [None] * 16
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
            liveness1, age1, gender1, emotion1, ethnicity1, mask1, eye1, facehair1, haircolor1, hairtype1, headwear1, activity1, pitch1, roll1, yaw1, quality1 = get_attributes(res1)

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
            liveness2, age2, gender2, emotion2, ethnicity2, mask2, eye2, facehair2, haircolor2, hairtype2, headwear2, activity2, pitch2, roll2, yaw2, quality2 = get_attributes(res2)
    except:
        pass
    
    matching_result = ""
    if face1 is not None and face2 is not None:
        matching_score = r.json().get('matching_score')
        if matching_score is not None:
            matching_result = """<br/><br/><br/><h1 style="text-align: center;color: #05ee3c;">SAME<br/>PERSON</h1>""" if matching_score >= 0.7 else """<br/><br/><br/><h1 style="text-align: center;color: red;">DIFFERENT<br/>PERSON</h1>"""

    return [r.json(), [face1, face2], matching_result, 
    liveness1, age1, gender1, emotion1, ethnicity1, mask1, eye1, facehair1, haircolor1, hairtype1, headwear1, activity1, pitch1, roll1, yaw1, quality1, 
    liveness2, age2, gender2, emotion2, ethnicity2, mask2, eye2, facehair2, haircolor2, hairtype2, headwear2, activity2, pitch2, roll2, yaw2, quality2]

with gr.Blocks() as demo:
    gr.Markdown(
        """
    # **Recognito Face Analysis**
    ## NIST FRVT Top #1 Face Recognition Algorithm Developer<br/>
    ## Contact us at https://recognito.vision
    <img src="https://recognito.vision/wp-content/uploads/2023/12/black-1.png" alt="NIST FRVT 1:1 Leaderboard" width="50%">
    """
    )
    with gr.Row():
        with gr.Column(scale=1):
            compare_face_input1 = gr.Image(label="Image1", type='filepath', height=270)
            gr.Examples(['examples/1.jpg', 'examples/2.jpg', 'examples/3.jpg', 'examples/4.jpg'], 
                        inputs=compare_face_input1)
            compare_face_input2 = gr.Image(label="Image2", type='filepath', height=270)
            gr.Examples(['examples/5.jpg', 'examples/6.jpg', 'examples/7.jpg', 'examples/8.jpg'], 
                        inputs=compare_face_input2)
            compare_face_button = gr.Button("Face Analysis & Verification", variant="primary", size="lg")

        with gr.Column(scale=2):            
            with gr.Row():
                compare_face_output = gr.Gallery(label="Faces", height=230, columns=[2], rows=[1])
                with gr.Column(variant="panel"):
                    compare_result = gr.Markdown("")

            with gr.Row():
                with gr.Column(variant="panel"):
                    gr.Markdown("<b>Image 1<b/>")
                    liveness1 = gr.CheckboxGroup(["GENUINE", "FAKE"], label="Liveness")
                    age1 = gr.Number(0, label="Age")
                    gender1 = gr.CheckboxGroup(["MALE", "FEMALE"], label="Gender")
                    emotion1 = gr.CheckboxGroup(["HAPPINESS", "ANGER", "FEAR", "NEUTRAL", "SADNESS", "SURPRISE"], label="Emotion")
                    ethnicity1 = gr.CheckboxGroup(["ASIAN", "BLACK", "CAUCASIAN", "EAST_INDIAN"], label="Ethnicity")
                    mask1 = gr.CheckboxGroup(["LOWER_FACE_MASK", "FULL_FACE_MASK", "OTHER_MASK", "GLASSES", "SUNGLASSES"], label="Mask & Glasses")
                    eye1 = gr.CheckboxGroup(["LEFT", "RIGHT"], label="Eye Open")
                    facehair1 = gr.CheckboxGroup(["BEARD", "BRISTLE", "MUSTACHE", "SHAVED"], label="Facial Hair")
                    haircolor1 = gr.CheckboxGroup(["BLACK", "BLOND", "BROWN"], label="Hair Color")
                    hairtype1 = gr.CheckboxGroup(["BALD", "SHORT", "MEDIUM", "LONG"], label="Hair Type")
                    headwear1 = gr.CheckboxGroup(["B_CAP", "CAP", "HAT", "HELMET", "HOOD"], label="Head Wear")
                    activity1 = gr.CheckboxGroup(["EATING", "PHONE_RECORDING", "PHONE_USE", "SMOKING", "SEATBELT"], label="Activity")
                    with gr.Row():
                        pitch1 = gr.Number(0, label="Pitch")
                        roll1 = gr.Number(0, label="Roll")
                        yaw1 = gr.Number(0, label="Yaw")
                        quality1 = gr.Number(0, label="Quality")
                with gr.Column(variant="panel"):                    
                    gr.Markdown("<b>Image 2<b/>")
                    liveness2 = gr.CheckboxGroup(["GENUINE", "FAKE"], label="Liveness")
                    age2 = gr.Number(0, label="Age")
                    gender2 = gr.CheckboxGroup(["MALE", "FEMALE"], label="Gender")
                    emotion2 = gr.CheckboxGroup(["HAPPINESS", "ANGER", "FEAR", "NEUTRAL", "SADNESS", "SURPRISE"], label="Emotion")
                    ethnicity2 = gr.CheckboxGroup(["ASIAN", "BLACK", "CAUCASIAN", "EAST_INDIAN"], label="Ethnicity")
                    mask2 = gr.CheckboxGroup(["LOWER_FACE_MASK", "FULL_FACE_MASK", "OTHER_MASK", "GLASSES", "SUNGLASSES"], label="Mask & Glasses")
                    eye2 = gr.CheckboxGroup(["LEFT", "RIGHT"], label="Eye Open")
                    facehair2 = gr.CheckboxGroup(["BEARD", "BRISTLE", "MUSTACHE", "SHAVED"], label="Facial Hair")
                    haircolor2 = gr.CheckboxGroup(["BLACK", "BLOND", "BROWN"], label="Hair Color")
                    hairtype2 = gr.CheckboxGroup(["BALD", "SHORT", "MEDIUM", "LONG"], label="Hair Type")
                    headwear2 = gr.CheckboxGroup(["B_CAP", "CAP", "HAT", "HELMET", "HOOD"], label="Head Wear")
                    activity2 = gr.CheckboxGroup(["EATING", "PHONE_RECORDING", "PHONE_USE", "SMOKING", "SEATBELT"], label="Activity")
                    with gr.Row():
                        pitch2 = gr.Number(0, label="Pitch")
                        roll2 = gr.Number(0, label="Roll")
                        yaw2 = gr.Number(0, label="Yaw")
                        quality2 = gr.Number(0, label="Quality")

            compare_result_output = gr.JSON(label='Result', visible=False)

    compare_face_button.click(compare_face, inputs=[compare_face_input1, compare_face_input2], outputs=[compare_result_output, compare_face_output, compare_result, 
    liveness1, age1, gender1, emotion1, ethnicity1, mask1, eye1, facehair1, haircolor1, hairtype1, headwear1, activity1, pitch1, roll1, yaw1, quality1, 
    liveness2, age2, gender2, emotion2, ethnicity2, mask2, eye2, facehair2, haircolor2, hairtype2, headwear2, activity2, pitch2, roll2, yaw2, quality2])

demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False)