import streamlit as st
import os
import pandas as pd
from PIL import Image
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl

def load_image(image_file):
    img=Image.open(image_file)
    return img

# key_path="./key.txt"
# with open (key_path,'r') as f:
#     pswd=f.read()
pswd=st.secrets["key"]

smtp_port = 587                 # Standard secure SMTP port
smtp_server = "smtp.gmail.com"

email_from = "yossithecat@gmail.com"
email_to = "yvolind@gmail.com"

subject = "New email from TIE with attachments!!"
body = """
This is the problem
This is where it is

"""
msg = MIMEMultipart()
msg['From'] = email_from
msg['To'] = email_to
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))

image_file = st.file_uploader("Upload An Image",type=['png','jpeg','jpg'])
if image_file is not None:
    file_details = {"FileName":image_file.name,"FileType":image_file.type}
    st.write(file_details)
    img = load_image(image_file)
    st.image(img)

    with open(image_file.name,mode='wb') as f:
        f.write(image_file.getbuffer())


    with open(image_file.name, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {image_file.name}",
        )

        # Add attachment to message and convert message to string
        msg.attach(part)
        text = msg.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_from, pswd)
            server.sendmail(email_from, email_to, text)
            server.quit()

        st.success("Saved File")











