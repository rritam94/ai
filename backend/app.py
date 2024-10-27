from autogen import GroupChat, GroupChatManager
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from autogen.agentchat import AssistantAgent, UserProxyAgent
from flask import Flask
from flask_socketio import SocketIO, emit
import base64
import os

class CustomGroupChatManager(GroupChatManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def _process_received_message(self, message, sender, silent):
        socketio.emit('new_message', {'from': sender.name, 'text': 'From: ' + sender.name + '\n' + message})
        if sender.name == 'ritam':
            with open("damage.png", "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
            socketio.emit('image', {'data': encoded_image})

        if sender.name == 'arjun':
            with open("animal.png", "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
            socketio.emit('image', {'data': encoded_image})

        return super()._process_received_message(message, sender, silent)
    
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

config_list = [{"model": "gpt-4o-mini", "api_key": os.environ['OPENAI_API_KEY']}]

llm_config = {"config_list": config_list, "cache_seed": 42}

def is_termination_msg(message):
    return message["content"].strip().upper() == "TERMINATE"

#1
overview_agent = MultimodalConversableAgent(
    name="ritvik",
    system_message="This is the 1st thing to be done. Provide a high-level overview of the image. Generate a paragraph about this image that should go in an emergency response report. If this is the second time coming around, print the word 'TERMINATE'. Only output this portion.",
    llm_config=llm_config
)

#1
damage_agent = MultimodalConversableAgent(
    name="ritam",
    system_message="This is the 2nd thing to be done. Looking only at the hurricane damage assessment image, summarize in one paragraph the YOLO object detection image SPECIFICALLY in regards to the hurricane damage in the picture. Feel free to add your own analysis and things you've noticed. Don't mention wildlife. Only output this portion.",
    llm_config=llm_config
)

#1
wildlife_agent_1 = MultimodalConversableAgent(
    name="arjun",
    system_message="This is the 3rd thing to be done. Looking only at the animals found image, summarize the image in regards to the found wildlife in the picture. Feel free to add your own analysis in the context of a hurricane recently happening and things you've noticed. Include metrics like what type of animals were found, how many were found where they could have came from, how they got displaced, etc. Write a paragraph about this. Only output this portion.",
    llm_config=llm_config
)


#1
wildlife_agent_2 = MultimodalConversableAgent(
    name="jon",
    system_message="This is the 4th thing to be done. Given an image, provide textual output in paragraph form about where animals could be hiding post hurricane in the picture. Animals tend to move under safer spaces so predict where they've moved so we can rescue them. Only output this portion.",
    llm_config=llm_config
)

#1
recommendor_agent = AssistantAgent(
    name="sam",
    system_message="This is the 5th thing to be done. Given the textual input, generate a paragraph for recommendations for emergency personnel to conduct.",
    llm_config=llm_config
)

#2
introduction_agent = AssistantAgent(
    name="laith",
    system_message="This is the 6th thing to be done. Given the textual input, generate an introduction for a damage and wildlife report that summarizes the findings. Only output this portion.",
    llm_config=llm_config
)

#2
conclusion_agent = AssistantAgent(
    name="ayush",
    system_message="This is the 7th thing to be done. Given the textual input, generate a conclusion for a damage and wildlife report that summarizes the findings. Only output this portion.",
    llm_config=llm_config
)

#3
orchestrator_agent = AssistantAgent(
    name="ojas",
    system_message='''This is the last thing to be done. Given the input from the other agents, generate a **COMPLETE** report that assesses the hurricane damage and wildlife findings. Extend beyond what's given to you and put in your own thoughts as well. 
        Try to make sure the document is in this format:
        - Introduction from Laith
        - Drone Picture Evaluation From Ritvik
            - Initial Drone Picture
        - Damage Assessment from Ritam
            - YOLO Damage Detection Picture
        - Wildlife Assessment
            - Found Animals from Arjun
                - YOLO Found Animals Picture
            - Predicting Hidden Animals from Jon
        - Recommendations from Sam
        - Conclusion from Ayush
    
      You will have a variety of images to choose from in the following list: [initial_image.png, damage.png, animal.png]. Use initial_image.png after the high-level overview, use damage.png after the hurricane damage assessment section, and use animal.png after the wildlife section.

      After generating the report, the group chat manager shall send you back to Ojas (this agent) and respond with the word 'TERMINATE'
      ''',
    
    llm_config=llm_config
)

agents = [
    overview_agent,
    damage_agent,
    wildlife_agent_1,
    wildlife_agent_2,
    recommendor_agent,
    introduction_agent,
    conclusion_agent,
    orchestrator_agent
]

groupchat = GroupChat(
    agents=agents,
    messages=[],
    max_round=15
)

manager = CustomGroupChatManager(groupchat=groupchat, llm_config=llm_config, is_termination_msg=is_termination_msg)

user_proxy = UserProxyAgent(
    name="User",
    system_message="A human user who initiates the conversation and provides the image.",
    human_input_mode="NEVER",
    code_execution_config=False
)

@socketio.on('start_chat')
def handle_start_chat():
    user_proxy.initiate_chat(
        manager,
        message='''Please analyze the first image for hurricane damage and wildlife impact: <img initial_image.jpg>

        Use this image for damage assessment <img damage.png>

        Use this image for wildlife summarization: <img animal.png>
        '''
    )

    final_report = groupchat.messages[-2]['content']

    latex_gen = AssistantAgent(
        name="rocita",
        system_message="Please generate Python code to convert the inputted text to a PDF report with pylatex. Name the pdf hurricane.pdf. Also, whenever you see a png file include it by the name of the png file. If you use NoEscape, make sure you import it! Also, for me to know when to terminate include a variable finished = True at the end of your program.",
        llm_config=llm_config
    )

    message = {
        "role": "user",
        "content": final_report
    }

    response = latex_gen.generate_reply(messages=[message])
    socketio.emit('new_message', {'from': 'rocita', 'text': response})

    response = response[response.find('python') + 6: response.find('finished = True') + len('finished = True')]
    response.replace('image.show()', '')

    try:
        exec(response)

        try:
            with open('hurricane.pdf', 'rb') as file:
                pdf_data = file.read()
            
            import base64
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
            
            socketio.emit('pdf_file', {
                'filename': 'hurricane.pdf',
                'data': pdf_base64
            })

        except Exception as e:
            socketio.emit('error', {'message': str(e)})

    except Exception as e:
        error = str(e)
        print(error)

if __name__ == '__main__':
    socketio.run(app, debug=True)