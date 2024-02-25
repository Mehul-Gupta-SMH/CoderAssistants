import os.path

from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from autogen.code_utils import extract_code

from CoderAssistants.Code.Utlities import base_utils

@base_utils.log_function
def generate_team(topic:str,team_type="python_dev",max_conv_series=20):

    print("Generating Team : ",team_type)

    config_list = [ {'model': base_utils.get_config_val(config_type="model_config",key_list=["OPEN_AI","model_name"]),
                     'api_key': base_utils.get_config_val(config_type="model_config",key_list=["OPEN_AI","api_key"])} ]


    team_members = base_utils.get_config_val(config_type=team_type,get_all=True,key_list = ["team_members"])
    team_manager = base_utils.get_config_val(config_type=team_type,get_all=True,key_list = ["manager","technical_manager"])

    member_agents = {}
    disallowed_speaker_transitions = {}

    for members in team_members:
        print("members :",members)
        member_agents[members] = AssistantAgent(name=members
                                                , system_message=team_members[members]['persona']
                                                , llm_config={"config_list": config_list}
                                                , description = team_members[members]['description']
                                                )

    for members in team_members:
        print("members that can't communicate :",team_members[members]['members_exclude_communication'])
        disallowed_speaker_transitions[member_agents[members]] = [
            member_agents[excluded_members]
            for excluded_members in team_members[members]['members_exclude_communication']
        ]


    groupchat = GroupChat(agents=list(member_agents.values())
                          , messages=[]
                          , max_round=max_conv_series
                          , allowed_or_disallowed_speaker_transitions = disallowed_speaker_transitions
                          , speaker_transitions_type = "disallowed"
                          ,speaker_selection_method='auto')

    team_manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list},
                                    system_message=team_manager["persona"])

    user_proxy = UserProxyAgent( "user_proxy",
                                 code_execution_config={"work_dir": "Code", "use_docker": False}
                                 )

    user_proxy.initiate_chat(team_manager,message=topic)

    ConvLog = f"{team_type}_ResultsConvLog"

    if not os.path.exists(
            os.path.join(
                os.getcwd(),ConvLog
            )
    ):
        os.mkdir(os.path.join(
            os.getcwd(),ConvLog
        ))

    with open(os.path.join(ConvLog,topic[:25].replace(".","_")+".ConvLog"),"w+") as ConvResults:
        full_message = ""
        for message in groupchat.messages:
            message =  message['role'] + " ---> "+ message['name'] + "\n\n" +  message['content'] + "\n\n################\n\n"
            full_message += message
        ConvResults.write(full_message)

    codes_extracted = []

    for messages in groupchat.messages:
        try:
            codes_extracteda.append(
                (
                    messages['content'].strip(),
                    extract(messages['content'].strip())
                )
            )
        except:
            continue

    return codes_extracted

