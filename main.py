import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl

####Functions####

#Connection to the google sheets#
conn = st.connection("gsheets", type=GSheetsConnection)
ttl_seconds = 5

def restart():
    st.session_state.page = 0
placeholder = st.empty()

def clear_my_cache():
    st.cache_data.clear()
if "page" not in st.session_state:
    st.session_state.page = 0


def send_email(sending_to,problem,num,specific_location,name):
    def load_image(image_file):
        img = Image.open(image_file)
        return img

    pswd = st.secrets["key"]
    smtp_port = 587  # Standard secure SMTP port
    smtp_server = "smtp.gmail.com"
    email_from = "yossithecat@gmail.com"
    email_to = "yvolind@gmail.com"
    subject = f"דווח ליקוי חדש מספר {num} "

    body = f"""
    שם השולח:
    {name}  
    מיקום הליקוי הוא:
    {specific_location}
    פירוט:
    {problem}  
    """
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = sending_to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if image_file is not None:
        file_details = {"FileName":image_file.name,"FileType":image_file.type}
        # st.write(file_details)
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

    else:

        text = msg.as_string()
        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_from, pswd)
            server.sendmail(email_from, email_to, text)
            server.quit()


##############End Of Functions#############
sql = ''' select * from Sheet1
where "ID"<= (
                                select round(max("ID"),0) as 'id'
                                from
                                Sheet1)

                                '''
# df=conn.read(worksheet='Sheet1',ttl=ttl_seconds)
df = conn.query(sql=sql, ttl=ttl_seconds)

sql = '''
                                select round(max("ID"),0) as 'id'
                                from
                                Sheet1

                                '''
temp_df = conn.query(sql=sql, ttl=ttl_seconds)
num = int(temp_df['id'].iloc[0])
num+=1

with placeholder.container():

    if st.session_state.page==0:

        st.title("טופס תקלות מתחם נורת")
        #list of locations for a problem
        locations_list=["בניין 38","בניין 40","בניין 42","חניונים ושטחים משותפים"]
        emails=['38adamlove@gmail.com','adam40kfaryona@gmail.com','adam42kfaryona@gmail.com']

        with st.form(key='problems_form'):
            name=st.text_input(label="שם מלא")
            location=st.selectbox("*מיקום התקלה",options=locations_list,index=None)
            specific_location=st.text_input(label="מיקום מפורט של התקלה")
            problem=st.text_area(label="*אנא פרטו ככל הניתן לגבי התקלה או הליקוי")
            image_file = st.file_uploader("תמונה של הליקוי", type=['png', 'jpeg', 'jpg'])
            st.markdown("**נדרש*")
            submit=st.form_submit_button(label="שלח!")

        if submit:
            if not location or not problem:
                st.warning("מיקום ופירוט התקלה הינם שדות חובה")
                # st.stop
            else:
                df_to_concat = pd.DataFrame(
                    [
                        {
                        "ID":num,
                        "Location":location,
                        "Problem":problem,
                        }
                    ]

                )
                updated_df = pd.concat([df,df_to_concat])
                conn.update(worksheet='Sheet1',data=updated_df)
                for i in range(0,len(locations_list)):
                    if i<3 and locations_list[i]==location:
                        sending_to=emails[i]
                        send_email(sending_to,problem,num,specific_location,name)
                    elif i==3 and locations_list[i]==location:
                        for sending_to in emails:
                            send_email(sending_to,problem,num,specific_location,name)
                clear_my_cache()
                st.session_state.page += 1

if st.session_state.page == 1:
    # st.empty()
    placeholder.empty()

# Replace the chart with several elements:
    with placeholder.container():
        st.success("נשלח לוועדים. תודה רבה!")
        st.button("דווחו על ליקוי נוסף", on_click=restart)
        st.markdown("התקלות האחרונות שדווחו")
        # Connecting to google sheets

        sql = '''
                select "ID","Location","Problem"
                from
                Sheet1
                where
                "Building" is not null
                '''
        # existing_data = conn.query(sql=sql, ttl=ttl_seconds)
        existing_data=df[['ID','Location','Problem']]
        existing_data=existing_data.dropna()
        existing_data=existing_data.tail()
        # existing_data=existing_data[['ID','Building','Problem']]
        st.dataframe(existing_data, hide_index=True)  # , height=700,width=500,hide_index=True)










