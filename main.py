import os
import time
import streamlit as st
from openai import OpenAI
os.environ[OPENAI_API_KEY] = st.secrets['openai']["OPENAI_API_KEY"]
client = OpenAI()

# thread_id를 하나로 관리하기 위함
if 'thread_id' not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

# thread_id, assistant_id 설정
thread_id = st.session_state.thread_id
# thread_id = "thread_7jCDbpM0K7e0QukPMRtdL1gM"
assistant_id="asst_2guEKPcOypRCB4rCAGKWvvuw"

# 기존 메시지 모두 불러오기
thread_messages = client.beta.threads.messages.list(thread_id, order="asc")

# 페이지 제목
st.header("AI 변호사 상담")

# 메시지 역순으로 가져와서 UI에 뿌리기
for msg in thread_messages.data:
    with st.chat_message(msg.role):
        st.write(msg.content[0].text.value)

# 메시지 없으면 첫인사 남기기
if thread_messages.data == []:
    with st.chat_message('assistant'):
        st.write("안녕하세요. AI 변호사입니다. 무엇을 도와드릴까요?")

# 입력창에 입력을 받아서 입력된 내용으로 메시지 생성
prompt = st.chat_input("AI 변호사에게 메시지 쓰기")
if prompt:
    message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=prompt
    )

    # 입력한 메시지 UI에 표시
    with st.chat_message(message.role):
        st.write(message.content[0].text.value)

    # run 돌리는 과정
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # run이 completed 되었나 0.1초마다 체크
    with st.spinner('응답 기다리는 중...'):
        while run.status != "completed":
            time.sleep(0.2)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

    # 메시지 불러오기 
    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )

    # 마지막 메시지 UI에 추가하기
    with st.chat_message(messages.data[0].role):
        st.write(messages.data[0].content[0].text.value)
